# EventBus Dependency Injection Integration

This document explains the comprehensive EventBus system with dependency injection integration, addressing the challenges of event handling in a DI-managed application.

## Problems Solved

### 🔍 **Original Issues**
1. **Handler Resolution**: EventBus only worked with pre-instantiated handlers
2. **Dependency Injection**: Event handlers couldn't receive injected dependencies
3. **Scope Management**: App-scoped EventBus vs request-scoped handlers
4. **Container Access**: EventBus had no access to DI container for resolution

### ✅ **Solutions Provided**
1. **Multiple EventBus Implementations**: Different strategies for different use cases
2. **DI-Aware Handlers**: Handlers automatically receive dependencies
3. **Request Scope Management**: Proper scoping for event handling
4. **Enhanced Registration**: Better registration system with DI support

## EventBus Implementations

### 1. **EventBus** (Simple)
```python
@dataclass(eq=False)
class EventBus(BaseEventBus):
    """Simple EventBus that works with pre-instantiated handlers."""
```

**Use Case**: When you have pre-instantiated handlers
**Pros**: Simple, fast, no DI complexity
**Cons**: Limited flexibility, no dependency injection

### 2. **DIEventBus** (DI-Aware)
```python
@dataclass(eq=False)
class DIEventBus(BaseEventBus):
    """DI-aware EventBus that resolves handlers from the container."""
```

**Use Case**: When you need DI but want control over container scoping
**Pros**: Full DI support, flexible container management
**Cons**: Requires manual container management

### 3. **RequestScopedEventBus** (Recommended)
```python
@dataclass(eq=False) 
class RequestScopedEventBus(BaseEventBus):
    """EventBus that creates a new request scope for each publish operation."""
```

**Use Case**: Most common scenario - automatic request scoping
**Pros**: Automatic scope management, full DI support, easy to use
**Cons**: Slight overhead for scope creation

## DI Provider Configuration

```python
class EventProvider(Provider):
    scope = Scope.APP

    @provide
    def event_handler_registry(self) -> EventHandlerRegistry:
        return EventHandlerRegistry()

    @provide
    def request_scoped_event_bus(self, event_registry: EventHandlerRegistry, container: Container) -> RequestScopedEventBus:
        return RequestScopedEventBus(event_registry=event_registry, container=container)

    @provide
    def event_bus(self, request_scoped_event_bus: RequestScopedEventBus) -> BaseEventBus:
        """Default EventBus implementation (request-scoped)."""
        return request_scoped_event_bus
```

## Event Handler Registration

### Enhanced Registration System

```python
from app.core.events.registration import DIEventRegistration

# Create registration with DI support
registration = DIEventRegistration(event_registry, container)

# Register handler with DI
registration.register_handler(
    event_type=UserCreatedEvent,
    handler_type=UserCreatedEventHandler,
    use_di=True
)

# Register multiple handlers for one event
registration.register_multiple_handlers(
    event_type=OrderCreatedEvent,
    handler_types=[EmailNotificationHandler, InventoryHandler, PaymentHandler],
    use_di=True
)
```

### Automatic Registration

```python
def register_auth_events_with_di(registration: DIEventRegistration) -> None:
    """Register auth module events with DI."""
    registration.register_handler(CreatedUserEvent, CreatedUserEventHandler, use_di=True)
    registration.register_handler(VerifiedUserEvent, VerifiedUserEventHandler, use_di=True)
    registration.register_handler(PasswordResetEvent, PasswordResetEventHandler, use_di=True)
```

## Usage Patterns

### 1. **Basic Event Publishing**
```python
async def publish_user_event():
    container = get_container()
    
    with container() as request_scope:
        event_bus = request_scope.get(BaseEventBus)
        
        event = CreatedUserEvent(user_id=123, email="user@example.com")
        results = await event_bus.publish([event])
```

### 2. **FastAPI Integration**
```python
@app.post("/users/register")
async def register_user(
    user_data: dict,
    event_bus: BaseEventBus = inject(BaseEventBus),
):
    # Create user...
    
    event = CreatedUserEvent(user_id=user_id, email=user_data["email"])
    await event_bus.publish([event])
    
    return {"user_id": user_id}
```

### 3. **Command Handler Integration**
```python
@dataclass(frozen=True)
class CreateOrderCommandHandler(BaseCommandHandler[CreateOrderCommand, int]):
    session: AsyncSession
    event_bus: BaseEventBus  # EventBus injected as dependency
    
    async def handle(self, command: CreateOrderCommand) -> int:
        # Create order...
        await self.session.commit()
        
        # Publish event
        event = OrderCreatedEvent(order_id=order_id, customer_email=command.customer_email)
        await self.event_bus.publish([event])
        
        return order_id
```

## Event Handler Examples

### DI-Aware Event Handler
```python
@dataclass(frozen=True)
class CreatedUserEventHandler(BaseEventHandler[CreatedUserEvent, None]):
    mail_service: MailServiceInterface  # Injected dependency
    queue_service: QueueServiceInterface  # Injected dependency
    
    async def handle(self, event: CreatedUserEvent) -> None:
        # Use injected services
        await self.mail_service.send_plain(
            subject="Welcome!",
            recipient=event.email,
            body="Welcome to our platform!"
        )
```

