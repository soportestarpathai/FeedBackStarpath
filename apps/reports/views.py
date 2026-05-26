from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.reports.models import Report, StatusHistory
from django.http import HttpResponse


@login_required
def dashboard_view(request):
    reports = _get_filtered_reports(request)
    platforms = Platform.objects.filter(activa=True)
    stats = {
        'total':     Report.objects.count() if not request.user.is_usuario else reports.count(),
        'criticos':  reports.filter(severidad=Report.CRITICA, estado=Report.ABIERTO).count(),
        'revision':  reports.filter(estado=Report.EN_REVISION).count(),
        'resueltos': reports.filter(estado=Report.RESUELTO).count(),
    }
    return render(request, 'reports/dashboard.html', {
        'reports': reports,
        'platforms': platforms,
        'stats': stats,
        'estado_choices': Report.ESTADO_CHOICES,
        'tipo_choices': Report.TIPO_CHOICES,
        'sev_choices': Report.SEV_CHOICES,
    })


@login_required
def reports_table_partial(request):
    reports = _get_filtered_reports(request)
    return render(request, 'partials/reports_table.html', {'reports': reports})


def _get_filtered_reports(request):
    qs = Report.objects.select_related('plataforma', 'reportado_por')
    if request.user.is_usuario:
        qs = qs.filter(reportado_por=request.user)
    plataforma = request.GET.get('plataforma')
    tipo       = request.GET.get('tipo')
    estado     = request.GET.get('estado')
    severidad  = request.GET.get('severidad')
    q          = request.GET.get('q')
    if plataforma: qs = qs.filter(plataforma_id=plataforma)
    if tipo:       qs = qs.filter(tipo=tipo)
    if estado:     qs = qs.filter(estado=estado)
    if severidad:  qs = qs.filter(severidad=severidad)
    if q:          qs = qs.filter(titulo__icontains=q)
    return qs


# Stubs — replace in Tasks 9-10
def new_report_view(request):
    return HttpResponse('TODO')

def report_detail_view(request, pk):
    return HttpResponse('TODO')

def admin_reports_view(request):
    return HttpResponse('TODO')

def change_status_view(request, pk):
    return HttpResponse('TODO')
