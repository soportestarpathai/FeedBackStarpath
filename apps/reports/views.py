from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden

from apps.accounts.decorators import tester_required, admin_required, superadmin_required
from apps.accounts.models import CustomUser
from apps.platforms.models import Platform
from apps.reports.models import Report, Screenshot, StatusHistory


# ─── Dispatch ──────────────────────────────────────────────────────────────

@login_required
def reportes_view(request):
    if request.user.rol == CustomUser.SUPERADMIN:
        return redirect('/superadmin/reportes/')
    if request.user.rol == CustomUser.ADMIN:
        return redirect('/admin/reportes/')
    if request.user.rol == CustomUser.TESTER:
        return _reportes_tester(request)
    return _reportes_usuario(request)


@login_required
def tabla_reportes_partial(request):
    if request.user.rol in (CustomUser.TESTER, CustomUser.ADMIN, CustomUser.SUPERADMIN):
        qs = _qs_tester(request)
        return render(request, 'partials/tabla_tester.html', {'reportes': qs, 'user': request.user})
    qs = _qs_usuario(request)
    return render(request, 'partials/tabla_usuario.html', {'reportes': qs})


# ─── TESTER ────────────────────────────────────────────────────────────────

def _qs_tester(request):
    plataformas_ids = request.user.plataformas_asignadas.values_list('id', flat=True)
    qs = Report.objects.select_related('plataforma', 'reportado_por', 'asignado_a').filter(
        plataforma_id__in=plataformas_ids
    )
    q          = request.GET.get('q', '').strip()
    plataforma = request.GET.get('plataforma', '')
    tipo       = request.GET.get('tipo', '')
    estado     = request.GET.get('estado', '')
    filtro     = request.GET.get('filtro', '')

    if q:          qs = qs.filter(titulo__icontains=q)
    if plataforma and plataforma.isdigit(): qs = qs.filter(plataforma_id=plataforma)
    if tipo:       qs = qs.filter(tipo=tipo)
    if estado:     qs = qs.filter(estado=estado)
    if filtro == 'mios':      qs = qs.filter(reportado_por=request.user)
    if filtro == 'asignados': qs = qs.filter(asignado_a=request.user)
    return qs


@tester_required
def _reportes_tester(request):
    qs = _qs_tester(request)
    plataformas_ids = request.user.plataformas_asignadas.values_list('id', flat=True)
    plataformas     = Platform.objects.filter(id__in=plataformas_ids)
    stats = {
        'visibles':  qs.count(),
        'bugs':      Report.objects.filter(plataforma_id__in=plataformas_ids, tipo=Report.BUG, estado=Report.ABIERTO).count(),
        'asignados': Report.objects.filter(plataforma_id__in=plataformas_ids, asignado_a=request.user).count(),
        'resueltos': Report.objects.filter(plataforma_id__in=plataformas_ids, estado=Report.RESUELTO).count(),
    }
    return render(request, 'reports/reportes_tester.html', {
        'reportes':       qs,
        'plataformas':    plataformas,
        'stats':          stats,
        'tipo_choices':   Report.TIPO_CHOICES,
        'estado_choices': Report.ESTADO_CHOICES,
    })


