from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from apps.accounts.forms import LoginForm, RegisterForm
from apps.accounts.models import CustomUser
from apps.accounts.decorators import admin_required


def _redirect_by_role(user):
    if user.rol == CustomUser.SUPERADMIN:
        return redirect('/superadmin/dashboard/')
    if user.rol == CustomUser.ADMIN:
        return redirect('/admin/resumen/')
    return redirect('/reportes/')


def login_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)
    form = LoginForm(request.POST or None)
    error = None
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            return _redirect_by_role(user)
        error = 'Credenciales incorrectas. Verifica tu correo y contraseña.'
    return render(request, 'accounts/login.html', {'form': form, 'error': error})


@require_POST
def logout_view(request):
    logout(request)
    return redirect('/login/')


def registro_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.rol = CustomUser.USUARIO
        user.save()
        messages.success(request, 'Cuenta creada. Inicia sesión para continuar.')
        return redirect('/login/')
    return render(request, 'accounts/registro.html', {'form': form})


def home_view(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return _redirect_by_role(request.user)


# ─── ADMIN USER MANAGEMENT ─────────────────────────────────────────────────

@admin_required
def usuarios_admin(request):
    ids      = list(request.user.plataformas_asignadas.values_list('id', flat=True))
    qs       = CustomUser.objects.filter(
        plataformas_asignadas__in=ids,
        rol__in=[CustomUser.TESTER, CustomUser.USUARIO],
    ).distinct().order_by('rol', 'email')
    rol    = request.GET.get('rol', '')
    estado = request.GET.get('estado', '')
    q      = request.GET.get('q', '').strip()
    if rol:    qs = qs.filter(rol=rol)
    if estado == 'activo':   qs = qs.filter(is_active=True)
    if estado == 'inactivo': qs = qs.filter(is_active=False)
    if q:      qs = qs.filter(email__icontains=q)
    from apps.platforms.models import Platform
    return render(request, 'platforms/usuarios_admin.html', {
        'usuarios':         qs,
        'rol_choices':      [(CustomUser.TESTER, 'Tester'), (CustomUser.USUARIO, 'Usuario')],
        'admin_plataformas': Platform.objects.filter(id__in=ids),
    })


@admin_required
@require_POST
def cambiar_rol(request, pk):
    ids  = list(request.user.plataformas_asignadas.values_list('id', flat=True))
    user = get_object_or_404(CustomUser, pk=pk)
    if not user.plataformas_asignadas.filter(id__in=ids).exists():
        return HttpResponseForbidden()

    if request.POST.get('desactivar'):
        user.is_active = False
        user.save()
    else:
        nuevo_rol = request.POST.get('rol', '')
        if nuevo_rol in (CustomUser.TESTER, CustomUser.USUARIO):
            user.rol = nuevo_rol
            user.save()
            # Al promover a Tester, asignar las plataformas del admin si aún no tiene ninguna
            if nuevo_rol == CustomUser.TESTER and not user.plataformas_asignadas.exists():
                from apps.platforms.models import Platform
                for pid in ids:
                    try:
                        user.plataformas_asignadas.add(Platform.objects.get(pk=pid))
                    except Platform.DoesNotExist:
                        pass

    from apps.platforms.models import Platform
    admin_plataformas = Platform.objects.filter(id__in=ids)
    return render(request, 'partials/fila_usuario_admin.html', {'u': user, 'admin_plataformas': admin_plataformas})
