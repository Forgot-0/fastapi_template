"""
Example showing how to use tasks with DI integration.

This demonstrates different ways to work with background tasks:
1. Using your original task approach (backward compatibility)
2. Using DI-aware tasks with dependency injection
3. Creating new tasks that use DI
"""

from app.core.di import get_container
from app.core.services.queue.service import QueueServiceInterface


# Example 1: Using your original task approach (still works)
def example_original_task_usage():
    """Example using your original SendEmail task approach."""
    from app.core.services.mail.aiosmtplib.task_di import create_legacy_send_email_task
    
    # This creates and registers your original task exactly as before
    SendEmail = create_legacy_send_email_task()
    
    # Usage remains the same
    email_data = {
        'recipient': 'user@example.com',
        'subject': 'Test Email',
        'sender_name': None,  # Will use config default
        'sender_address': None,  # Will use config default
    }
    
    # This would queue the task as before
    # await queue_service.push(SendEmail, {
    #     'content': '<h1>Hello!</h1>',
    #     'email_data': email_data
    # })


# Example 2: Using DI-aware tasks
async def example_di_task_usage():
    """Example using DI-aware tasks."""
    container = get_container()
    
    with container() as request_scope:
        queue_service = request_scope.get(QueueServiceInterface)
        
        # Import the DI-aware task
        from app.core.services.mail.aiosmtplib.task_di import SendEmailTask
        
        # Queue the task - it will automatically receive DI dependencies
        email_data = {
            'recipient': 'user@example.com',
            'subject': 'Test Email with DI',
            'sender_name': None,  # Will use injected config
            'sender_address': None,  # Will use injected config
        }
        
        task_id = await queue_service.push(SendEmailTask, {
            'content': '<h1>Hello from DI task!</h1>',
            'email_data': email_data
        })
        
        print(f"Queued DI task with ID: {task_id}")
        return task_id


# Example 3: Creating a new DI-aware task
from app.core.services.queue.task import BaseTask
from app.core.configs.app import AppConfig
from app.core.services.mail.service import MailServiceInterface


class UserNotificationTask(BaseTask):
    """Example of a new task that uses DI for multiple services."""
    __task_name__ = 'user.notification'
    
    def __init__(self, config: AppConfig = None, mail_service: MailServiceInterface = None):
        self.config = config
        self.mail_service = mail_service
    
    async def run(self, user_id: int, notification_type: str, message: str) -> None:
        """Send user notification via email."""
        # Use injected services or fall back to global imports
        config = self.config or self._get_global_config()
        mail_service = self.mail_service or self._get_global_mail_service()
        
        # Business logic using injected dependencies
        subject = f"{config.PROJECT_NAME} - {notification_type}"
        
        await mail_service.send_plain(
            subject=subject,
            recipient=f"user_{user_id}@example.com",  # In real app, get from user service
            body=message
        )
        
        print(f"Sent {notification_type} notification to user {user_id}")
    
    def _get_global_config(self):
        from app.core.configs.app import app_config
        return app_config
    
    def _get_global_mail_service(self):
        # Fallback for non-DI usage
        from app.core.services.queue.depends import get_queue_service
        from app.core.services.mail.aiosmtplib.service import AioSmtpLibMailService
        return AioSmtpLibMailService(queue_service=get_queue_service())


# Example 4: Registering the new task with DI
def register_user_notification_task():
    """Register the UserNotificationTask with DI."""
    from app.core.di.tasks import DIAwareTaskiqDecorator
    from taskiq import AsyncBroker
    
    container = get_container()
    
    with container() as app_scope:
        broker = app_scope.get(AsyncBroker)
        
        # Create DI-aware decorator
        di_decorator = DIAwareTaskiqDecorator(broker, container)
        
        # Register the task
        di_decorator(UserNotificationTask)
        
        print("Registered UserNotificationTask with DI")


# Example 5: Using the new task
async def example_custom_task_usage():
    """Example using the custom UserNotificationTask."""
    container = get_container()
    
    with container() as request_scope:
        queue_service = request_scope.get(QueueServiceInterface)
        
        # Queue the custom task
        task_id = await queue_service.push(UserNotificationTask, {
            'user_id': 123,
            'notification_type': 'Welcome',
            'message': 'Welcome to our platform!'
        })
        
        print(f"Queued UserNotificationTask with ID: {task_id}")
        return task_id


# Example 6: FastAPI endpoint using DI tasks
from fastapi import FastAPI
from app.core.di import inject

app = FastAPI()

@app.post("/send-notification")
async def send_notification(
    user_id: int,
    message: str,
    queue_service: QueueServiceInterface = inject(QueueServiceInterface),
):
    """FastAPI endpoint that queues a task using DI."""
    
    # Queue the task with DI-injected dependencies
    task_id = await queue_service.push(UserNotificationTask, {
        'user_id': user_id,
        'notification_type': 'Manual',
        'message': message
    })
    
    return {"task_id": task_id, "status": "queued"}


if __name__ == "__main__":
    # Register the custom task
    register_user_notification_task()
    
    # Examples would be run in an async context
    import asyncio
    
    async def run_examples():
        await example_di_task_usage()
        await example_custom_task_usage()
    
    asyncio.run(run_examples())