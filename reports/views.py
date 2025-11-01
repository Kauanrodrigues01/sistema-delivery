from logging import getLogger

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML

from .models import DailyReport
from .utils import calculate_daily_report_data

logger = getLogger(__name__)


@login_required
def get_daily_report(request):
    """
    Retorna dados do relatório diário em formato JSON.
    """
    if not request.user.is_staff:
        logger.warning(
            f"Tentativa de acesso não autorizado ao relatório por: {request.user.username}"
        )
        return HttpResponseForbidden("You are not authorized to view this report.")

    logger.info("Gerando relatório diário JSON")

    data = calculate_daily_report_data()

    logger.info(
        f"Relatório gerado: {data['quantity_orders']} pedidos, "
        f"R$ {data['revenue_today']:.2f} em receita"
    )

    return JsonResponse(data)


@login_required
def daily_report_pdf(request):
    """
    Gera um PDF do relatório diário usando WeasyPrint.
    """
    if not request.user.is_staff:
        logger.warning(
            f"Tentativa de acesso não autorizado ao PDF do relatório por: {request.user.username}"
        )
        return HttpResponseForbidden("You are not authorized to view this report.")

    logger.info(f"Gerando PDF do relatório diário para {request.user.username}")

    today = timezone.now()
    data = calculate_daily_report_data()

    # Renderizar template HTML
    html_string = render_to_string(
        "reports/daily_report.html",
        {
            "data": data,
            "date": today,
            "now": timezone.now(),
        },
    )

    # Gerar PDF com WeasyPrint
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    # Preparar resposta HTTP
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="relatorio_diario_{today.strftime("%Y%m%d")}.pdf"'
    )

    logger.info(f"PDF do relatório gerado com sucesso para {today.date()}")

    return response


@login_required
def saved_report_pdf(request, report_id):
    """
    Gera PDF a partir de um relatório salvo no banco de dados.

    Args:
        report_id: ID do relatório no banco de dados
    """
    if not request.user.is_staff:
        logger.warning(
            f"Tentativa de acesso não autorizado ao PDF de relatório salvo por: {request.user.username}"
        )
        return HttpResponseForbidden("You are not authorized to view this report.")

    # Buscar relatório salvo
    report = get_object_or_404(DailyReport, id=report_id)

    logger.info(f"Gerando PDF do relatório salvo de {report.date} para {request.user.username}")

    # Obter dados do relatório
    data = report.get_data_dict()

    # Renderizar template HTML
    html_string = render_to_string(
        "reports/daily_report.html",
        {
            "data": data,
            "date": report.date,
            "now": timezone.now(),
        },
    )

    # Gerar PDF com WeasyPrint
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    # Preparar resposta HTTP
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="relatorio_diario_{report.date.strftime("%Y%m%d")}.pdf"'
    )

    logger.info(f"PDF do relatório salvo gerado com sucesso para {report.date}")

    return response
