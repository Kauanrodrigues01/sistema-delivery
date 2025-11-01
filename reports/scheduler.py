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
    """
    global scheduler

    # Evita inicializar o scheduler múltiplas vezes
    if scheduler is not None:
        logger.info("Scheduler já está em execução")
        return

    # Só inicia o scheduler se não estiver em modo de migração ou testes
    import sys

    if "migrate" in sys.argv or "makemigrations" in sys.argv or "test" in sys.argv:
        logger.info("Pulando inicialização do scheduler durante migração/testes")
        return

    try:
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Agendar geração do relatório diário às 23:55
        scheduler.add_job(
            generate_and_save_daily_report,
            trigger=CronTrigger(hour=23, minute=55),  # Executa às 23:55 todos os dias
            id="generate_daily_report",
            name="Gerar relatório diário",
            replace_existing=True,
            max_instances=1,  # Garante que só uma instância rode por vez
        )

        scheduler.start()
        logger.info("Scheduler iniciado com sucesso. Relatórios diários serão gerados às 23:55")

    except Exception as e:
        logger.error(f"Erro ao iniciar scheduler: {type(e).__name__}: {str(e)}", exc_info=True)
