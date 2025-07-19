# Task Integration with Dependency Injection

This guide explains how to integrate your existing `SendEmail` task and other Taskiq tasks with the Dishka DI system.

## Overview

Your original `SendEmail` task has been successfully integrated with the DI system while maintaining **100% backward compatibility**. You now have multiple ways to work with tasks:

1. **Original approach** - Works exactly as before
2. **DI-enhanced approach** - Gets dependencies injected automatically
3. **Hybrid approach** - Mix both as needed

## Your Original Task (Unchanged)

Your original task in `app/core/services/mail/aiosmtplib/task.py` still works exactly as before:

```python
from email.message import EmailMessage
import aiosmtplib
from app.core.configs.app import app_config
from app.core.services.queue.depends import get_queued_decorator
from app.core.services.queue.task import BaseTask
from app.core.services.mail.aiosmtplib.init import smtp_config

queued = get_queued_decorator()

@queued
class SendEmail(BaseTask):
    __task_name__ = 'mail.send'

    async def run(self, content: str, email_data: dict) -> None:
        sender_name = email_data.get('sender_name') or app_config.EMAIL_SENDER_NAME
        sender_address = email_data.get('sender_address') or app_config.EMAIL_SENDER_ADDRESS

        message = EmailMessage()
        message['From'] = f'{sender_name} <{sender_address}>'
        message['To'] = email_data['recipient']
        message['Subject'] = f'{app_config.PROJECT_NAME} | {email_data["subject"]}'
        message.add_alternative(content, subtype='html')

        await aiosmtplib.send(message, **smtp_config)
```

**This continues to work exactly as it did before!**

## DI-Enhanced Version

A new DI-aware version is available in `app/core/services/mail/aiosmtplib/task_di.py`:

```python
class SendEmailTask(BaseTask):
    """DI-aware SendEmail task that receives configuration via dependency injection."""
    __task_name__ = 'mail.send'

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config

    async def run(self, content: str, email_data: dict) -> None:
        # Uses injected config or falls back to global config
        config = self.config or self._get_global_config()
        
        sender_name = email_data.get('sender_name') or config.EMAIL_SENDER_NAME
        sender_address = email_data.get('sender_address') or config.EMAIL_SENDER_ADDRESS
        # ... rest of the logic
```

## Integration Methods

### Method 1: Automatic Registration (Recommended)

The DI system automatically registers both versions during startup:

```python
# In app/core/di/initialize.py
def register_tasks_with_di(container) -> None:
    """Register all background tasks with DI integration."""
    from app.core.di.tasks import DIAwareTaskiqDecorator
    from app.core.services.mail.aiosmtplib.task_di import SendEmailTask
    
    with container() as app_scope:
        broker = app_scope.get(AsyncBroker)
        di_decorator = DIAwareTaskiqDecorator(broker, container)
        di_decorator(SendEmailTask)  # Registers DI-aware version
```

### Method 2: Manual Registration

You can manually register tasks with DI:

```python
from app.core.di import get_container
from app.core.di.tasks import DIAwareTaskiqDecorator

def register_custom_task():
    container = get_container()
    
    with container() as app_scope:
        broker = app_scope.get(AsyncBroker)
        di_decorator = DIAwareTaskiqDecorator(broker, container)
        di_decorator(YourCustomTask)
```

## Usage Examples

### Using Your Original Task

```python
# This continues to work exactly as before
from app.core.services.queue.service import QueueServiceInterface

async def send_email_original_way(queue_service: QueueServiceInterface):
    from app.core.services.mail.aiosmtplib.task import SendEmail
    
    email_data = {
        'recipient': 'user@example.com',
        'subject': 'Test Email',
        'sender_name': None,  # Uses app_config
        'sender_address': None,  # Uses app_config
    }
    
    task_id = await queue_service.push(SendEmail, {
        'content': '<h1>Hello!</h1>',
        'email_data': email_data
    })
```

### Using DI-Enhanced Task

```python
# New DI-aware approach
async def send_email_di_way(queue_service: QueueServiceInterface):
    from app.core.services.mail.aiosmtplib.task_di import SendEmailTask
    
    email_data = {
        'recipient': 'user@example.com',
        'subject': 'Test Email with DI',
        'sender_name': None,  # Uses injected config
        'sender_address': None,  # Uses injected config
    }
    
    # Task automatically gets DI dependencies
    task_id = await queue_service.push(SendEmailTask, {
        'content': '<h1>Hello from DI!</h1>',
        'email_data': email_data
    })
```

