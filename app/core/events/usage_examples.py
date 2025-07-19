"""
EventBus DI Integration Examples

This module demonstrates different ways to use the EventBus with dependency injection,
including various patterns and use cases.
"""

from typing import List
from fastapi import FastAPI
from app.core.di import inject, get_container
from app.core.events.service import BaseEventBus, RequestScopedEventBus, DIEventBus
from app.core.events.registration import DIEventRegistration
from app.core.events.event import EventHandlerRegistry


# Example 1: Basic EventBus usage with DI
async def example_basic_event_publishing():
    """Example of basic event publishing with DI-resolved handlers."""
    from app.auth.events.users.created import CreatedUserEvent
    
    container = get_container()
    
    with container() as request_scope:
        event_bus = request_scope.get(BaseEventBus)
        
        # Create and publish an event
        event = CreatedUserEvent(user_id=123, email="user@example.com")
        
        # Publish the event - handlers will be resolved from DI with dependencies
        results = await event_bus.publish([event])
        
        print(f"Event published, {len(results)} handlers processed")
        return results


# Example 2: FastAPI endpoint that publishes events
app = FastAPI()

@app.post("/users/register")
async def register_user(
    user_data: dict,
    event_bus: BaseEventBus = inject(BaseEventBus),
):
    """FastAPI endpoint that publishes events after user registration."""
    # Simulate user registration logic
    user_id = 123
    email = user_data["email"]
    
    # Create event
    from app.auth.events.users.created import CreatedUserEvent
    event = CreatedUserEvent(user_id=user_id, email=email)
    
    # Publish event - handlers get dependencies injected automatically
    results = await event_bus.publish([event])
    
    return {
        "user_id": user_id,
        "email": email,
        "events_processed": len(results)
    }


# Example 3: Publishing multiple events
async def example_multiple_events():
    """Example of publishing multiple events at once."""
    from app.auth.events.users.created import CreatedUserEvent
    from app.auth.events.users.verified import VerifiedUserEvent
    
    container = get_container()
    
    with container() as request_scope:
        event_bus = request_scope.get(BaseEventBus)
        
        # Create multiple events
        events = [
            CreatedUserEvent(user_id=123, email="user1@example.com"),
            CreatedUserEvent(user_id=124, email="user2@example.com"),
            VerifiedUserEvent(user_id=123, email="user1@example.com"),
        ]
        
        # Publish all events
        results = await event_bus.publish(events)
        
        print(f"Published {len(events)} events, {len(results)} handlers processed")
        return results


# Example 4: Custom event with DI-aware handler
from app.core.events.event import BaseEvent, BaseEventHandler
from app.core.configs.app import AppConfig
from app.core.services.mail.service import MailServiceInterface
from dataclasses import dataclass

@dataclass(frozen=True)
class OrderCreatedEvent(BaseEvent):
    order_id: int
    customer_email: str
    total_amount: float
    
    __event_name__: str = "order_created"

@dataclass(frozen=True)
class OrderNotificationHandler(BaseEventHandler[OrderCreatedEvent, None]):
    config: AppConfig
    mail_service: MailServiceInterface
    
    async def handle(self, event: OrderCreatedEvent) -> None:
        """Handle order created event with DI dependencies."""
        subject = f"{self.config.PROJECT_NAME} - Order Confirmation"
        
        message = f"""
        Thank you for your order!
        
        Order ID: {event.order_id}
        Total: ${event.total_amount:.2f}
        
        We'll send you updates about your order.
        """
        
        await self.mail_service.send_plain(
            subject=subject,
            recipient=event.customer_email,
            body=message
        )
        
        print(f"Order notification sent for order {event.order_id}")


# Example 5: Registering custom events with DI
def register_custom_events():
    """Example of registering custom events with DI."""
    container = get_container()
    
    with container() as app_scope:
        event_registry = app_scope.get(EventHandlerRegistry)
        
        # Create DI registration
        registration = DIEventRegistration(event_registry, container)
        
        # Register custom event with DI handler
        registration.register_handler(
            event_type=OrderCreatedEvent,
            handler_type=OrderNotificationHandler,
            use_di=True
        )
        
        print("Custom events registered with DI")
        return registration


