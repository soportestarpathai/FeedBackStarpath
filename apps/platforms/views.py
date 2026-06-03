from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from apps.accounts.decorators import superadmin_required
from apps.accounts.models import CustomUser
from apps.platforms.models import Platform
from apps.reports.models import Report, StatusHistory


@superadmin_required
def dashboard_superadmin(request):
    plataformas = Platform.objects.all()

    actividad = []
    for p in plataformas:
        admins = CustomUser.objects.filter(plataformas_asignadas=p, rol=CustomUser.ADMIN)
        abiertos  = Report.objects.filter(plataforma=p, estado=Report.ABIERTO).count()
        resueltos = Report.objects.filter(plataforma=p, estado=Report.RESUELTO).count()
        ultimo    = Report.objects.filter(plataforma=p).order_by('-creado_en').first()
        actividad.append({
            'plataforma': p,
            'admins':     admins,
            'abiertos':   abiertos,
            'resueltos':  resueltos,
            'ultimo':     ultimo,
        })

    admins = CustomUser.objects.filter(rol=CustomUser.ADMIN).order_by('email')

    hace_30 = timezone.now() - timedelta(days=30)
    mes_actual = Report.objects.filter(creado_en__gte=hace_30).count()

    resueltos_con_hist = StatusHistory.objects.filter(
        estado_nuevo=Report.RESUELTO
    ).select_related('reporte')
    tiempos = []
    for h in resueltos_con_hist[:50]:
        delta = (h.fecha - h.reporte.creado_en).total_seconds() / 3600
        if delta > 0:
            tiempos.append(delta)
    avg_horas = round(sum(tiempos) / len(tiempos), 1) if tiempos else 0

    plats_sin_admin = sum(
        1 for p in plataformas
        if not CustomUser.objects.filter(plataformas_asignadas=p, rol=CustomUser.ADMIN).exists()
    )
    total_reportes = Report.objects.count()
    total_resueltos = Report.objects.filter(estado=Report.RESUELTO).count()
    tasa_fix = round((total_resueltos / total_reportes * 100), 1) if total_reportes else 0

    resumen = {
        'usuarios':       CustomUser.objects.count(),
        'reportes_mes':   mes_actual,
        'avg_horas':      avg_horas,
        'sin_admin':      plats_sin_admin,
        'tasa_fix':       tasa_fix,
        'criticos':       Report.objects.filter(severidad=Report.CRITICA, estado=Report.ABIERTO).count(),
    }

    return render(request, 'superadmin/dashboard_superadmin.html', {
        'actividad':  actividad,
        'admins':     admins,
        'resumen':    resumen,
        'plataformas': plataformas,
    })


@superadmin_required
def lista_plataformas(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        desc   = request.POST.get('descripcion', '').strip()
        color  = request.POST.get('color', '#2563eb').strip()
        if nombre:
            Platform.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc, 'color': color})
        return redirect('/superadmin/plataformas/')
    plataformas = Platform.objects.all()
    plat_data = []
    for p in plataformas:
        admins   = CustomUser.objects.filter(plataformas_asignadas=p, rol=CustomUser.ADMIN)
        abiertos = Report.objects.filter(plataforma=p, estado=Report.ABIERTO).count()
        totales  = Report.objects.filter(plataforma=p).count()
        plat_data.append({'plataforma': p, 'admins': admins, 'abiertos': abiertos, 'totales': totales})
    return render(request, 'superadmin/lista_plataformas.html', {'plat_data': plat_data})


@superadmin_required
@require_POST
def toggle_plataforma(request, pk):
    p = get_object_or_404(Platform, pk=pk)
    p.activa = not p.activa
    p.save()
    admins   = CustomUser.objects.filter(plataformas_asignadas=p, rol=CustomUser.ADMIN)
    abiertos = Report.objects.filter(plataforma=p, estado=Report.ABIERTO).count()
    totales  = Report.objects.filter(plataforma=p).count()
    return render(request, 'partials/card_plataforma.html', {
        'item': {'plataforma': p, 'admins': admins, 'abiertos': abiertos, 'totales': totales}
    })


@superadmin_required
@require_POST
def eliminar_plataforma(request, pk):
    get_object_or_404(Platform, pk=pk).delete()
    return redirect('/superadmin/plataformas/')


@superadmin_required
def lista_admins(request):
    admins = CustomUser.objects.filter(rol=CustomUser.ADMIN).prefetch_related('plataformas_asignadas').order_by('email')
    plataformas = Platform.objects.filter(activa=True)
    return render(request, 'superadmin/lista_admins.html', {
        'admins':     admins,
        'plataformas': plataformas,
    })


@superadmin_required
def crear_admin(request):
    if request.method == 'POST':
        email     = request.POST.get('email', '').strip()
        first_name= request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password  = request.POST.get('password', '').strip()
        plats     = request.POST.getlist('plataformas')

        if email and password:
            base = email.split('@')[0]
            username = base
            n = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f'{base}{n}'; n += 1
            user = CustomUser.objects.create_user(
                username=username, email=email, password=password,
                first_name=first_name, last_name=last_name, rol=CustomUser.ADMIN,
            )
            for plat_id in plats:
                if plat_id.isdigit():
                    try:
                        user.plataformas_asignadas.add(Platform.objects.get(pk=int(plat_id)))
                    except Platform.DoesNotExist:
                        pass
            messages.success(request, f'Admin {email} creado correctamente.')
        return redirect('/superadmin/admins/')

    plataformas = Platform.objects.filter(activa=True)
    return render(request, 'superadmin/crear_admin.html', {'plataformas': plataformas})


@superadmin_required
@require_POST
def toggle_admin(request, pk):
    user = get_object_or_404(CustomUser, pk=pk, rol=CustomUser.ADMIN)
    user.is_active = not user.is_active
    user.save()
    hace_30 = timezone.now() - timedelta(days=30)
    reportes_mes = Report.objects.filter(
        plataforma__in=user.plataformas_asignadas.all(),
        creado_en__gte=hace_30,
    ).count()
    return render(request, 'partials/fila_admin_sa.html', {'a': user, 'reportes_mes': reportes_mes})


@superadmin_required
def config_global(request):
    return render(request, 'superadmin/config_global.html')
