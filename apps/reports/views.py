from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.reports.models import Report, Screenshot, StatusHistory
from apps.reports.forms import ReportForm
from django.http import HttpResponse, HttpResponseForbidden


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
    if plataforma and str(plataforma).isdigit(): qs = qs.filter(plataforma_id=plataforma)
    if tipo:       qs = qs.filter(tipo=tipo)
    if estado:     qs = qs.filter(estado=estado)
    if severidad:  qs = qs.filter(severidad=severidad)
    if q:          qs = qs.filter(titulo__icontains=q)
    return qs


@login_required
def new_report_view(request):
    form = ReportForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        report = form.save(commit=False)
        report.reportado_por = request.user
        report.save()
        for img in request.FILES.getlist('screenshots'):
            Screenshot.objects.create(reporte=report, imagen=img)
        return redirect('report_detail', pk=report.pk)
    return render(request, 'reports/new_report.html', {'form': form})

@login_required
def report_detail_view(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.user.is_usuario and report.reportado_por != request.user:
        return HttpResponseForbidden()
    return render(request, 'reports/report_detail.html', {
        'report': report,
        'estado_choices': Report.ESTADO_CHOICES,
    })


@role_required(User.TESTER, User.ADMIN)
def change_status_view(request, pk):
    report = get_object_or_404(Report, pk=pk)
    nuevo = request.POST.get('estado')
    if nuevo in dict(Report.ESTADO_CHOICES) and nuevo != report.estado:
        report.cambiar_estado(nuevo, request.user)
    if request.headers.get('HX-Request'):
        return render(request, 'partials/status_badge.html', {'report': report})
    return redirect('report_detail', pk=pk)


@role_required(User.TESTER, User.ADMIN)
def admin_reports_view(request):
    reports = _get_filtered_reports(request)
    platforms = Platform.objects.filter(activa=True)
    return render(request, 'reports/admin_reports.html', {
        'reports': reports,
        'platforms': platforms,
        'estado_choices': Report.ESTADO_CHOICES,
        'tipo_choices': Report.TIPO_CHOICES,
        'sev_choices': Report.SEV_CHOICES,
    })
