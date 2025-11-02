from logging import getLogger
from time import sleep

from django.db import transaction
from django.utils import timezone

from .models import DailyReport
from .utils import calculate_daily_report_data

logger = getLogger(__name__)


def generate_and_save_daily_report():
    """
    Gera e salva o relatório diário no banco de dados.
    Esta função é executada automaticamente às 23:55 todos os dias.
    """
    max_retries = 3
    retry_delay = 2  # segundos

    for attempt in range(max_retries):
        try:
            today = timezone.now().date()

            if attempt == 0:
                logger.info(
                    f"[TASK] Iniciando geração do relatório diário para {today}"
                )
            else:
                logger.info(
                    f"[TASK] Tentativa {attempt + 1} de {max_retries} para gerar relatório"
                )

            # Calcular dados do relatório
            data = calculate_daily_report_data()

            # Criar ou atualizar o relatório com transaction atomic
            with transaction.atomic():
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
            error_msg = f"{type(e).__name__}: {str(e)}"

            # Se for database locked e ainda temos tentativas, aguarda e tenta novamente
            if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                logger.warning(
                    f"[TASK] Database locked na tentativa {attempt + 1}. "
                    f"Aguardando {retry_delay}s antes de tentar novamente..."
                )
                sleep(retry_delay)
                retry_delay *= 2  # Backoff exponencial
                continue

            # Se não for database locked ou acabaram as tentativas, registra erro e levanta exceção
            logger.error(
                f"[TASK] Erro ao gerar relatório diário após {attempt + 1} tentativa(s): {error_msg}",
                exc_info=True,
            )
            raise

    # Se chegou aqui, todas as tentativas falharam
    logger.error(f"[TASK] Falha ao gerar relatório após {max_retries} tentativas")
    raise Exception(f"Falha ao gerar relatório após {max_retries} tentativas")