@login_required
def nuevo_reporte_tester(request):
    if request.user.rol == CustomUser.USUARIO:
        plataformas = Platform.objects.filter(activa=True)
    else:
        plataformas_ids = request.user.plataformas_asignadas.values_list('id', flat=True)
        plataformas     = Platform.objects.filter(id__in=plataformas_ids, activa=True)

    if request.method == 'POST':
        titulo    = request.POST.get('titulo', '').strip()
        desc      = request.POST.get('descripcion', '').strip()
        plat_id   = request.POST.get('plataforma', '')
        tipo      = request.POST.get('tipo', Report.BUG)
        severidad = request.POST.get('severidad', Report.MEDIA)
        if severidad == Report.CRITICA and request.user.rol in (CustomUser.USUARIO, CustomUser.TESTER):
            severidad = Report.ALTA
        url       = request.POST.get('url_pagina', '').strip()
        pasos     = request.POST.get('pasos_reproducir', '').strip()
        esperado  = request.POST.get('resultado_esperado', '').strip()
        obtenido  = request.POST.get('resultado_obtenido', '').strip()
        nav       = request.POST.get('navegador', '').strip()
        so        = request.POST.get('sistema_operativo', '').strip()

        rf_items = [t for t in request.POST.getlist('rf_items') if t.strip()]
        rnf_cats = request.POST.getlist('rnf_categorias')
        rnf_desc = request.POST.getlist('rnf_descripciones')
        rnf_items = [
            {'categoria': c, 'descripcion': d}
            for c, d in zip(rnf_cats, rnf_desc)
            if d.strip()
        ]

        if titulo and plat_id and plat_id.isdigit():
            reporte = Report.objects.create(
                titulo=titulo,
                descripcion=desc,
                plataforma_id=int(plat_id),
                tipo=tipo,
                severidad=severidad,
                url_pagina=url,
                pasos_reproducir=pasos,
                resultado_esperado=esperado,
                resultado_obtenido=obtenido,
                navegador=nav,
                sistema_operativo=so,
                requisitos_funcionales=rf_items,
                requisitos_no_funcionales=rnf_items,
                reportado_por=request.user,
            )
            for img in request.FILES.getlist('screenshots'):
                Screenshot.objects.create(reporte=reporte, imagen=img)
            return redirect(f'/reportes/{reporte.pk}/')

    if request.user.rol == CustomUser.USUARIO:
        return render(request, 'reports/nuevo_reporte_usuario.html', {
        'plataformas':  plataformas,
        'tipo_choices': Report.TIPO_CHOICES,
        'sev_choices':  [(k, v) for k, v in Report.SEV_CHOICES if k != Report.CRITICA],
    })
    return render(request, 'reports/nuevo_reporte_tester.html', {
    'plataformas':  plataformas,
    'tipo_choices': Report.TIPO_CHOICES,
    'sev_choices':  [(k, v) for k, v in Report.SEV_CHOICES if k != Report.CRITICA],
})


@login_required
def detalle_reporte_tester(request, pk):
    reporte  = get_object_or_404(Report.objects.select_related('plataforma', 'reportado_por', 'asignado_a'), pk=pk)
    if request.user.rol == CustomUser.USUARIO:
        if reporte.reportado_por != request.user:
            return HttpResponseForbidden()
    else:
        plat_ids = list(request.user.plataformas_asignadas.values_list('id', flat=True))
        if reporte.plataforma_id not in plat_ids:
            return HttpResponseForbidden()
    es_propio = (reporte.reportado_por == request.user)
    puede_cambiar_estado = (
        request.user.rol == CustomUser.TESTER
        or es_propio
    )
    historial = reporte.historial.select_related('cambiado_por').all()
    return render(request, 'reports/detalle_tester.html', {
        'reporte':              reporte,
        'es_propio':            es_propio,
        'puede_cambiar_estado': puede_cambiar_estado,
        'historial':            historial,
        'estado_choices':       Report.ESTADO_CHOICES,
    })


@login_required
@require_POST
def cambiar_estado_tester(request, pk):
    reporte = get_object_or_404(Report, pk=pk)
    if request.user.rol == CustomUser.USUARIO:
        if reporte.reportado_por != request.user:
            return HttpResponseForbidden()
    elif request.user.rol == CustomUser.TESTER:
        plat_ids = list(request.user.plataformas_asignadas.values_list('id', flat=True))
        if reporte.plataforma_id not in plat_ids:
            return HttpResponseForbidden()
    nuevo = request.POST.get('estado', '')
    nota  = request.POST.get('nota', '').strip()
    if nuevo in dict(Report.ESTADO_CHOICES) and nuevo != reporte.estado:
        reporte.cambiar_estado(nuevo, request.user, nota)
    # HTMX table row update; non-HTMX (detail page form) → redirect back
    if request.headers.get('HX-Request'):
        return render(request, 'partials/fila_tester.html', {'r': reporte, 'user': request.user})
    return redirect(f'/reportes/{pk}/')


