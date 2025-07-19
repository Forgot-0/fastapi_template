from typing import TypeVar, Callable, Any
from functools import wraps

from dishka import Container
from dishka.integrations.fastapi import setup_dishka, FromDishka
from fastapi import FastAPI, Depends

from app.core.di.container import container


T = TypeVar('T')


def setup_di(app: FastAPI) -> None:
    """Setup dependency injection for FastAPI application."""
    setup_dishka(container, app)


def inject(dependency_type: type[T]) -> T:
    """Helper function to inject dependencies in FastAPI endpoints."""
    return FromDishka(dependency_type)


def di_depends(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to automatically inject dependencies based on type annotations."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get function signature and inject dependencies
        import inspect
        sig = inspect.signature(func)
        
        injected_kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name not in kwargs and param.annotation != inspect.Parameter.empty:
                try:
                    # Try to get dependency from container
                    with container() as request_container:
                        injected_kwargs[param_name] = request_container.get(param.annotation)
                except Exception:
                    # If injection fails, skip this parameter
                    pass
        
        kwargs.update(injected_kwargs)
        return await func(*args, **kwargs)
    
    return wrapper


# Export commonly used dependencies
def get_container() -> Container:
    """Get the main DI container."""
    return container