### FastAPI Endpoint Example

```python
from fastapi import FastAPI
from app.core.di import inject
from app.core.services.queue.service import QueueServiceInterface

app = FastAPI()

@app.post("/send-email")
async def send_email(
    recipient: str,
    subject: str,
    content: str,
    queue_service: QueueServiceInterface = inject(QueueServiceInterface),
):
    """Send email using DI-enhanced task."""
    from app.core.services.mail.aiosmtplib.task_di import SendEmailTask
    
    task_id = await queue_service.push(SendEmailTask, {
        'content': content,
        'email_data': {
            'recipient': recipient,
            'subject': subject,
        }
    })
    
    return {"task_id": task_id, "status": "queued"}
```

## Creating New DI-Aware Tasks

Here's how to create new tasks that use DI:

```python
from app.core.services.queue.task import BaseTask
from app.core.configs.app import AppConfig
from app.core.services.mail.service import MailServiceInterface

class UserWelcomeTask(BaseTask):
    """Task that uses multiple DI services."""
    __task_name__ = 'user.welcome'
    
    def __init__(self, config: AppConfig = None, mail_service: MailServiceInterface = None):
        self.config = config
        self.mail_service = mail_service
    
    async def run(self, user_id: int, user_email: str) -> None:
        # Use injected services
        config = self.config or self._get_global_config()
        mail_service = self.mail_service or self._get_global_mail_service()
        
        welcome_message = f"Welcome to {config.PROJECT_NAME}!"
        
        await mail_service.send_plain(
            subject="Welcome!",
            recipient=user_email,
            body=welcome_message
        )
    
    def _get_global_config(self):
        from app.core.configs.app import app_config
        return app_config
    
    def _get_global_mail_service(self):
        # Fallback implementation
        pass

# Register with DI
def register_welcome_task():
    from app.core.di import get_container
    from app.core.di.tasks import DIAwareTaskiqDecorator
    
    container = get_container()
    with container() as app_scope:
        broker = app_scope.get(AsyncBroker)
        di_decorator = DIAwareTaskiqDecorator(broker, container)
        di_decorator(UserWelcomeTask)
```

## Benefits of DI Integration

### ✅ **Backward Compatibility**
- Your original `SendEmail` task works unchanged
- No breaking changes to existing code
- Can mix old and new approaches

### ✅ **Dependency Injection**
- Tasks automatically receive configured dependencies
- No more global imports in tasks
- Easy to test with mocked dependencies

### ✅ **Type Safety**
- Full type hints for injected dependencies
- IDE autocompletion and error detection
- Compile-time dependency validation

### ✅ **Flexibility**
- Use original approach for simple tasks
- Use DI approach for complex tasks
- Mix both approaches as needed

### ✅ **Testability**
- Easy to mock dependencies for testing
- Isolated task testing
- No global state dependencies

## Migration Strategy

### Phase 1: Keep Original (Current)
```python
# Your existing code continues to work
@queued
class SendEmail(BaseTask):
    # ... existing implementation
```

### Phase 2: Add DI Support (Optional)
```python
# Add DI-aware version alongside original
class SendEmailTask(BaseTask):
    def __init__(self, config: AppConfig = None):
        self.config = config
    # ... DI-aware implementation
```

### Phase 3: Use DI Where Beneficial
```python
# Use DI for new tasks or where testing is important
# Keep original for simple, stable tasks
```

## Task Registration Summary

The DI system automatically handles:

1. **Original Tasks**: Registered via `@queued` decorator
2. **DI Tasks**: Registered via `DIAwareTaskiqDecorator` 
3. **Dependencies**: Automatically injected when tasks run
4. **Fallbacks**: DI tasks fall back to global config if DI unavailable

## Best Practices

1. **Start Simple**: Keep using your original task for existing functionality
2. **Add DI Gradually**: Use DI for new tasks or when testing is important
3. **Provide Fallbacks**: Always provide fallback implementations in DI tasks
4. **Test Both**: Test both original and DI versions of critical tasks
5. **Document Dependencies**: Clearly document what dependencies tasks expect

This integration provides the best of both worlds: your existing code continues to work unchanged, while new code can benefit from dependency injection capabilities.