@tester_required
def mis_plataformas_tester(request):
    plataformas = request.user.plataformas_asignadas.all()
    plat_data = []
    for p in plataformas:
        abiertos = Report.objects.filter(plataforma=p, estado=Report.ABIERTO).count()
        totales  = Report.objects.filter(plataforma=p).count()
        plat_data.append({'plataforma': p, 'abiertos': abiertos, 'totales': totales})
    return render(request, 'reports/mis_plataformas_tester.html', {'plat_data': plat_data})


# ─── USUARIO ───────────────────────────────────────────────────────────────

def _qs_usuario(request):
    qs = Report.objects.select_related('plataforma').filter(reportado_por=request.user)
    q      = request.GET.get('q', '').strip()
    tipo   = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')
    if q:      qs = qs.filter(titulo__icontains=q)
    if tipo:   qs = qs.filter(tipo=tipo)
    if estado: qs = qs.filter(estado=estado)
    return qs


@login_required
def _reportes_usuario(request):
    qs = _qs_usuario(request)
    stats = {
        'total':    Report.objects.filter(reportado_por=request.user).count(),
        'abiertos': Report.objects.filter(reportado_por=request.user, estado=Report.ABIERTO).count(),
        'revision': Report.objects.filter(reportado_por=request.user, estado=Report.EN_REVISION).count(),
        'resueltos':Report.objects.filter(reportado_por=request.user, estado=Report.RESUELTO).count(),
    }
    return render(request, 'reports/reportes_usuario.html', {
        'reportes':       qs,
        'stats':          stats,
        'tipo_choices':   Report.TIPO_CHOICES,
        'estado_choices': Report.ESTADO_CHOICES,
    })


# ─── ADMIN ─────────────────────────────────────────────────────────────────

def _plat_ids_admin(request):
    return list(request.user.plataformas_asignadas.values_list('id', flat=True))


def _qs_admin(request):
    ids = _plat_ids_admin(request)
    qs  = Report.objects.select_related('plataforma', 'reportado_por', 'asignado_a').filter(
        plataforma_id__in=ids
    )
    q         = request.GET.get('q', '').strip()
    tipo      = request.GET.get('tipo', '')
    estado    = request.GET.get('estado', '')
    severidad = request.GET.get('severidad', '')
    asignado  = request.GET.get('asignado', '')
    if q:         qs = qs.filter(titulo__icontains=q)
    if tipo:      qs = qs.filter(tipo=tipo)
    if estado:    qs = qs.filter(estado=estado)
    if severidad: qs = qs.filter(severidad=severidad)
    if asignado == 'sin':  qs = qs.filter(asignado_a__isnull=True)
    if asignado == 'con':  qs = qs.filter(asignado_a__isnull=False)
    reportado_por = request.GET.get('reportado_por', '')
    if reportado_por and reportado_por.isdigit():
        qs = qs.filter(reportado_por_id=int(reportado_por))
    return qs


