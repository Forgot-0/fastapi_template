# from datetime import datetime, timedelta
# from uuid import uuid4
# from jose import jwt, JWTError
 

# def create_refresh_token(day) -> str:
#     """
#     Create a refresh token with an optional expiration time.

#     :param data: The data to encode in the token.
#     :param expires_delta: Optional timedelta for token expiration.
#     :return: The encoded JWT refresh token.
#     """
#     ttl = timedelta(days=day)
#     expire = ttl.total_seconds()

#     to_encode = {
#         "type": "refresh",
#         "exp": expire
#     }

#     encoded_jwt = jwt.encode(to_encode, "qeqw", algorithm='HS256')
#     return encoded_jwt



# print(create_refresh_token(day=2))
# print(create_refresh_token(day=3))
from typing import Dict, Iterator, Type, Any, List, Protocol
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dishka import Container, Provider, Scope, make_container, provide, decorate


# =========================
# Domain / ORM setup
# =========================
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

# create engine and session factory
engine = create_engine('sqlite:///:memory:', echo=True)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

# =========================
# CQRS: Command and Handler Protocol
# =========================
class Command(Protocol):
    ...

class Handler(Protocol):
    command_type: Type[Command]
    def handle(self, command: Command) -> Any: ...

# =========================
# Module: User Commands and Handler
# =========================
class CreateUserCommand:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

class CreateUserCommandHandler:
    command_type = CreateUserCommand

    def __init__(self, session: Session):
        self._session = session

    def handle(self, command: CreateUserCommand) -> User:
        user = User(name=command.name, email=command.email)
        print(self._session)
        self._session.add(user)
        self._session.commit()
        return user


class MockUserCommand:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

class MockUserCommandHandler:
    command_type = MockUserCommand

    def __init__(self, session: Session):
        self._session = session

    def handle(self, command: MockUserCommand) -> None:
        print(self._session)
        
        return None


# =========================
# Core Mediator Implementation
# =========================
class Mediator:
    def __init__(self):
        self._handlers: Dict[Type[Command], Handler] = {}

    def register(self, handler: Handler):
        self._handlers[handler.command_type] = handler

    def send(self, command: Command) -> Any:
        handler = self._handlers[type(command)]
        return handler.handle(command)

# =========================
# Module Providers
# =========================
class UserModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def session(self) -> Iterator[Session]:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @provide(scope=Scope.REQUEST)
    def create_user_handler(self, session: Session) -> CreateUserCommandHandler:
        return CreateUserCommandHandler(session)

    @provide(scope=Scope.REQUEST)
    def mock_user_handler(self, session: Session) -> MockUserCommandHandler:
        return MockUserCommandHandler(session=session)

# =========================
# Root Application Provider
# =========================



class MediatorProvider(Provider):
    scope = Scope.APP
    # собираем все обработчики модулей

    @provide(scope=Scope.APP)
    def mediator(self, container: Container) -> Mediator:
        m = Mediator()
        with container() as scope:
            m.register(scope.get(CreateUserCommandHandler))
        with container() as scope:
            m.register(scope.get(MockUserCommandHandler))
        return m


class AuthMediatorProvider(Provider):
    scope=Scope.APP
    # собираем все обработчики модулей

    # sp = provide(CreateUserCommandHandler, scope=Scope.REQUEST)

    # @provide
    # def app_mediator(self, m:Mediator, container: Container) -> None:
    #     with container() as scope:
    #         m.register(scope.get(CreateUserCommandHandler))
    #     return None




# =========================
# Application Bootstrap
# =========================
def build_app_container(module_providers: List[Provider]):
    # собираем всех провайдеров
    providers = module_providers
    # биндим все обработчики в одну коллекцию
    container = make_container(*providers)
    return container

# =========================
# Usage example
# =========================
if __name__ == '__main__':
    # определяем модули
    container = build_app_container([MediatorProvider(), UserModuleProvider(), AuthMediatorProvider()])


    # получаем mediator
    mediator: Mediator = container.get(Mediator)
    with container() as scope:
        handler = scope.get(CreateUserCommandHandler)
        result = handler.handle(CreateUserCommand('Alice', 'alice@example.com'))
        print(f"Created user: {result.id}, {result.name}, {result.email}")

    with container() as scope:
        handler = scope.get(MockUserCommandHandler)
        result = handler.handle(MockUserCommand('Alice', 'alice@sfg.com'))

    # выполняем команду в контексте запроса


    # result = handler.handle(CreateUserCommand('Alice', 'alice@example.com'))
    # result = mediator.send(CreateUserCommand('Alice', 'alice@example.com'))
    # result = mediator.send(CreateUserCommand('Alice', 'alice@sfg.com'))
    # result = mediator.send(CreateUserCommand('Alice', 'alice@vbf.com'))


