from dishka import Provider, Scope, decorate, provide
from passlib.context import CryptContext
from redis.asyncio import Redis

from app.auth.commands.auth.auth_url import CreateOAuthAuthorizeUrlCommand, CreateOAuthAuthorizeUrlCommandHandler
from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler
from app.auth.commands.auth.logout import LogoutCommand, LogoutCommandHandler
from app.auth.commands.auth.oauth import (
    ProcessOAuthCallbackCommand,
    ProcessOAuthCallbackCommandHandler,
)
from app.auth.commands.auth.refresh_token import RefreshTokenCommand, RefreshTokenCommandHandler
from app.auth.commands.permissions.add_permission_user import (
    AddPermissionToUserCommand,
    AddPermissionToUserCommandHandler,
)
from app.auth.commands.permissions.create import CreatePermissionCommand, CreatePermissionCommandHandler
from app.auth.commands.permissions.delete import DeletePermissionCommand, DeletePermissionCommandHandler
from app.auth.commands.permissions.remove_permission_user import (
    DeletePermissionToUserCommand,
    DeletePermissionToUserCommandHandler,
)
from app.auth.commands.roles.add_permissions import AddPermissionRoleCommand, AddPermissionRoleCommandHandler
from app.auth.commands.roles.assign_role_to_user import AssignRoleCommand, AssignRoleCommandHandler
from app.auth.commands.roles.create import CreateRoleCommand, CreateRoleCommandHandler
from app.auth.commands.roles.delete_permissions import DeletePermissionRoleCommand, DeletePermissionRoleCommandHandler
from app.auth.commands.roles.remove_role_user import RemoveRoleCommand, RemoveRoleCommandHandler
from app.auth.commands.roles.update import RoleUpdateCommand, RoleUpdateCommandHandler
from app.auth.commands.sessions.deactivate_session import (
    UserDeactivateSessionCommand,
    UserDeactivateSessionCommandHandler,
)
from app.auth.commands.users.register import RegisterCommand, RegisterCommandHandler
from app.auth.commands.users.reset_password import ResetPasswordCommand, ResetPasswordCommandHandler
from app.auth.commands.users.send_reset_password import SendResetPasswordCommand, SendResetPasswordCommandHandler
from app.auth.commands.users.send_verify import SendVerifyCommand, SendVerifyCommandHandler
from app.auth.commands.users.verify import VerifyCommand, VerifyCommandHandler
from app.auth.config import auth_config
from app.auth.events.users.created import SendVerifyEventHandler
from app.auth.models.user import CreatedUserEvent
from app.auth.queries.auth.get_by_token import GetByAccessTokenQuery, GetByAccessTokenQueryHandler
from app.auth.queries.auth.oauth import GetUserOAuthAccountsQuery, GetUserOAuthAccountsQueryHandler
from app.auth.queries.auth.verify import VerifyTokenQuery, VerifyTokenQueryHandler
from app.auth.queries.permissions.get_list import GetListPemissionsQuery, GetListPemissionsQueryHandler
from app.auth.queries.roles.get_list import GetListRolesQuery, GetListRolesQueryHandler
from app.auth.queries.sessions.get_list import GetListSessionQuery, GetListSessionQueryHandler
from app.auth.queries.sessions.get_list_by_user import GetListSessionsUserQuery, GetListSessionsUserQueryHandler
from app.auth.queries.users.get_list import GetListUserQuery, GetListUserQueryHandler
from app.auth.repositories.oauth import OauthAccountRepository, OAuthCodeRepository
from app.auth.repositories.permission import PermissionInvalidateRepository, PermissionRepository
from app.auth.repositories.role import RoleInvalidateRepository, RoleRepository
from app.auth.repositories.session import SessionRepository, TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.cookie_manager import IRefreshTokenCookieManager, RefreshTokenCookieManager
from app.auth.services.hash import HashService
from app.auth.services.jwt import JWTManager
from app.auth.services.oauth_manager import OAuthManager, OAuthProviderFactory
from app.auth.services.oauth_providers import OAuthGithub, OAuthGoogle, OAuthYandex
from app.auth.services.rbac import RBACManager
from app.auth.services.session import SessionManager
from app.core.configs.app import app_config
from app.core.events.event import EventRegisty
from app.core.mediators.command import CommandRegisty
from app.core.mediators.query import QueryRegistry


