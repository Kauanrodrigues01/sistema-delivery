from django.utils import timezone

from core.models import ClientSession


def get_or_create_client_session(request):
    """
    Pega ou cria uma ClientSession baseada na sessão Django.
    Atualiza last_activity automaticamente.

    Args:
        request: HttpRequest object

    Returns:
        ClientSession: Instância da sessão do cliente
    """
    # Garantir que a sessão Django existe
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    # Tentar pegar da sessão Django primeiro (mais rápido)
    client_session_id = request.session.get("client_session_id")

    if client_session_id:
        try:
            client_session = ClientSession.objects.get(id=client_session_id)
            # Atualizar last_activity
            client_session.last_activity = timezone.now()
            client_session.save(update_fields=["last_activity"])
            return client_session
        except ClientSession.DoesNotExist:
            pass

    # Se não achou, buscar ou criar pelo session_key
    client_session, created = ClientSession.objects.get_or_create(
        session_key=session_key,
        defaults={
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:255],
            "ip_address": get_client_ip(request),
        },
    )

    if not created:
        # Atualizar last_activity se já existia
        client_session.last_activity = timezone.now()
        client_session.save(update_fields=["last_activity"])

    # Guardar ID na sessão Django para acesso rápido
    request.session["client_session_id"] = client_session.id

    return client_session


def get_client_ip(request):
    """
    Pega o IP real do cliente, considerando proxies
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
