from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from apps.accounts.forms import LoginForm, RegisterForm
from apps.accounts.models import User

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
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
            return redirect('/')
        error = 'Credenciales incorrectas'
    return render(request, 'accounts/login.html', {'form': form, 'error': error})

@require_POST
def logout_view(request):
    logout(request)
    return redirect('/login/')

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.rol = User.USUARIO
        user.save()
        return redirect('/login/')
    return render(request, 'accounts/register.html', {'form': form})


from apps.accounts.decorators import role_required

@role_required(User.ADMIN)
def admin_users_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_rol = request.POST.get('rol')
        if new_rol in [User.USUARIO, User.TESTER, User.ADMIN] and user_id:
            User.objects.filter(pk=int(user_id)).update(rol=new_rol)
        return redirect('admin_users')
    users = User.objects.all().order_by('rol', 'email')
    return render(request, 'accounts/admin_users.html', {
        'users': users,
        'rol_choices': User.ROL_CHOICES,
    })
