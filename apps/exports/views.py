import base64
import os
from io import BytesIO

from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from apps.accounts.decorators import admin_required
from apps.accounts.models import CustomUser
from apps.platforms.models import Platform
from apps.reports.models import Report


@admin_required
def exportar_pdf(request):
    is_sa = request.user.rol == CustomUser.SUPERADMIN
    if is_sa:
        plataformas = Platform.objects.all()
    else:
        plataformas = request.user.plataformas_asignadas.all()

    if request.method == 'POST':
        qs = Report.objects.select_related('plataforma', 'reportado_por', 'asignado_a').prefetch_related('screenshots', 'historial')

        if not is_sa:
            ids = list(request.user.plataformas_asignadas.values_list('id', flat=True))
            qs = qs.filter(plataforma_id__in=ids)

        plat_id   = request.POST.get('plataforma', '')
        estado    = request.POST.get('estado', '')
        severidad = request.POST.get('severidad', '')
        tipo      = request.POST.get('tipo', '')
        desde     = request.POST.get('desde', '')
        hasta     = request.POST.get('hasta', '')

        if plat_id and plat_id.isdigit(): qs = qs.filter(plataforma_id=plat_id)
        if estado:    qs = qs.filter(estado=estado)
        if severidad: qs = qs.filter(severidad=severidad)
        if tipo:      qs = qs.filter(tipo=tipo)
        if desde:     qs = qs.filter(creado_en__date__gte=desde)
        if hasta:     qs = qs.filter(creado_en__date__lte=hasta)

        inc_resumen   = 'inc_resumen'   in request.POST
        inc_tabla     = 'inc_tabla'     in request.POST
        inc_tecnico   = 'inc_tecnico'   in request.POST
        inc_historial = 'inc_historial' in request.POST

        reports_data = []
        for r in qs:
            shots = []
            for s in r.screenshots.all():
                if s.imagen and os.path.exists(s.imagen.path):
                    with open(s.imagen.path, 'rb') as f:
                        b64 = base64.b64encode(f.read()).decode()
                        shots.append(f'data:image/jpeg;base64,{b64}')
            reports_data.append({'report': r, 'screenshots_b64': shots})

        filtro_plat = Platform.objects.filter(pk=plat_id).first() if plat_id and plat_id.isdigit() else None

        html_string = render_to_string('exports/pdf_template.html', {
            'reports_data':  reports_data,
            'generado_en':   timezone.now(),
            'plataforma':    filtro_plat,
            'inc_resumen':   inc_resumen,
            'inc_tabla':     inc_tabla,
            'inc_tecnico':   inc_tecnico,
            'inc_historial': inc_historial,
            'totales': {
                'total':       qs.count(),
                'bugs':        qs.filter(tipo=Report.BUG).count(),
                'sugerencias': qs.filter(tipo=Report.SUGERENCIA).count(),
                'quejas':      qs.filter(tipo=Report.QUEJA).count(),
                'criticos':    qs.filter(severidad=Report.CRITICA).count(),
                'resueltos':   qs.filter(estado=Report.RESUELTO).count(),
            },
        })

        try:
            from weasyprint import HTML
            pdf_buf = BytesIO()
            HTML(string=html_string).write_pdf(pdf_buf)
            pdf_buf.seek(0)
            fname = f"feedbackeve-{timezone.now().strftime('%Y-%m-%d')}.pdf"
            response = HttpResponse(pdf_buf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{fname}"'
            return response
        except Exception as e:
            return HttpResponse(f'Error generando PDF: {e}', status=500)

    return render(request, 'exports/exportar_pdf.html', {
        'plataformas':    plataformas,
        'estado_choices': Report.ESTADO_CHOICES,
        'sev_choices':    Report.SEV_CHOICES,
        'tipo_choices':   Report.TIPO_CHOICES,
        'is_sa':          is_sa,
    })