class AuthModuleProvider(Provider):
    scope = Scope.REQUEST

    # repository
    user_repository = provide(UserRepository)
    token_repository = provide(SessionRepository)
    role_repository = provide(RoleRepository)
    permission_repository = provide(PermissionRepository)
    oauth_repository = provide(OauthAccountRepository)

    @provide(scope=Scope.APP)
    def token_blacklist(self) -> TokenBlacklistRepository:
        return TokenBlacklistRepository(
            Redis.from_url(app_config.redis_url)
        )

    @provide(scope=Scope.APP)
    def role_blacklist(self) -> RoleInvalidateRepository:
        return RoleInvalidateRepository(
            Redis.from_url(app_config.redis_url)
        )

    @provide(scope=Scope.APP)
    def permission_blacklist(self) -> PermissionInvalidateRepository:
        return PermissionInvalidateRepository(
            Redis.from_url(app_config.redis_url)
        )

    @provide(scope=Scope.APP)
    def oauth_code_repository(self) -> OAuthCodeRepository:
        return OAuthCodeRepository(
            Redis.from_url(app_config.redis_url)
        )

    #services
    @provide(scope=Scope.APP)
    def cookie_manager(self) -> RefreshTokenCookieManager:
        return IRefreshTokenCookieManager()

    @provide(scope=Scope.APP)
    def hash_service(self) -> HashService:
        return HashService(
            CryptContext(schemes=["bcrypt"], deprecated="auto")
        )

    @provide(scope=Scope.APP)
    def jwt_manager(self, token_blacklist: TokenBlacklistRepository) -> JWTManager:
        return JWTManager(
            jwt_secret=auth_config.JWT_SECRET_KEY,
            jwt_algorithm=auth_config.JWT_ALGORITHM,
            access_token_expire_minutes=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_expire_days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS,
            token_blacklist=token_blacklist
        )

    @provide(scope=Scope.APP)
    def oauth_factory(self) -> OAuthProviderFactory:
        provider_factory =  OAuthProviderFactory()

        if auth_config.OAUTH_GOOGLE_CLIENT_ID:
            provider_factory.register_provider(
                OAuthGoogle(
                    name="google",
                    client_id=auth_config.OAUTH_GOOGLE_CLIENT_ID,
                    client_secret=auth_config.OAUTH_GOOGLE_CLIENT_SECRET,
                    redirect_uri=auth_config.OAUTH_GOOGLE_REDIRECT_URI,
                    base_auth_url="https://accounts.google.com/o/oauth2/v2/auth",
                    token_url="https://oauth2.googleapis.com/token",
                    userinfo_url="https://openidconnect.googleapis.com/v1/userinfo"
                )
            )

        if auth_config.OAUTH_YANDEX_CLIENT_ID:
            provider_factory.register_provider(
                OAuthYandex(
                    name="yandex",
                    client_id=auth_config.OAUTH_YANDEX_CLIENT_ID,
                    client_secret=auth_config.OAUTH_YANDEX_CLIENT_SECRET,
                    redirect_uri=auth_config.OAUTH_YANDEX_REDIRECT_URI,
                    base_auth_url="https://oauth.yandex.ru/authorize",
                    token_url="https://oauth.yandex.ru/token",
                    userinfo_url="https://login.yandex.ru/info"
                )
            )

        if auth_config.OAUTH_GITHUB_CLIENT_ID:
            provider_factory.register_provider(
                OAuthGithub(
                    name="github",
                    client_id=auth_config.OAUTH_GITHUB_CLIENT_ID,
                    client_secret=auth_config.OAUTH_GITHUB_CLIENT_SECRET,
                    redirect_uri=auth_config.OAUTH_GITHUB_REDIRECT_URI,
                    base_auth_url="https://github.com/login/oauth/authorize",
                    token_url="https://github.com/login/oauth/access_token",
                    userinfo_url="https://api.github.com/user"
                )
            )

        return provider_factory


    @provide(scope=Scope.APP)
    def rbac_manager(self) -> RBACManager:
        return RBACManager()

    session_manager = provide(SessionManager)
    oauth_manager = provide(OAuthManager)

    #handelr command
    register_user_handler = provide(RegisterCommandHandler)
    reset_password_handler = provide(ResetPasswordCommandHandler)
    send_reset_password_handler = provide(SendResetPasswordCommandHandler)
    send_verify_handler = provide(SendVerifyCommandHandler)
    verify_handler = provide(VerifyCommandHandler)

    login_handler = provide(LoginCommandHandler)
    logout_handler = provide(LogoutCommandHandler)
    refresh_handler = provide(RefreshTokenCommandHandler)
    oauth_url = provide(CreateOAuthAuthorizeUrlCommandHandler)
    callback_oauth = provide(ProcessOAuthCallbackCommandHandler)

    create_role_handler = provide(CreateRoleCommandHandler)
    update_role_handler = provide(RoleUpdateCommandHandler)
    assign_role_handler = provide(AssignRoleCommandHandler)
    remove_role_handler = provide(RemoveRoleCommandHandler)
    add_permission_role_handler = provide(AddPermissionRoleCommandHandler)
    remove_permission_role_handler = provide(DeletePermissionRoleCommandHandler)

    create_permission_handler = provide(CreatePermissionCommandHandler)
    delete_permission_handler = provide(DeletePermissionCommandHandler)
    add_permission_to_user_handler = provide(AddPermissionToUserCommandHandler)
    delete_permission_to_user_handler = provide(DeletePermissionToUserCommandHandler)

    deactivate_session_handler = provide(UserDeactivateSessionCommandHandler)

    @decorate
    def register_auth_command_handlers(self, command_registry: CommandRegisty) -> CommandRegisty:
        # User commands
        command_registry.register_command(RegisterCommand, [RegisterCommandHandler])
        command_registry.register_command(VerifyCommand, [VerifyCommandHandler])
        command_registry.register_command(SendVerifyCommand, [SendVerifyCommandHandler])
        command_registry.register_command(ResetPasswordCommand, [ResetPasswordCommandHandler])
        command_registry.register_command(SendResetPasswordCommand, [SendResetPasswordCommandHandler])

        # Auth commands
        command_registry.register_command(LoginCommand, [LoginCommandHandler])
        command_registry.register_command(LogoutCommand, [LogoutCommandHandler])
        command_registry.register_command(RefreshTokenCommand, [RefreshTokenCommandHandler])

        # OAuth commands
        command_registry.register_command(CreateOAuthAuthorizeUrlCommand, [CreateOAuthAuthorizeUrlCommandHandler])
        command_registry.register_command(ProcessOAuthCallbackCommand, [ProcessOAuthCallbackCommandHandler])

        #Role
        command_registry.register_command(CreateRoleCommand, [CreateRoleCommandHandler])
        command_registry.register_command(AssignRoleCommand, [AssignRoleCommandHandler])
        command_registry.register_command(RemoveRoleCommand, [RemoveRoleCommandHandler])
        command_registry.register_command(AddPermissionRoleCommand, [AddPermissionRoleCommandHandler])
        command_registry.register_command(DeletePermissionRoleCommand, [DeletePermissionRoleCommandHandler])
        command_registry.register_command(RoleUpdateCommand, [RoleUpdateCommandHandler])

        #Permission
        command_registry.register_command(CreatePermissionCommand, [CreatePermissionCommandHandler])
        command_registry.register_command(DeletePermissionCommand, [DeletePermissionCommandHandler])
        command_registry.register_command(AddPermissionToUserCommand, [AddPermissionToUserCommandHandler])
        command_registry.register_command(DeletePermissionToUserCommand, [DeletePermissionToUserCommandHandler])

        # Session
        command_registry.register_command(UserDeactivateSessionCommand, [UserDeactivateSessionCommandHandler])
        return command_registry

    #event
    send_verify_email = provide(SendVerifyEventHandler)

    @decorate
    def register_auth_event_handlers(self, event_registry: EventRegisty) -> EventRegisty:
        # User events
        event_registry.subscribe(CreatedUserEvent, [
            SendVerifyEventHandler
        ])
        return event_registry

    # query
    get_jwt_data = provide(VerifyTokenQueryHandler)
    get_list_user_query_handler = provide(GetListUserQueryHandler)
    get_user_by_access_token_query_handler = provide(GetByAccessTokenQueryHandler)
    get_permissions_query_handler = provide(GetListPemissionsQueryHandler)
    get_roles_query_handler = provide(GetListRolesQueryHandler)
    get_list_user_sessions = provide(GetListSessionsUserQueryHandler)
    get_list_sessions = provide(GetListSessionQueryHandler)
    get_user_oauth_accounts = provide(GetUserOAuthAccountsQueryHandler)

    @decorate
    def register_auth_query_handlers(self, query_registry: QueryRegistry) -> QueryRegistry:
        # Auth
        query_registry.register_query(GetByAccessTokenQuery, GetByAccessTokenQueryHandler)
        query_registry.register_query(VerifyTokenQuery, VerifyTokenQueryHandler)

        # OAuth
        query_registry.register_query(GetUserOAuthAccountsQuery, GetUserOAuthAccountsQueryHandler)

        # User
        query_registry.register_query(GetListUserQuery, GetListUserQueryHandler)

        # Permissions
        query_registry.register_query(GetListPemissionsQuery, GetListPemissionsQueryHandler)

        # Role
        query_registry.register_query(GetListRolesQuery, GetListRolesQueryHandler)

        # Session
        query_registry.register_query(GetListSessionsUserQuery, GetListSessionsUserQueryHandler)
        query_registry.register_query(GetListSessionQuery, GetListSessionQueryHandler)
        return query_registry
