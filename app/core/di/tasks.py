from typing import Any, Dict, Type
from dishka import Provider, Scope, provide, Container
from taskiq import AsyncBroker

from app.core.configs.app import AppConfig
from app.core.services.queue.taskiq.decorator import TaskiqQueuedDecorator
from app.core.services.queue.task import BaseTask


class DITaskWrapper:
    """Wrapper that injects dependencies into tasks."""
    
    def __init__(self, task_class: Type[BaseTask], container: Container):
        self.task_class = task_class
        self.container = container
        self.__task_name__ = task_class.__task_name__
    
    def get_name(self) -> str:
        return self.task_class.get_name()
    
    async def run(self, *args, **kwargs) -> Any:
        """Run the task with injected dependencies."""
        with self.container() as request_scope:
            # Get dependencies that the task might need
            config = request_scope.get(AppConfig)
            
            # Create task instance with dependencies
            if hasattr(self.task_class, '__init__') and self.task_class.__init__.__code__.co_argcount > 1:
                # Task expects dependencies in constructor
                task_instance = self.task_class(config=config)
            else:
                # Task uses default constructor
                task_instance = self.task_class()
                # Inject dependencies as attributes
                task_instance.config = config
            
            return await task_instance.run(*args, **kwargs)


class TaskProvider(Provider):
    scope = Scope.APP

    @provide
    def queued_decorator(self, broker: AsyncBroker, container: Container) -> 'DIAwareTaskiqDecorator':
        """Provide a DI-aware queued decorator."""
        return DIAwareTaskiqDecorator(broker, container)


class DIAwareTaskiqDecorator:
    """Enhanced decorator that wraps tasks with DI capabilities."""
    
    def __init__(self, broker: AsyncBroker, container: Container):
        self.broker = broker
        self.container = container
    
    def __call__(self, cls: Type[BaseTask]) -> Type[BaseTask]:
        # Create DI wrapper
        wrapper = DITaskWrapper(cls, self.container)
        
        # Register the wrapper with the broker
        self.broker.register_task(func=wrapper.run, task_name=cls.get_name())
        
        return cls


# Enhanced version of your SendEmail task that works with DI
class SendEmailTask(BaseTask):
    """DI-aware SendEmail task."""
    __task_name__ = 'mail.send'
    
    def __init__(self, config: AppConfig = None):
        self.config = config
    
    async def run(self, content: str, email_data: dict) -> None:
        from app.core.services.mail.aiosmtplib.init import smtp_config
        from email.message import EmailMessage
        import aiosmtplib
        
        # Use injected config or fall back to global config
        config = self.config or self._get_global_config()
        
        sender_name = email_data.get('sender_name') or config.EMAIL_SENDER_NAME
        sender_address = email_data.get('sender_address') or config.EMAIL_SENDER_ADDRESS

        message = EmailMessage()
        message['From'] = f'{sender_name} <{sender_address}>'
        message['To'] = email_data['recipient']
        message['Subject'] = f'{config.PROJECT_NAME} | {email_data["subject"]}'
        message.add_alternative(content, subtype='html')

        await aiosmtplib.send(message, **smtp_config)
    
    def _get_global_config(self):
        """Fallback to global config if DI is not available."""
        from app.core.configs.app import app_config
        return app_config


def register_tasks_with_di(container: Container) -> None:
    """Register all tasks with DI integration."""
    with container() as app_scope:
        broker = app_scope.get(AsyncBroker)
        decorator = DIAwareTaskiqDecorator(broker, container)
        
        # Register your enhanced SendEmail task
        decorator(SendEmailTask)


# Function to get DI-aware decorator
def get_di_queued_decorator(container: Container) -> DIAwareTaskiqDecorator:
    """Get a DI-aware queued decorator."""
    with container() as app_scope:
        broker = app_scope.get(AsyncBroker)
        return DIAwareTaskiqDecorator(broker, container)