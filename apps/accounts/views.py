from datetime import datetime, time
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.views.decorators.http import require_POST

from django.http import HttpResponseForbidden

from django.core.mail import send_mail

from django.template.loader import render_to_string

from django.conf import settings

from apps.accounts.forms import LoginForm, RegisterForm

from apps.accounts.models import CustomUser, EmailVerification

from apps.accounts.decorators import admin_required





def _redirect_by_role(user):

    if user.rol == CustomUser.SUPERADMIN:

        return redirect('/superadmin/dashboard/')

    if user.rol == CustomUser.ADMIN:

        return redirect('/admin/resumen/')

    return redirect('/reportes/')





def _enviar_codigo(user, verificacion):

    html = render_to_string('accounts/email_verificacion.html', {

        'user': user,

        'code': verificacion.code,

        'expiry': EmailVerification.EXPIRY_MINUTES,

    })

    send_mail(

        subject='Tu cÃ³digo de verificaciÃ³n â€” FeedBackStarpath',

        message=f'Tu cÃ³digo de verificaciÃ³n es: {verificacion.code}. VÃ¡lido por {EmailVerification.EXPIRY_MINUTES} minutos.',

        from_email=settings.DEFAULT_FROM_EMAIL,

        recipient_list=[user.email],

        html_message=html,

        fail_silently=False,

    )





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

        error = 'Credenciales incorrectas. Verifica tu correo y contraseÃ±a.'

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

        messages.success(request, 'Cuenta creada. Inicia sesiÃ³n para continuar.')

        return redirect('/login/')

    return render(request, 'accounts/registro.html', {'form': form})





def verificar_correo_view(request):

    user_id = request.session.get('verificar_user_id')

    if not user_id:

        return redirect('/registro/')



    user = get_object_or_404(CustomUser, pk=user_id, is_active=False)

    verificacion = EmailVerification.objects.filter(

        user=user, usado=False

    ).order_by('-created_at').first()



    error = None



    if request.method == 'POST':

        accion = request.POST.get('accion', 'verificar')



        if accion == 'reenviar':

            try:

                nueva = EmailVerification.crear_para(user)

                _enviar_codigo(user, nueva)

                messages.success(request, f'Nuevo cÃ³digo enviado a {user.email}.')

            except Exception as e:

                error = f'No se pudo reenviar el correo: {e}'

            return render(request, 'accounts/verificar_correo.html', {

                'email': user.email, 'error': error,

            })



        codigo = request.POST.get('codigo', '').strip()

        if not verificacion:

            error = 'No hay un cÃ³digo activo. Solicita uno nuevo.'

        else:

            ok, motivo = verificacion.verificar(codigo)

            if ok:

                user.is_active = True

                user.save()

                del request.session['verificar_user_id']

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                messages.success(request, f'Â¡Bienvenido {user.first_name or user.email}! Tu cuenta ha sido verificada.')

                return _redirect_by_role(user)

            elif motivo == 'expirado':

                error = 'El cÃ³digo ha expirado. Solicita uno nuevo.'

            elif motivo.startswith('incorrecto'):

                restantes = motivo.split(':')[1]

                error = f'CÃ³digo incorrecto. Te quedan {restantes} intento(s).'

                if int(restantes) <= 0:

                    error = 'Demasiados intentos fallidos. Solicita un nuevo cÃ³digo.'



    expirado = verificacion.expirado if verificacion else True

    return render(request, 'accounts/verificar_correo.html', {

        'email':    user.email,

        'error':    error,

        'expirado': expirado,

    })





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
    desde  = request.GET.get('desde', '').strip()
    hasta  = request.GET.get('hasta', '').strip()
    if rol:    qs = qs.filter(rol=rol)
    if estado == 'activo':   qs = qs.filter(is_active=True)
    if estado == 'inactivo': qs = qs.filter(is_active=False)
    if q:      qs = qs.filter(email__icontains=q)
    if desde:
        desde_dt = timezone.make_aware(datetime.combine(datetime.strptime(desde, '%Y-%m-%d'), time.min))
        qs = qs.filter(date_joined__gte=desde_dt)
    if hasta:
        hasta_dt = timezone.make_aware(datetime.combine(datetime.strptime(hasta, '%Y-%m-%d'), time.max))
        qs = qs.filter(date_joined__lte=hasta_dt)
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