@admin_required
def resumen_admin(request):
    ids        = _plat_ids_admin(request)
    plataforma = request.user.plataformas_asignadas.first()

    stats = {
        'total':     Report.objects.filter(plataforma_id__in=ids).count(),
        'abiertos':  Report.objects.filter(plataforma_id__in=ids, estado=Report.ABIERTO).count(),
        'criticos':  Report.objects.filter(plataforma_id__in=ids, severidad=Report.CRITICA, estado=Report.ABIERTO).count(),
        'resueltos': Report.objects.filter(plataforma_id__in=ids, estado=Report.RESUELTO).count(),
    }
    reportes_criticos = (
        Report.objects.filter(plataforma_id__in=ids, severidad=Report.CRITICA, estado=Report.ABIERTO)
        .select_related('asignado_a')
        .order_by('-creado_en')[:3]
    )
    actividad_reciente = (
        StatusHistory.objects.filter(reporte__plataforma_id__in=ids)
        .select_related('reporte', 'cambiado_por')
        .order_by('-fecha')[:5]
    )
    info = {
        'testers':        CustomUser.objects.filter(plataformas_asignadas__in=ids, rol=CustomUser.TESTER).distinct().count(),
        'usuarios':       CustomUser.objects.filter(plataformas_asignadas__in=ids, rol=CustomUser.USUARIO).distinct().count(),
        'total_reportes': Report.objects.filter(plataforma_id__in=ids).count(),
        'criticos_sin':   Report.objects.filter(plataforma_id__in=ids, severidad=Report.CRITICA, estado=Report.ABIERTO, asignado_a__isnull=True).count(),
    }
    return render(request, 'reports/resumen_admin.html', {
        'plataforma':        plataforma,
        'stats':             stats,
        'reportes_criticos': reportes_criticos,
        'actividad_reciente':actividad_reciente,
        'info':              info,
    })


@admin_required
def reportes_admin(request):
    ids        = _plat_ids_admin(request)
    qs         = _qs_admin(request)
    testers    = CustomUser.objects.filter(plataformas_asignadas__in=ids, rol=CustomUser.TESTER).distinct()
    stats = {
        'total':    Report.objects.filter(plataforma_id__in=ids).count(),
        'abiertos': Report.objects.filter(plataforma_id__in=ids, estado=Report.ABIERTO).count(),
        'criticos': Report.objects.filter(plataforma_id__in=ids, severidad=Report.CRITICA, estado=Report.ABIERTO).count(),
        'resueltos':Report.objects.filter(plataforma_id__in=ids, estado=Report.RESUELTO).count(),
    }
    return render(request, 'reports/reportes_admin.html', {
        'reportes':       qs,
        'testers':        testers,
        'stats':          stats,
        'tipo_choices':   Report.TIPO_CHOICES,
        'estado_choices': Report.ESTADO_CHOICES,
        'sev_choices':    Report.SEV_CHOICES,
    })


@admin_required
def tabla_admin_partial(request):
    qs      = _qs_admin(request)
    ids     = _plat_ids_admin(request)
    testers = CustomUser.objects.filter(plataformas_asignadas__in=ids, rol=CustomUser.TESTER).distinct()
    return render(request, 'partials/tabla_admin.html', {
        'reportes': qs,
        'testers':  testers,
        'user':     request.user,
    })


@admin_required
def detalle_reporte_admin(request, pk):
    ids     = _plat_ids_admin(request)
    reporte = get_object_or_404(
        Report.objects.select_related('plataforma', 'reportado_por', 'asignado_a'), pk=pk
    )
    if reporte.plataforma_id not in ids:
        return HttpResponseForbidden()
    testers  = CustomUser.objects.filter(plataformas_asignadas__in=ids, rol=CustomUser.TESTER).distinct()
    historial = reporte.historial.select_related('cambiado_por').all()
    return render(request, 'reports/detalle_admin.html', {
        'reporte':        reporte,
        'testers':        testers,
        'historial':      historial,
        'estado_choices': Report.ESTADO_CHOICES,
    })


@admin_required
@require_POST
def cambiar_estado_admin(request, pk):
    ids     = _plat_ids_admin(request)
    reporte = get_object_or_404(Report, pk=pk)
    if reporte.plataforma_id not in ids:
        return HttpResponseForbidden()
    nuevo = request.POST.get('estado', '')
    nota  = request.POST.get('nota', '').strip()
    if nuevo in dict(Report.ESTADO_CHOICES) and nuevo != reporte.estado:
        reporte.cambiar_estado(nuevo, request.user, nota)
    testers = CustomUser.objects.filter(plataformas_asignadas__in=ids, rol=CustomUser.TESTER).distinct()
    return render(request, 'partials/fila_admin.html', {
        'r':       reporte,
        'testers': testers,
        'user':    request.user,
    })


