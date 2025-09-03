from dishka import Provider, Scope, provide

from app.auth.events.users.created import SendVerifyEventHandler



class AuthEventProvider(Provider):
    scope = Scope.REQUEST

    send_verify_email = provide(SendVerifyEventHandler)