### Multi-Service Event Handler
```python
@dataclass(frozen=True)
class OrderNotificationHandler(BaseEventHandler[OrderCreatedEvent, None]):
    config: AppConfig
    mail_service: MailServiceInterface
    sms_service: SMSServiceInterface
    analytics_service: AnalyticsServiceInterface
    
    async def handle(self, event: OrderCreatedEvent) -> None:
        # Send email notification
        await self.mail_service.send_plain(...)
        
        # Send SMS for high-value orders
        if event.total_amount > 100:
            await self.sms_service.send(...)
        
        # Track analytics
        await self.analytics_service.track_event("order_created", event.order_id)
```

## Testing with DI

### Unit Testing
```python
async def test_event_handler():
    # Create mock dependencies
    mock_mail_service = Mock(spec=MailServiceInterface)
    mock_config = Mock(spec=AppConfig)
    mock_config.PROJECT_NAME = "Test Project"
    
    # Create handler with mocked dependencies
    handler = OrderNotificationHandler(
        config=mock_config,
        mail_service=mock_mail_service
    )
    
    # Test event handling
    event = OrderCreatedEvent(order_id=123, customer_email="test@example.com", total_amount=99.99)
    await handler.handle(event)
    
    # Verify interactions
    mock_mail_service.send_plain.assert_called_once()
```

### Integration Testing
```python
async def test_eventbus_integration():
    # Create test container with real implementations
    test_container = create_test_container()
    
    with test_container() as request_scope:
        event_bus = request_scope.get(BaseEventBus)
        
        event = CreatedUserEvent(user_id=123, email="test@example.com")
        results = await event_bus.publish([event])
        
        assert len(results) > 0
```

## Advanced Patterns

### 1. **Event Saga Pattern**
```python
async def process_order_saga(order_id: int):
    """Event-driven saga for order processing."""
    container = get_container()
    
    with container() as request_scope:
        event_bus = request_scope.get(BaseEventBus)
        
        # Each step publishes events that trigger the next step
        await event_bus.publish([OrderCreatedEvent(...)])
        # -> Triggers PaymentProcessingEvent
        # -> Triggers InventoryReservationEvent  
        # -> Triggers ShippingScheduledEvent
```

### 2. **Conditional Event Handling**
```python
class ConditionalEventHandler(BaseEventHandler[OrderCreatedEvent, None]):
    async def handle(self, event: OrderCreatedEvent) -> None:
        if event.total_amount > 1000:
            # Special handling for high-value orders
            await self.vip_notification_service.notify(event)
        else:
            # Standard handling
            await self.standard_notification_service.notify(event)
```

### 3. **Event Aggregation**
```python
class EventAggregator(BaseEventHandler[BaseEvent, None]):
    """Aggregates multiple events for batch processing."""
    
    def __init__(self):
        self.event_buffer = []
        self.buffer_size = 10
    
    async def handle(self, event: BaseEvent) -> None:
        self.event_buffer.append(event)
        
        if len(self.event_buffer) >= self.buffer_size:
            await self.process_batch(self.event_buffer)
            self.event_buffer.clear()
```

## Performance Considerations

### 1. **Request Scope Efficiency**
- `RequestScopedEventBus` creates one request scope per publish operation
- All handlers for that operation share the same scope
- Efficient for most use cases

### 2. **Error Handling**
- Individual handler failures don't stop other handlers
- Comprehensive error logging
- Graceful degradation

### 3. **Memory Management**
- Event handlers are created per request and disposed
- No memory leaks from long-lived handler instances
- Proper cleanup of resources

## Migration Strategy

### Phase 1: Use Simple EventBus
```python
# Start with simple approach
event_bus = EventBus(event_registry)
```

### Phase 2: Add DI for New Handlers
```python
# Register new handlers with DI
registration.register_handler(NewEvent, NewEventHandler, use_di=True)
```

### Phase 3: Migrate to RequestScopedEventBus
```python
# Switch to full DI integration
event_bus = RequestScopedEventBus(event_registry, container)
```

## Best Practices

### ✅ **Do**
- Use `RequestScopedEventBus` for most scenarios
- Design handlers to be stateless
- Use dependency injection for all handler dependencies
- Implement proper error handling in handlers
- Test handlers with mocked dependencies

### ❌ **Don't**
- Store state in event handlers
- Create circular dependencies between events
- Ignore handler failures silently
- Mix DI and non-DI handlers unnecessarily
- Create overly complex event hierarchies

## Summary

The enhanced EventBus system provides:

- **Multiple Implementation Options**: Choose the right EventBus for your use case
- **Full DI Integration**: Handlers receive dependencies automatically
- **Proper Scope Management**: Request-scoped handlers with app-scoped EventBus
- **Enhanced Registration**: Flexible registration system with DI support
- **Comprehensive Testing**: Easy to test with dependency injection
- **Performance Optimized**: Efficient scope management and error handling

This system solves the original challenges while maintaining flexibility and performance, providing a robust foundation for event-driven architecture with dependency injection.