@admin_required
@require_POST
def asignar_tester(request, pk):
    ids     = _plat_ids_admin(request)
    reporte = get_object_or_404(Report, pk=pk)
    if reporte.plataforma_id not in ids:
        return HttpResponseForbidden()
    tester_id = request.POST.get('asignado_a', '')
    if tester_id == '':
        reporte.asignado_a = None
    elif tester_id.isdigit():
        try:
            tester = CustomUser.objects.get(pk=int(tester_id), rol=CustomUser.TESTER)
            reporte.asignado_a = tester
        except CustomUser.DoesNotExist:
            pass
    reporte.save()
    testers = CustomUser.objects.filter(plataformas_asignadas__in=ids, rol=CustomUser.TESTER).distinct()
    return render(request, 'partials/asignacion.html', {
        'reporte': reporte,
        'testers': testers,
    })


# ─── SUPERADMIN REPORTS ────────────────────────────────────────────────────

@superadmin_required
def reportes_superadmin(request):
    from apps.platforms.models import Platform
    qs = Report.objects.select_related('plataforma', 'reportado_por', 'asignado_a')
    q         = request.GET.get('q', '').strip()
    plataforma= request.GET.get('plataforma', '')
    tipo      = request.GET.get('tipo', '')
    estado    = request.GET.get('estado', '')
    severidad = request.GET.get('severidad', '')
    if q:         qs = qs.filter(titulo__icontains=q)
    if plataforma and plataforma.isdigit(): qs = qs.filter(plataforma_id=plataforma)
    if tipo:      qs = qs.filter(tipo=tipo)
    if estado:    qs = qs.filter(estado=estado)
    if severidad: qs = qs.filter(severidad=severidad)
    stats = {
        'total':    Report.objects.count(),
        'abiertos': Report.objects.filter(estado=Report.ABIERTO).count(),
        'criticos': Report.objects.filter(severidad=Report.CRITICA, estado=Report.ABIERTO).count(),
        'resueltos':Report.objects.filter(estado=Report.RESUELTO).count(),
    }
    return render(request, 'superadmin/reportes_sa.html', {
        'reportes':       qs,
        'plataformas':    Platform.objects.all(),
        'stats':          stats,
        'tipo_choices':   Report.TIPO_CHOICES,
        'estado_choices': Report.ESTADO_CHOICES,
        'sev_choices':    Report.SEV_CHOICES,
    })


@superadmin_required
def tabla_sa_partial(request):
    from apps.platforms.models import Platform
    qs = Report.objects.select_related('plataforma', 'reportado_por', 'asignado_a')
    q         = request.GET.get('q', '').strip()
    plataforma= request.GET.get('plataforma', '')
    tipo      = request.GET.get('tipo', '')
    estado    = request.GET.get('estado', '')
    severidad = request.GET.get('severidad', '')
    if q:         qs = qs.filter(titulo__icontains=q)
    if plataforma and plataforma.isdigit(): qs = qs.filter(plataforma_id=plataforma)
    if tipo:      qs = qs.filter(tipo=tipo)
    if estado:    qs = qs.filter(estado=estado)
    if severidad: qs = qs.filter(severidad=severidad)
    return render(request, 'partials/tabla_sa.html', {'reportes': qs})


@superadmin_required
@require_POST
def cambiar_estado_sa(request, pk):
    reporte = get_object_or_404(Report, pk=pk)
    nuevo   = request.POST.get('estado', '')
    nota    = request.POST.get('nota', '').strip()
    if nuevo in dict(Report.ESTADO_CHOICES) and nuevo != reporte.estado:
        reporte.cambiar_estado(nuevo, request.user, nota)
    return render(request, 'partials/fila_sa.html', {'r': reporte})