from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.rol not in roles:
                return HttpResponseForbidden('Acceso denegado.')
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
