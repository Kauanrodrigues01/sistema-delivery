from logging import getLogger

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse

logger = getLogger(__name__)


def health_check(request):
    """
    Health check endpoint para monitoramento da aplicação
    Verifica: Database, Cache (Redis) e WebSocket (Channels)
    """
    health_status = {
        "status": "healthy",
        "database": "ok",
        "cache": "ok",
        "websocket": "ok",
    }

    # Test DB connection
    try:
        logger.info("Health check: Testando conexão com Database...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        logger.info("Health check: Database OK")
    except Exception as e:
        logger.error(f"Health check: ERRO no Database - {type(e).__name__}: {str(e)}")
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"

    # Test cache (Redis)
    try:
        logger.info("Health check: Testando conexão com Redis Cache...")
        cache.set("health_check", "ok", 30)
        cache_ok = cache.get("health_check") == "ok"
        if not cache_ok:
            logger.error("Health check: ERRO no Redis Cache - Falha ao ler/escrever")
            health_status["status"] = "unhealthy"
            health_status["cache"] = "error: failed to read/write"
        else:
            logger.info("Health check: Redis Cache OK")
    except Exception as e:
        logger.error(
            f"Health check: ERRO no Redis Cache - {type(e).__name__}: {str(e)}"
        )
        health_status["status"] = "unhealthy"
        health_status["cache"] = f"error: {str(e)}"

    # Test WebSocket/Channels
    try:
        logger.info("Health check: Testando WebSocket/Channels (Redis backend)...")
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()

        if channel_layer is None:
            logger.error(
                "Health check: ERRO no WebSocket - Channel layer não configurado"
            )
            health_status["status"] = "unhealthy"
            health_status["websocket"] = "error: channel layer not configured"
        else:
            # Tenta enviar uma mensagem de teste para o channel layer
            # Isso verifica se o Redis backend do Channels está funcionando
            test_group = "health_check_test"
            async_to_sync(channel_layer.group_send)(
                test_group, {"type": "health.check", "message": "ping"}
            )
            logger.info("Health check: WebSocket/Channels OK")
            health_status["websocket"] = "ok"
    except Exception as e:
        logger.error(
            f"Health check: ERRO no WebSocket/Channels - {type(e).__name__}: {str(e)}"
        )
        health_status["status"] = "unhealthy"
        health_status["websocket"] = f"error: {str(e)}"

    # Log final
    if health_status["status"] == "healthy":
        logger.info("Health check: ✅ Todos os serviços estão saudáveis")
    else:
        logger.warning(f"Health check: ⚠️ Sistema UNHEALTHY - {health_status}")

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JsonResponse(health_status, status=status_code)


def cache_stats_view(request):
    """
    View para mostrar estatísticas do cache (apenas para admins)
    """
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        # Verificar se o Redis está disponível
        from django_redis import get_redis_connection

        # Obter conexão Redis diretamente
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()

        stats = {
            "used_memory": info.get("used_memory_human", "N/A"),
            "used_memory_peak": info.get("used_memory_peak_human", "N/A"),
            "total_keys": info.get("db1", {}).get("keys", 0),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "redis_version": info.get("redis_version", "N/A"),
            "connected_clients": info.get("connected_clients", 0),
        }

        # Calcular hit ratio
        hits = stats["hits"]
        misses = stats["misses"]
        stats["hit_ratio"] = (
            round(hits / (hits + misses), 4) if (hits + misses) > 0 else 0
        )

        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
