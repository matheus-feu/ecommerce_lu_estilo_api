import sentry_sdk
from sentry_sdk import capture_exception, configure_scope

from src.core.settings import settings


def sentry_before_send(event, hint):
    if 'log_record' in hint:
        if hint['log_record'].name == 'suds.client':
            return None

    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        if isinstance(exc_value, ValueError):
            if exc_value.args and 'Invalid traceparent version' in exc_value.args[0]:
                return None

    return event


sentry_sdk.init(
    dsn=settings.sentry.SENTRY_DSN,
    traces_sample_rate=0,
    before_send=sentry_before_send,
    sample_rate=1,
    auto_session_tracking=True,
    send_default_pii=True,
    debug=False,
    release="luestilo@0.1.0"
)


def send_to_sentry(error, user=None):
    """
    Envia erro ao Sentry com informações do usuário autenticado, se disponível.
    :param error: Exceção a ser enviada
    :param user: Usuário autenticado (opcional)
    """
    with configure_scope() as scope:
        try:
            if user:
                scope.user = {
                    "id": getattr(user, "id", None),
                    "email": getattr(user, "email", None),
                    "username": getattr(user, "name", None),
                }
            else:
                scope.user = {"id": settings.app.APP_NAME}
            scope.set_tag("domain", settings.app.APP_HOST)
        except Exception:
            pass

    capture_exception(error)