# Example 6: Using different EventBus implementations
async def example_different_eventbus_types():
    """Example showing different EventBus implementations."""
    container = get_container()
    
    # Method 1: Using RequestScopedEventBus (recommended)
    with container() as request_scope:
        request_scoped_bus = request_scope.get(RequestScopedEventBus)
        event = OrderCreatedEvent(order_id=1, customer_email="test@example.com", total_amount=99.99)
        await request_scoped_bus.publish([event])
    
    # Method 2: Using DIEventBus with manual container passing
    with container() as app_scope:
        event_registry = app_scope.get(EventHandlerRegistry)
        di_bus = DIEventBus(event_registry, container)
        await di_bus.publish([event])
    
    # Method 3: Using the default BaseEventBus (which is RequestScopedEventBus)
    with container() as request_scope:
        default_bus = request_scope.get(BaseEventBus)
        await default_bus.publish([event])


# Example 7: Command handler that publishes events
from app.core.commands import BaseCommand, BaseCommandHandler
from sqlalchemy.ext.asyncio import AsyncSession

@dataclass(frozen=True)
class CreateOrderCommand(BaseCommand):
    customer_email: str
    items: List[dict]
    total_amount: float

@dataclass(frozen=True)
class CreateOrderCommandHandler(BaseCommandHandler[CreateOrderCommand, int]):
    session: AsyncSession
    event_bus: BaseEventBus
    
    async def handle(self, command: CreateOrderCommand) -> int:
        """Create order and publish event."""
        # Simulate order creation
        order_id = 12345
        
        # Save to database
        # ... database logic here ...
        await self.session.commit()
        
        # Publish event
        event = OrderCreatedEvent(
            order_id=order_id,
            customer_email=command.customer_email,
            total_amount=command.total_amount
        )
        
        await self.event_bus.publish([event])
        
        print(f"Order {order_id} created and event published")
        return order_id


# Example 8: Testing events with DI
async def test_event_handling():
    """Example of testing event handling with DI."""
    from unittest.mock import Mock
    
    # Create mock dependencies
    mock_config = Mock(spec=AppConfig)
    mock_config.PROJECT_NAME = "Test Project"
    
    mock_mail_service = Mock(spec=MailServiceInterface)
    
    # Create handler with mocked dependencies
    handler = OrderNotificationHandler(
        config=mock_config,
        mail_service=mock_mail_service
    )
    
    # Create and handle event
    event = OrderCreatedEvent(
        order_id=123,
        customer_email="test@example.com",
        total_amount=99.99
    )
    
    await handler.handle(event)
    
    # Verify mock was called
    mock_mail_service.send_plain.assert_called_once()
    call_args = mock_mail_service.send_plain.call_args
    assert "Test Project" in call_args.kwargs["subject"]
    assert call_args.kwargs["recipient"] == "test@example.com"


# Example 9: Event-driven saga pattern
async def example_order_saga():
    """Example of event-driven saga using multiple events."""
    container = get_container()
    
    with container() as request_scope:
        event_bus = request_scope.get(BaseEventBus)
        
        # Step 1: Order created
        order_event = OrderCreatedEvent(
            order_id=123,
            customer_email="customer@example.com",
            total_amount=199.99
        )
        
        await event_bus.publish([order_event])
        
        # Step 2: Payment processed (would be triggered by payment service)
        # Step 3: Inventory reserved (would be triggered by inventory service)
        # Step 4: Shipping scheduled (would be triggered by shipping service)
        
        print("Order saga initiated")


# Example 10: Conditional event handling
class ConditionalEventHandler(BaseEventHandler[OrderCreatedEvent, None]):
    """Handler that processes events conditionally."""
    
    def __init__(self, config: AppConfig, mail_service: MailServiceInterface):
        self.config = config
        self.mail_service = mail_service
    
    async def handle(self, event: OrderCreatedEvent) -> None:
        """Handle event only for high-value orders."""
        if event.total_amount > 100.00:
            # Send special notification for high-value orders
            subject = f"{self.config.PROJECT_NAME} - VIP Order Confirmation"
            
            message = f"""
            Thank you for your VIP order!
            
            Order ID: {event.order_id}
            Total: ${event.total_amount:.2f}
            
            You'll receive priority processing and free shipping!
            """
            
            await self.mail_service.send_plain(
                subject=subject,
                recipient=event.customer_email,
                body=message
            )
            
            print(f"VIP notification sent for order {event.order_id}")


if __name__ == "__main__":
    import asyncio
    
    async def run_examples():
        # Register custom events first
        register_custom_events()
        
        # Run examples
        await example_basic_event_publishing()
        await example_multiple_events()
        await example_different_eventbus_types()
        await test_event_handling()
        await example_order_saga()
    
    asyncio.run(run_examples())