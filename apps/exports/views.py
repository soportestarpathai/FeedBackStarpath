import base64
import os
from io import BytesIO

from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML

from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.reports.models import Report


@role_required(User.ADMIN)
def pdf_form_view(request):
    platforms = Platform.objects.filter(activa=True)
    return render(request, 'exports/pdf_form.html', {
        'platforms': platforms,
        'estado_choices': Report.ESTADO_CHOICES,
        'sev_choices': Report.SEV_CHOICES,
    })


@role_required(User.ADMIN)
def pdf_download_view(request):
    qs = Report.objects.select_related('plataforma', 'reportado_por').prefetch_related('screenshots')
    plataforma = request.GET.get('plataforma')
    estado     = request.GET.get('estado')
    severidad  = request.GET.get('severidad')
    desde      = request.GET.get('desde')
    hasta      = request.GET.get('hasta')

    if plataforma and str(plataforma).isdigit():
        qs = qs.filter(plataforma_id=plataforma)
    if estado:    qs = qs.filter(estado=estado)
    if severidad: qs = qs.filter(severidad=severidad)
    if desde:     qs = qs.filter(creado_en__date__gte=desde)
    if hasta:     qs = qs.filter(creado_en__date__lte=hasta)

    reports_data = []
    for r in qs:
        shots = []
        for s in r.screenshots.all():
            if s.imagen and os.path.exists(s.imagen.path):
                with open(s.imagen.path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode()
                    shots.append(f'data:image/jpeg;base64,{b64}')
        reports_data.append({'report': r, 'screenshots_b64': shots})

    html_string = render_to_string('pdf/report.html', {
        'reports_data': reports_data,
        'generado_en': timezone.now(),
        'filtros': {
            'plataforma': Platform.objects.filter(pk=plataforma).first() if plataforma else None,
            'estado': estado,
            'severidad': severidad,
            'desde': desde,
            'hasta': hasta,
        },
        'totales': {
            'total':       qs.count(),
            'bugs':        qs.filter(tipo=Report.BUG).count(),
            'sugerencias': qs.filter(tipo=Report.SUGERENCIA).count(),
            'quejas':      qs.filter(tipo=Report.QUEJA).count(),
            'criticos':    qs.filter(severidad=Report.CRITICA).count(),
            'resueltos':   qs.filter(estado=Report.RESUELTO).count(),
        },
    })

    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)
    pdf_file.seek(0)

    filename = f"reporte-feedbackeve-{timezone.now().strftime('%Y-%m-%d')}.pdf"
    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