# ─── EXPORTAR USUARIOS EN PDF ──────────────────────────────────────────────


@admin_required
def exportar_usuarios_pdf(request):
    from weasyprint import HTML
    from django.http import HttpResponse
    from django.utils import timezone

    ids = list(request.user.plataformas_asignadas.values_list('id', flat=True))
    qs = CustomUser.objects.filter(
        plataformas_asignadas__in=ids,
        rol__in=[CustomUser.TESTER, CustomUser.USUARIO],
    ).distinct().order_by('rol', 'email')

    rol    = request.GET.get('rol', '')
    estado = request.GET.get('estado', '')
    q      = request.GET.get('q', '').strip()
    desde  = request.GET.get('desde', '').strip()
    hasta  = request.GET.get('hasta', '').strip()
    if rol:    qs = qs.filter(rol=rol)
    if estado == 'activo':   qs = qs.filter(is_active=True)
    if estado == 'inactivo': qs = qs.filter(is_active=False)
    if q:      qs = qs.filter(email__icontains=q)
    if desde:
        desde_dt = timezone.make_aware(datetime.combine(datetime.strptime(desde, '%Y-%m-%d'), time.min))
        qs = qs.filter(date_joined__gte=desde_dt)
    if hasta:
        hasta_dt = timezone.make_aware(datetime.combine(datetime.strptime(hasta, '%Y-%m-%d'), time.max))
        qs = qs.filter(date_joined__lte=hasta_dt)

    total = qs.count()
    total_testers  = qs.filter(rol=CustomUser.TESTER).count()
    total_usuarios = qs.filter(rol=CustomUser.USUARIO).count()
    total_activos   = qs.filter(is_active=True).count()
    total_inactivos = qs.filter(is_active=False).count()

    def pct(n):
        return round((n / total * 100), 1) if total else 0

    # --- Gráfica de dona (rol): stroke-dasharray sobre circunferencia de r=40 ---
    circunferencia = 2 * 3.14159265 * 40  # ≈ 251.33
    testers_len  = circunferencia * (total_testers / total) if total else 0
    usuarios_len = circunferencia - testers_len

    # --- Gráfica de barras (estado): alturas proporcionales, máx 100px ---
    max_barra = 100
    max_val = max(total_activos, total_inactivos, 1)
    barra_activos_h   = round((total_activos / max_val) * max_barra, 1)
    barra_inactivos_h = round((total_inactivos / max_val) * max_barra, 1)
    barra_activos_y   = round(110 - barra_activos_h, 1)
    barra_inactivos_y = round(110 - barra_inactivos_h, 1)

    try:
        html_string = render_to_string('pdf/usuarios_pdf.html', {
            'usuarios': qs,
            'admin': request.user,
            'fecha_generacion': timezone.now(),
            'resumen': {
                'total':            total,
                'total_testers':    total_testers,
                'total_usuarios':   total_usuarios,
                'total_activos':    total_activos,
                'total_inactivos':  total_inactivos,
                'pct_testers':      pct(total_testers),
                'pct_usuarios':     pct(total_usuarios),
                'pct_activos':      pct(total_activos),
                'pct_inactivos':    pct(total_inactivos),
            },
            'dona': {
                'circunferencia':  circunferencia,
                'testers_len':     round(testers_len, 2),
                'usuarios_len':    round(usuarios_len, 2),
            },
            'barras': {
                'activos_h':   barra_activos_h,
                'inactivos_h': barra_inactivos_h,
                'activos_y':   barra_activos_y,
                'inactivos_y': barra_inactivos_y,
            },
        })
        pdf_file = HTML(string=html_string).write_pdf()
    except Exception as e:
        return HttpResponse(f"Error generando PDF: {e}", status=500)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="usuarios_starpath.pdf"'
    return response
