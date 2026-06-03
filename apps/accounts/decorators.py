from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.conf import settings


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")
            if request.user.rol not in roles:
                return HttpResponseForbidden('Acceso denegado.')
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def superadmin_required(view_func):
    from apps.accounts.models import CustomUser
    return role_required(CustomUser.SUPERADMIN)(view_func)


def admin_required(view_func):
    from apps.accounts.models import CustomUser
    return role_required(CustomUser.ADMIN, CustomUser.SUPERADMIN)(view_func)


def tester_required(view_func):
    from apps.accounts.models import CustomUser
    return role_required(CustomUser.TESTER, CustomUser.ADMIN, CustomUser.SUPERADMIN)(view_func)
