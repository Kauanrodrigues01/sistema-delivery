from logging import getLogger

from django.utils import timezone

from .models import DailyReport
from .utils import calculate_daily_report_data

logger = getLogger(__name__)


def generate_and_save_daily_report():
    """
    Gera e salva o relatório diário no banco de dados.
    Esta função é executada automaticamente às 23:55 todos os dias.
    """
    try:
        today = timezone.now().date()

        logger.info(f"[TASK] Iniciando geração do relatório diário para {today}")

        # Calcular dados do relatório
        data = calculate_daily_report_data()

        # Criar ou atualizar o relatório
        report, created = DailyReport.objects.update_or_create(
            date=today,
            defaults=data,
        )

        action = "criado" if created else "atualizado"
        logger.info(
            f"[TASK] Relatório diário {action} com sucesso: {data['quantity_orders']} pedidos, "
            f"R$ {data['revenue_today']:.2f} em receita"
        )

        return report

    except Exception as e:
        logger.error(
            f"[TASK] Erro ao gerar relatório diário: {type(e).__name__}: {str(e)}",
            exc_info=True,
        )
        raise
