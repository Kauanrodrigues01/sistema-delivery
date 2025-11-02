import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore

from .tasks import generate_and_save_daily_report

logger = logging.getLogger(__name__)

scheduler = None


def start_scheduler():
    """
    Inicia o scheduler em background para executar tarefas agendadas.
    Roda em uma thread separada para evitar conflitos com ASGI/async context.
    """
    global scheduler

    # Evita inicializar o scheduler múltiplas vezes
    if scheduler is not None:
        logger.info("Scheduler já está em execução")
        return

    # Só inicia o scheduler se não estiver em modo de migração, testes, collectstatic ou compress
    import sys

    skip_commands = [
        "migrate",
        "makemigrations",
        "test",
        "collectstatic",
        "compress",
        "compilemessages",
        "createcachetable",
    ]

    if any(cmd in sys.argv for cmd in skip_commands):
        logger.info(
            f"Pulando inicialização do scheduler durante comando de gerenciamento: {sys.argv}"
        )
        return

    try:
        # Rodar o scheduler em uma thread separada para evitar problemas com ASGI/async
        import threading

        def _start_scheduler_thread():
            global scheduler
            try:
                scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
                scheduler.add_jobstore(DjangoJobStore(), "default")

                # Agendar geração do relatório diário às 23:55
                scheduler.add_job(
                    generate_and_save_daily_report,
                    trigger=CronTrigger(
                        hour=00, minute=17
                    ),  # Executa às 23:55 todos os dias
                    id="generate_daily_report",
                    name="Gerar relatório diário",
                    replace_existing=True,
                    max_instances=1,  # Garante que só uma instância rode por vez
                )

                scheduler.start()
                logger.info(
                    "Scheduler iniciado com sucesso. Relatórios diários serão gerados às 23:55"
                )

            except Exception as e:
                logger.error(
                    f"Erro ao iniciar scheduler na thread: {type(e).__name__}: {str(e)}",
                    exc_info=True,
                )

        # Iniciar em thread daemon para não bloquear o shutdown
        thread = threading.Thread(
            target=_start_scheduler_thread, daemon=True, name="SchedulerThread"
        )
        thread.start()
        logger.info("Thread do scheduler iniciada")

    except Exception as e:
        logger.error(
            f"Erro ao criar thread do scheduler: {type(e).__name__}: {str(e)}",
            exc_info=True,
        )
