# FeedbackEve Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a unified bug and feedback portal for multiple company platforms (EVE 360, Medical, Órbita, etc.) using Django 5 + MySQL + HTMX + TailwindCSS + WeasyPrint.

**Architecture:** Django MVT monolith with 4 apps (accounts, platforms, reports, exports). HTMX handles dynamic table filtering and modals without a separate frontend. PDFs are generated server-side with WeasyPrint.

**Tech Stack:** Python 3.12, Django 5.1, MySQL 8, HTMX 1.9 (CDN), Alpine.js 3 (CDN), TailwindCSS (CDN), WeasyPrint 62, Pillow 10

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `config/settings.py`
- Create: `config/urls.py`
- Create: `.env`
- Create: `.gitignore`

- [ ] **Step 1: Create virtual environment**

```bash
cd C:\Users\HUAWEI\Desktop\FedbackEve
python -m venv venv
venv\Scripts\activate
```

- [ ] **Step 2: Create requirements.txt and install**

```
Django==5.1
mysqlclient==2.2.6
weasyprint==62.3
Pillow==10.4.0
python-dotenv==1.0.1
```

```bash
pip install -r requirements.txt
```

- [ ] **Step 3: Create Django project and apps**

```bash
django-admin startproject config .
python manage.py startapp accounts
python manage.py startapp platforms
python manage.py startapp reports
python manage.py startapp exports
mkdir templates static media
```

Move each app into an `apps/` folder:
```bash
mkdir apps
move accounts apps\
move platforms apps\
move reports apps\
move exports apps\
```

Create `apps/__init__.py` (empty file).

- [ ] **Step 4: Create .env**

```
SECRET_KEY=cambia-esto-en-produccion-usa-algo-aleatorio
DEBUG=True
DB_NAME=feedbackeve
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
```

- [ ] **Step 5: Configure config/settings.py**

```python
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.accounts',
    'apps.platforms',
    'apps.reports',
    'apps.exports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'feedbackeve'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

- [ ] **Step 6: Configure config/urls.py**

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('', include('apps.platforms.urls')),
    path('', include('apps.reports.urls')),
    path('', include('apps.exports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

- [ ] **Step 7: Create empty urls.py for each app**

`apps/accounts/urls.py`, `apps/platforms/urls.py`, `apps/reports/urls.py`, `apps/exports/urls.py` — all with:
```python
from django.urls import path
urlpatterns = []
```

- [ ] **Step 8: Create MySQL database**

```sql
CREATE DATABASE feedbackeve CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

- [ ] **Step 9: Create .gitignore**

```
venv/
.env
__pycache__/
*.pyc
media/
db.sqlite3
```

- [ ] **Step 10: Verify**

```bash
python manage.py check
```
Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 11: Commit**

```bash
git add requirements.txt config/ apps/ templates/ static/ .gitignore
git commit -m "chore: initial Django project setup"
```

---

### Task 2: CustomUser Model

**Files:**
- Create/Modify: `apps/accounts/models.py`
- Create: `apps/accounts/tests.py`

- [ ] **Step 1: Write failing test**

`apps/accounts/tests.py`:
```python
from django.test import TestCase
from apps.accounts.models import User

class UserModelTest(TestCase):
    def test_create_user_with_rol(self):
        user = User.objects.create_user(
            username='tester1',
            email='tester@example.com',
            password='pass1234',
            rol=User.TESTER,
        )
        self.assertEqual(user.rol, User.TESTER)
        self.assertEqual(user.email, 'tester@example.com')

    def test_default_rol_is_usuario(self):
        user = User.objects.create_user(username='u1', password='pass1234')
        self.assertEqual(user.rol, User.USUARIO)

    def test_is_admin_property(self):
        admin = User.objects.create_user(username='adm', password='p', rol=User.ADMIN)
        self.assertTrue(admin.is_admin)
        self.assertFalse(admin.is_tester)

    def test_is_tester_property(self):
        tester = User.objects.create_user(username='tst', password='p', rol=User.TESTER)
        self.assertTrue(tester.is_tester)
        self.assertFalse(tester.is_admin)
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
python manage.py test apps.accounts.tests.UserModelTest -v 2
```
Expected: `ImportError` or `AttributeError` — model doesn't exist yet.

- [ ] **Step 3: Implement User model**

`apps/accounts/models.py`:
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USUARIO = 'USUARIO'
    TESTER  = 'TESTER'
    ADMIN   = 'ADMIN'
    ROL_CHOICES = [
        (USUARIO, 'Usuario'),
        (TESTER,  'Tester'),
        (ADMIN,   'Admin'),
    ]

    email = models.EmailField(unique=True)
    rol   = models.CharField(max_length=10, choices=ROL_CHOICES, default=USUARIO)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def is_admin(self):
        return self.rol == self.ADMIN

    @property
    def is_tester(self):
        return self.rol == self.TESTER

    @property
    def is_usuario(self):
        return self.rol == self.USUARIO

    def __str__(self):
        return self.email
```

- [ ] **Step 4: Create and run migrations**

```bash
python manage.py makemigrations accounts
python manage.py migrate
```
Expected: migrations applied, no errors.

- [ ] **Step 5: Run tests — expect PASS**

```bash
python manage.py test apps.accounts.tests.UserModelTest -v 2
```
Expected: `4 tests OK`

- [ ] **Step 6: Commit**

```bash
git add apps/accounts/models.py apps/accounts/tests.py apps/accounts/migrations/
git commit -m "feat: add CustomUser model with rol field"
```

---

### Task 3: Login, Register, Logout

**Files:**
- Create: `apps/accounts/forms.py`
- Modify: `apps/accounts/views.py`
- Modify: `apps/accounts/urls.py`
- Create: `templates/accounts/login.html`
- Create: `templates/accounts/register.html`
- Modify: `apps/accounts/tests.py`

- [ ] **Step 1: Write failing tests**

Add to `apps/accounts/tests.py`:
```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User

class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='gustavo',
            email='gustavo@test.com',
            password='testpass123',
        )

    def test_login_page_loads(self):
        r = self.client.get(reverse('login'))
        self.assertEqual(r.status_code, 200)

    def test_login_with_valid_credentials(self):
        r = self.client.post(reverse('login'), {
            'email': 'gustavo@test.com',
            'password': 'testpass123',
        })
        self.assertRedirects(r, '/')

    def test_login_with_wrong_password(self):
        r = self.client.post(reverse('login'), {
            'email': 'gustavo@test.com',
            'password': 'wrong',
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Credenciales incorrectas')

    def test_register_creates_user_as_usuario(self):
        r = self.client.post(reverse('register'), {
            'username': 'nuevo',
            'email': 'nuevo@test.com',
            'password1': 'Seguro123!',
            'password2': 'Seguro123!',
        })
        self.assertRedirects(r, '/login/')
        u = User.objects.get(email='nuevo@test.com')
        self.assertEqual(u.rol, User.USUARIO)

    def test_logout_redirects(self):
        self.client.login(username='gustavo@test.com', password='testpass123')
        r = self.client.post(reverse('logout'))
        self.assertRedirects(r, '/login/')
```

- [ ] **Step 2: Run — expect FAIL**

```bash
python manage.py test apps.accounts.tests.AuthViewsTest -v 2
```
Expected: `NoReverseMatch` — URLs not defined yet.

- [ ] **Step 3: Create forms**

`apps/accounts/forms.py`:
```python
from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.accounts.models import User

class LoginForm(forms.Form):
    email    = forms.EmailField(label='Correo electrónico')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model  = User
        fields = ('username', 'email', 'password1', 'password2')
```

- [ ] **Step 4: Create views**

`apps/accounts/views.py`:
```python
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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
```

- [ ] **Step 5: Create urls**

`apps/accounts/urls.py`:
```python
from django.urls import path
from apps.accounts import views

urlpatterns = [
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('registro/', views.register_view, name='register'),
]
```

- [ ] **Step 6: Create templates/accounts/login.html**

```html
{% extends 'base.html' %}
{% block content %}
<div class="min-h-screen flex items-center justify-center bg-[#0a1628]">
  <div class="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
    <div class="text-center mb-8">
      <h1 class="text-2xl font-bold text-[#0a1628]">Feedback<span class="text-sky-500">Eve</span></h1>
      <p class="text-slate-500 text-sm mt-1">Portal de Calidad e Incidencias</p>
    </div>
    {% if error %}
      <p class="bg-red-50 text-red-600 text-sm p-3 rounded-lg mb-4 border border-red-200">{{ error }}</p>
    {% endif %}
    <form method="post">
      {% csrf_token %}
      <div class="mb-4">
        <label class="block text-sm font-medium text-slate-700 mb-1">Correo electrónico</label>
        <input name="email" type="email" required
          class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400">
      </div>
      <div class="mb-6">
        <label class="block text-sm font-medium text-slate-700 mb-1">Contraseña</label>
        <input name="password" type="password" required
          class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400">
      </div>
      <button type="submit"
        class="w-full bg-[#0a1628] text-white font-semibold py-2.5 rounded-lg hover:bg-[#162d5a] transition">
        Iniciar sesión
      </button>
    </form>
    <p class="text-center text-sm text-slate-500 mt-4">
      ¿No tienes cuenta? <a href="{% url 'register' %}" class="text-sky-500 hover:underline">Regístrate</a>
    </p>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 7: Create templates/accounts/register.html**

```html
{% extends 'base.html' %}
{% block content %}
<div class="min-h-screen flex items-center justify-center bg-[#0a1628]">
  <div class="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
    <h1 class="text-xl font-bold text-[#0a1628] mb-1">Crear cuenta</h1>
    <p class="text-slate-500 text-sm mb-6">Tu cuenta tendrá rol de Usuario básico.</p>
    <form method="post">
      {% csrf_token %}
      {% for field in form %}
        <div class="mb-4">
          <label class="block text-sm font-medium text-slate-700 mb-1">{{ field.label }}</label>
          <input name="{{ field.html_name }}" type="{{ field.field.widget.input_type }}"
            class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400">
          {% if field.errors %}
            <p class="text-red-500 text-xs mt-1">{{ field.errors|join:", " }}</p>
          {% endif %}
        </div>
      {% endfor %}
      <button type="submit"
        class="w-full bg-[#0a1628] text-white font-semibold py-2.5 rounded-lg hover:bg-[#162d5a] transition">
        Registrarse
      </button>
    </form>
    <p class="text-center text-sm text-slate-500 mt-4">
      ¿Ya tienes cuenta? <a href="{% url 'login' %}" class="text-sky-500 hover:underline">Iniciar sesión</a>
    </p>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 8: Create templates/base.html**

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FeedbackEve</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="bg-[#f0f4f8] text-slate-900">
  {% block content %}{% endblock %}
</body>
</html>
```

- [ ] **Step 9: Run tests — expect PASS**

```bash
python manage.py test apps.accounts.tests -v 2
```
Expected: `7 tests OK`

- [ ] **Step 10: Commit**

```bash
git add apps/accounts/ templates/accounts/ templates/base.html
git commit -m "feat: add login, register, logout with CustomUser"
```

---

### Task 4: Role Decorator + Admin User Management

**Files:**
- Create: `apps/accounts/decorators.py`
- Modify: `apps/accounts/views.py`
- Modify: `apps/accounts/urls.py`
- Create: `templates/accounts/admin_users.html`
- Modify: `apps/accounts/tests.py`

- [ ] **Step 1: Write failing tests**

Add to `apps/accounts/tests.py`:
```python
class RoleDecoratorTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = User.objects.create_user(
            username='u', email='u@t.com', password='pass', rol=User.USUARIO)
        self.admin = User.objects.create_user(
            username='a', email='a@t.com', password='pass', rol=User.ADMIN)

    def test_admin_only_view_blocks_usuario(self):
        self.client.force_login(self.usuario)
        r = self.client.get(reverse('admin_users'))
        self.assertEqual(r.status_code, 403)

    def test_admin_only_view_allows_admin(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse('admin_users'))
        self.assertEqual(r.status_code, 200)
```

- [ ] **Step 2: Run — expect FAIL**

```bash
python manage.py test apps.accounts.tests.RoleDecoratorTest -v 2
```
Expected: `NoReverseMatch`

- [ ] **Step 3: Create decorator**

`apps/accounts/decorators.py`:
```python
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
```

- [ ] **Step 4: Add admin_users view**

Add to `apps/accounts/views.py`:
```python
from apps.accounts.decorators import role_required

@role_required(User.ADMIN)
def admin_users_view(request):
    users = User.objects.all().order_by('rol', 'email')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_rol = request.POST.get('rol')
        if new_rol in [User.USUARIO, User.TESTER, User.ADMIN]:
            User.objects.filter(pk=user_id).update(rol=new_rol)
    return render(request, 'accounts/admin_users.html', {
        'users': users,
        'rol_choices': User.ROL_CHOICES,
    })
```

- [ ] **Step 5: Add URL**

`apps/accounts/urls.py`:
```python
from django.urls import path
from apps.accounts import views

urlpatterns = [
    path('login/',         views.login_view,       name='login'),
    path('logout/',        views.logout_view,       name='logout'),
    path('registro/',      views.register_view,     name='register'),
    path('admin/usuarios/',views.admin_users_view,  name='admin_users'),
]
```

- [ ] **Step 6: Create templates/accounts/admin_users.html**

```html
{% extends 'dashboard_base.html' %}
{% block page_title %}Gestión de Usuarios{% endblock %}
{% block main_content %}
<div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
  <table class="w-full">
    <thead class="bg-slate-50 text-xs font-bold text-slate-500 uppercase tracking-wide">
      <tr>
        <th class="px-4 py-3 text-left">Usuario</th>
        <th class="px-4 py-3 text-left">Email</th>
        <th class="px-4 py-3 text-left">Rol actual</th>
        <th class="px-4 py-3 text-left">Cambiar rol</th>
      </tr>
    </thead>
    <tbody>
      {% for u in users %}
      <tr class="border-t border-slate-100 hover:bg-slate-50">
        <td class="px-4 py-3 font-medium">{{ u.username }}</td>
        <td class="px-4 py-3 text-slate-500">{{ u.email }}</td>
        <td class="px-4 py-3">
          <span class="text-xs font-semibold px-2 py-1 rounded
            {% if u.rol == 'ADMIN' %}bg-sky-100 text-sky-700
            {% elif u.rol == 'TESTER' %}bg-purple-100 text-purple-700
            {% else %}bg-slate-100 text-slate-600{% endif %}">
            {{ u.get_rol_display }}
          </span>
        </td>
        <td class="px-4 py-3">
          <form method="post">
            {% csrf_token %}
            <input type="hidden" name="user_id" value="{{ u.pk }}">
            <select name="rol" onchange="this.form.submit()"
              class="text-xs border border-slate-300 rounded px-2 py-1">
              {% for val, label in rol_choices %}
                <option value="{{ val }}" {% if u.rol == val %}selected{% endif %}>{{ label }}</option>
              {% endfor %}
            </select>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

- [ ] **Step 7: Run tests — expect PASS**

```bash
python manage.py test apps.accounts.tests -v 2
```
Expected: `9 tests OK`

- [ ] **Step 8: Commit**

```bash
git add apps/accounts/ templates/accounts/admin_users.html
git commit -m "feat: add role decorator and admin user management"
```

---

### Task 5: Platform Model + Admin CRUD

**Files:**
- Create: `apps/platforms/models.py`
- Create: `apps/platforms/forms.py`
- Create: `apps/platforms/views.py`
- Modify: `apps/platforms/urls.py`
- Create: `apps/platforms/tests.py`
- Create: `templates/platforms/admin_platforms.html`

- [ ] **Step 1: Write failing tests**

`apps/platforms/tests.py`:
```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.platforms.models import Platform

class PlatformModelTest(TestCase):
    def test_create_platform(self):
        p = Platform.objects.create(nombre='EVE 360', color='#0ea5e9')
        self.assertEqual(str(p), 'EVE 360')
        self.assertTrue(p.activa)

class PlatformCRUDTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='adm', email='adm@t.com', password='p', rol=User.ADMIN)
        self.client.force_login(self.admin)

    def test_list_platforms(self):
        Platform.objects.create(nombre='EVE 360', color='#0ea5e9')
        r = self.client.get(reverse('admin_platforms'))
        self.assertContains(r, 'EVE 360')

    def test_create_platform_post(self):
        r = self.client.post(reverse('admin_platforms'), {
            'nombre': 'Medical', 'color': '#a855f7', 'descripcion': 'Consultorio',
        })
        self.assertEqual(Platform.objects.filter(nombre='Medical').count(), 1)

    def test_toggle_platform_active(self):
        p = Platform.objects.create(nombre='Órbita', color='#f97316', activa=True)
        self.client.post(reverse('platform_toggle', args=[p.pk]))
        p.refresh_from_db()
        self.assertFalse(p.activa)
```

- [ ] **Step 2: Run — expect FAIL**

```bash
python manage.py test apps.platforms.tests -v 2
```
Expected: `ImportError` — Platform model doesn't exist.

- [ ] **Step 3: Create Platform model**

`apps/platforms/models.py`:
```python
from django.db import models

class Platform(models.Model):
    nombre      = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    color       = models.CharField(max_length=7, default='#0ea5e9')
    activa      = models.BooleanField(default=True)
    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
```

- [ ] **Step 4: Create form**

`apps/platforms/forms.py`:
```python
from django import forms
from apps.platforms.models import Platform

class PlatformForm(forms.ModelForm):
    class Meta:
        model  = Platform
        fields = ['nombre', 'descripcion', 'color']
```

- [ ] **Step 5: Create views**

`apps/platforms/views.py`:
```python
from django.shortcuts import render, get_object_or_404, redirect
from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.platforms.forms import PlatformForm

@role_required(User.ADMIN)
def admin_platforms_view(request):
    form = PlatformForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_platforms')
    platforms = Platform.objects.all()
    return render(request, 'platforms/admin_platforms.html', {
        'platforms': platforms, 'form': form,
    })

@role_required(User.ADMIN)
def platform_toggle_view(request, pk):
    p = get_object_or_404(Platform, pk=pk)
    p.activa = not p.activa
    p.save()
    return redirect('admin_platforms')

@role_required(User.ADMIN)
def platform_delete_view(request, pk):
    get_object_or_404(Platform, pk=pk).delete()
    return redirect('admin_platforms')
```

- [ ] **Step 6: Create URLs**

`apps/platforms/urls.py`:
```python
from django.urls import path
from apps.platforms import views

urlpatterns = [
    path('admin/plataformas/',         views.admin_platforms_view, name='admin_platforms'),
    path('admin/plataformas/<int:pk>/toggle/', views.platform_toggle_view, name='platform_toggle'),
    path('admin/plataformas/<int:pk>/delete/', views.platform_delete_view, name='platform_delete'),
]
```

- [ ] **Step 7: Migrations**

```bash
python manage.py makemigrations platforms
python manage.py migrate
```

- [ ] **Step 8: Create templates/platforms/admin_platforms.html**

```html
{% extends 'dashboard_base.html' %}
{% block page_title %}Plataformas{% endblock %}
{% block main_content %}
<div class="grid grid-cols-3 gap-6">
  <!-- Form -->
  <div class="col-span-1 bg-white rounded-xl border border-slate-200 p-6">
    <h3 class="font-semibold mb-4">Nueva plataforma</h3>
    <form method="post">
      {% csrf_token %}
      <div class="mb-3">
        <label class="text-sm font-medium text-slate-700">Nombre</label>
        <input name="nombre" type="text" required
          class="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-sky-400 outline-none">
      </div>
      <div class="mb-3">
        <label class="text-sm font-medium text-slate-700">Descripción</label>
        <textarea name="descripcion" rows="2"
          class="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-sky-400 outline-none"></textarea>
      </div>
      <div class="mb-4">
        <label class="text-sm font-medium text-slate-700">Color</label>
        <input name="color" type="color" value="#0ea5e9"
          class="mt-1 h-9 w-full border border-slate-300 rounded-lg cursor-pointer">
      </div>
      <button type="submit"
        class="w-full bg-[#0a1628] text-white font-semibold py-2 rounded-lg hover:bg-[#162d5a] transition text-sm">
        Agregar
      </button>
    </form>
  </div>
  <!-- List -->
  <div class="col-span-2 bg-white rounded-xl border border-slate-200 overflow-hidden">
    <table class="w-full">
      <thead class="bg-slate-50 text-xs font-bold text-slate-500 uppercase tracking-wide">
        <tr>
          <th class="px-4 py-3 text-left">Plataforma</th>
          <th class="px-4 py-3 text-left">Descripción</th>
          <th class="px-4 py-3 text-left">Estado</th>
          <th class="px-4 py-3 text-left">Acciones</th>
        </tr>
      </thead>
      <tbody>
        {% for p in platforms %}
        <tr class="border-t border-slate-100 hover:bg-slate-50">
          <td class="px-4 py-3 font-medium flex items-center gap-2">
            <span class="w-3 h-3 rounded-full inline-block" style="background:{{ p.color }}"></span>
            {{ p.nombre }}
          </td>
          <td class="px-4 py-3 text-sm text-slate-500">{{ p.descripcion|default:"—" }}</td>
          <td class="px-4 py-3">
            <span class="text-xs font-semibold px-2 py-1 rounded
              {% if p.activa %}bg-green-100 text-green-700{% else %}bg-slate-100 text-slate-500{% endif %}">
              {% if p.activa %}Activa{% else %}Inactiva{% endif %}
            </span>
          </td>
          <td class="px-4 py-3 flex gap-2">
            <a href="{% url 'platform_toggle' p.pk %}"
              class="text-xs text-sky-600 hover:underline">
              {% if p.activa %}Desactivar{% else %}Activar{% endif %}
            </a>
            <a href="{% url 'platform_delete' p.pk %}"
              class="text-xs text-red-500 hover:underline"
              onclick="return confirm('¿Eliminar {{ p.nombre }}?')">Eliminar</a>
          </td>
        </tr>
        {% empty %}
        <tr><td colspan="4" class="px-4 py-6 text-center text-slate-400 text-sm">Sin plataformas registradas</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 9: Run tests — expect PASS**

```bash
python manage.py test apps.platforms.tests -v 2
```
Expected: `4 tests OK`

- [ ] **Step 10: Commit**

```bash
git add apps/platforms/ templates/platforms/
git commit -m "feat: add Platform model and admin CRUD"
```

---

### Task 6: Report, Screenshot, StatusHistory Models

**Files:**
- Create: `apps/reports/models.py`
- Create: `apps/reports/tests.py`

- [ ] **Step 1: Write failing tests**

`apps/reports/tests.py`:
```python
from django.test import TestCase
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.reports.models import Report, Screenshot, StatusHistory

class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='u', email='u@t.com', password='p')
        self.platform = Platform.objects.create(nombre='EVE 360', color='#0ea5e9')

    def test_create_report(self):
        r = Report.objects.create(
            titulo='Error en login',
            descripcion='No redirige',
            plataforma=self.platform,
            tipo=Report.BUG,
            severidad=Report.CRITICA,
            reportado_por=self.user,
        )
        self.assertEqual(r.estado, Report.ABIERTO)
        self.assertEqual(str(r), 'Error en login')

    def test_status_history_on_change(self):
        report = Report.objects.create(
            titulo='T', descripcion='D', plataforma=self.platform,
            tipo=Report.BUG, severidad=Report.ALTA, reportado_por=self.user,
        )
        report.cambiar_estado(Report.EN_REVISION, self.user)
        self.assertEqual(report.estado, Report.EN_REVISION)
        h = StatusHistory.objects.get(reporte=report)
        self.assertEqual(h.estado_anterior, Report.ABIERTO)
        self.assertEqual(h.estado_nuevo, Report.EN_REVISION)
```

- [ ] **Step 2: Run — expect FAIL**

```bash
python manage.py test apps.reports.tests.ReportModelTest -v 2
```
Expected: `ImportError`

- [ ] **Step 3: Implement models**

`apps/reports/models.py`:
```python
from django.db import models
from django.conf import settings

class Report(models.Model):
    BUG       = 'BUG'
    SUGERENCIA = 'SUGERENCIA'
    QUEJA     = 'QUEJA'
    TIPO_CHOICES = [(BUG,'Bug'),(SUGERENCIA,'Sugerencia'),(QUEJA,'Queja')]

    BAJA   = 'BAJA'
    MEDIA  = 'MEDIA'
    ALTA   = 'ALTA'
    CRITICA = 'CRITICA'
    SEV_CHOICES = [(BAJA,'Baja'),(MEDIA,'Media'),(ALTA,'Alta'),(CRITICA,'Crítica')]

    ABIERTO     = 'ABIERTO'
    EN_REVISION = 'EN_REVISION'
    RESUELTO    = 'RESUELTO'
    CERRADO     = 'CERRADO'
    ESTADO_CHOICES = [
        (ABIERTO,'Abierto'),(EN_REVISION,'En revisión'),
        (RESUELTO,'Resuelto'),(CERRADO,'Cerrado'),
    ]

    titulo             = models.CharField(max_length=200)
    descripcion        = models.TextField()
    plataforma         = models.ForeignKey('platforms.Platform', on_delete=models.CASCADE)
    tipo               = models.CharField(max_length=15, choices=TIPO_CHOICES)
    severidad          = models.CharField(max_length=10, choices=SEV_CHOICES, default=MEDIA)
    estado             = models.CharField(max_length=15, choices=ESTADO_CHOICES, default=ABIERTO)
    url_pagina         = models.URLField(blank=True)
    pasos_reproducir   = models.TextField(blank=True)
    resultado_esperado = models.TextField(blank=True)
    resultado_obtenido = models.TextField(blank=True)
    entorno            = models.JSONField(default=dict, blank=True)
    reportado_por      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creado_en          = models.DateTimeField(auto_now_add=True)
    actualizado_en     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return self.titulo

    def cambiar_estado(self, nuevo_estado, usuario):
        StatusHistory.objects.create(
            reporte=self,
            estado_anterior=self.estado,
            estado_nuevo=nuevo_estado,
            cambiado_por=usuario,
        )
        self.estado = nuevo_estado
        self.save()

class Screenshot(models.Model):
    reporte    = models.ForeignKey(Report, related_name='screenshots', on_delete=models.CASCADE)
    imagen     = models.ImageField(upload_to='screenshots/')
    subido_en  = models.DateTimeField(auto_now_add=True)

class StatusHistory(models.Model):
    reporte         = models.ForeignKey(Report, related_name='historial', on_delete=models.CASCADE)
    estado_anterior = models.CharField(max_length=15)
    estado_nuevo    = models.CharField(max_length=15)
    cambiado_por    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha           = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
```

- [ ] **Step 4: Migrate**

```bash
python manage.py makemigrations reports
python manage.py migrate
```

- [ ] **Step 5: Run tests — expect PASS**

```bash
python manage.py test apps.reports.tests.ReportModelTest -v 2
```
Expected: `2 tests OK`

- [ ] **Step 6: Commit**

```bash
git add apps/reports/models.py apps/reports/migrations/ apps/reports/tests.py
git commit -m "feat: add Report, Screenshot, StatusHistory models"
```

---

### Task 7: Dashboard Base Template + Navigation

**Files:**
- Create: `templates/dashboard_base.html`
- Create: `templates/partials/sidebar.html`

- [ ] **Step 1: Create templates/dashboard_base.html**

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FeedbackEve — {% block page_title %}{% endblock %}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="bg-[#f0f4f8] text-slate-900 flex flex-col min-h-screen">

  <!-- NAVBAR -->
  <nav class="bg-[#0a1628] h-14 flex items-center px-6 gap-4 sticky top-0 z-50">
    <a href="/" class="text-white font-extrabold text-base tracking-tight mr-8">
      Feedback<span class="text-sky-400">Eve</span>
    </a>
    <a href="/"                 class="nav-link {% block nav_home %}{% endblock %}">Dashboard</a>
    <a href="/reportes/nuevo/"  class="nav-link {% block nav_new %}{% endblock %}">Nuevo Reporte</a>
    {% if user.is_tester or user.is_admin %}
    <a href="/admin/reportes/"  class="nav-link {% block nav_admin_rep %}{% endblock %}">Todos los Reportes</a>
    {% endif %}
    {% if user.is_admin %}
    <a href="/admin/plataformas/" class="nav-link {% block nav_plat %}{% endblock %}">Plataformas</a>
    <a href="/admin/usuarios/"    class="nav-link {% block nav_users %}{% endblock %}">Usuarios</a>
    <a href="/exports/pdf/"       class="nav-link {% block nav_pdf %}{% endblock %}">Exportar PDF</a>
    {% endif %}
    <div class="ml-auto flex items-center gap-3">
      <span class="text-slate-400 text-xs">
        {{ user.email }}
        <span class="ml-1 text-xs font-semibold px-1.5 py-0.5 rounded
          {% if user.is_admin %}bg-sky-900 text-sky-300
          {% elif user.is_tester %}bg-purple-900 text-purple-300
          {% else %}bg-slate-700 text-slate-300{% endif %}">
          {{ user.get_rol_display }}
        </span>
      </span>
      <form method="post" action="{% url 'logout' %}">
        {% csrf_token %}
        <button type="submit" class="text-slate-400 hover:text-white text-xs transition">Salir</button>
      </form>
    </div>
  </nav>

  <!-- MAIN -->
  <main class="flex-1 p-8">
    <h2 class="text-xl font-bold text-slate-800 mb-1">{% block page_title %}{% endblock %}</h2>
    <p class="text-slate-500 text-sm mb-6">{% block page_subtitle %}{% endblock %}</p>
    {% block main_content %}{% endblock %}
  </main>

  <style>
    .nav-link { color: #94a3b8; font-size: 13px; font-weight: 500; padding: 5px 12px; border-radius: 6px; transition: all .15s; }
    .nav-link:hover { color: #fff; background: rgba(255,255,255,0.07); }
    .nav-link.active { color: #fff; background: rgba(255,255,255,0.1); }
  </style>

</body>
</html>
```

- [ ] **Step 2: Update base.html to include CDN scripts**

`templates/base.html` (add Tailwind CDN — already done in Task 3 Step 8, verify it has it).

- [ ] **Step 3: Commit**

```bash
git add templates/dashboard_base.html
git commit -m "feat: add dashboard base template with navbar"
```

---

### Task 8: Dashboard View + HTMX Table

**Files:**
- Create: `apps/reports/views.py`
- Modify: `apps/reports/urls.py`
- Create: `templates/reports/dashboard.html`
- Create: `templates/partials/reports_table.html`
- Modify: `apps/reports/tests.py`

- [ ] **Step 1: Write failing tests**

Add to `apps/reports/tests.py`:
```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.reports.models import Report

class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='u', email='u@t.com', password='p', rol=User.USUARIO)
        self.admin = User.objects.create_user(
            username='a', email='a@t.com', password='p', rol=User.ADMIN)
        self.plat = Platform.objects.create(nombre='EVE 360', color='#0ea5e9')

    def test_dashboard_requires_login(self):
        r = self.client.get(reverse('dashboard'))
        self.assertRedirects(r, '/login/?next=/')

    def test_dashboard_usuario_sees_only_own_reports(self):
        other = User.objects.create_user(username='o', email='o@t.com', password='p')
        Report.objects.create(titulo='Mío', descripcion='d',
            plataforma=self.plat, tipo=Report.BUG, severidad=Report.ALTA,
            reportado_por=self.user)
        Report.objects.create(titulo='Otro', descripcion='d',
            plataforma=self.plat, tipo=Report.BUG, severidad=Report.ALTA,
            reportado_por=other)
        self.client.force_login(self.user)
        r = self.client.get(reverse('dashboard'))
        self.assertContains(r, 'Mío')
        self.assertNotContains(r, 'Otro')

    def test_dashboard_admin_sees_all_reports(self):
        Report.objects.create(titulo='Mío', descripcion='d',
            plataforma=self.plat, tipo=Report.BUG, severidad=Report.ALTA,
            reportado_por=self.user)
        self.client.force_login(self.admin)
        r = self.client.get(reverse('dashboard'))
        self.assertContains(r, 'Mío')

    def test_htmx_filter_by_platform(self):
        plat2 = Platform.objects.create(nombre='Medical', color='#a855f7')
        Report.objects.create(titulo='EVE bug', descripcion='d',
            plataforma=self.plat, tipo=Report.BUG, severidad=Report.ALTA,
            reportado_por=self.admin)
        Report.objects.create(titulo='Medical bug', descripcion='d',
            plataforma=plat2, tipo=Report.BUG, severidad=Report.ALTA,
            reportado_por=self.admin)
        self.client.force_login(self.admin)
        r = self.client.get(
            reverse('reports_table'),
            {'plataforma': self.plat.pk},
            HTTP_HX_REQUEST='true',
        )
        self.assertContains(r, 'EVE bug')
        self.assertNotContains(r, 'Medical bug')
```

- [ ] **Step 2: Run — expect FAIL**

```bash
python manage.py test apps.reports.tests.DashboardViewTest -v 2
```
Expected: `NoReverseMatch`

- [ ] **Step 3: Create views**

`apps/reports/views.py`:
```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.reports.models import Report, StatusHistory

@login_required
def dashboard_view(request):
    reports = _get_filtered_reports(request)
    platforms = Platform.objects.filter(activa=True)
    stats = {
        'total':    Report.objects.count() if not request.user.is_usuario else reports.count(),
        'criticos': reports.filter(severidad=Report.CRITICA, estado=Report.ABIERTO).count(),
        'revision': reports.filter(estado=Report.EN_REVISION).count(),
        'resueltos':reports.filter(estado=Report.RESUELTO).count(),
    }
    return render(request, 'reports/dashboard.html', {
        'reports': reports, 'platforms': platforms, 'stats': stats,
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
```

- [ ] **Step 4: Create URLs**

`apps/reports/urls.py`:
```python
from django.urls import path
from apps.reports import views

urlpatterns = [
    path('',                    views.dashboard_view,        name='dashboard'),
    path('reportes/tabla/',     views.reports_table_partial, name='reports_table'),
    path('reportes/nuevo/',     views.new_report_view,       name='new_report'),
    path('reportes/<int:pk>/',  views.report_detail_view,    name='report_detail'),
    path('admin/reportes/',     views.admin_reports_view,    name='admin_reports'),
    path('reportes/<int:pk>/estado/', views.change_status_view, name='change_status'),
]
```

**Note:** `new_report_view`, `report_detail_view`, `admin_reports_view`, `change_status_view` will be implemented in Tasks 9–10. Add stubs now:

```python
# Stubs — replace in Tasks 9-10
from django.http import HttpResponse
def new_report_view(request):     return HttpResponse('TODO')
def report_detail_view(request, pk): return HttpResponse('TODO')
def admin_reports_view(request):  return HttpResponse('TODO')
def change_status_view(request, pk): return HttpResponse('TODO')
```

- [ ] **Step 5: Create templates/reports/dashboard.html**

```html
{% extends 'dashboard_base.html' %}
{% block page_title %}Dashboard{% endblock %}
{% block page_subtitle %}Resumen de todos los reportes{% endblock %}
{% block nav_home %}active{% endblock %}
{% block main_content %}

<!-- Stats -->
<div class="grid grid-cols-4 gap-4 mb-6">
  <div class="bg-white rounded-xl border border-slate-200 p-5">
    <p class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Total</p>
    <p class="text-3xl font-extrabold text-sky-500">{{ stats.total }}</p>
  </div>
  <div class="bg-white rounded-xl border border-slate-200 p-5">
    <p class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Críticos Abiertos</p>
    <p class="text-3xl font-extrabold text-red-500">{{ stats.criticos }}</p>
  </div>
  <div class="bg-white rounded-xl border border-slate-200 p-5">
    <p class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">En Revisión</p>
    <p class="text-3xl font-extrabold text-yellow-500">{{ stats.revision }}</p>
  </div>
  <div class="bg-white rounded-xl border border-slate-200 p-5">
    <p class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Resueltos</p>
    <p class="text-3xl font-extrabold text-green-500">{{ stats.resueltos }}</p>
  </div>
</div>

<!-- Filters + Table -->
<div class="bg-white rounded-xl border border-slate-200">
  <div class="p-4 border-b border-slate-100 flex flex-wrap items-center gap-3">
    <input type="text" placeholder="Buscar reporte..."
      class="border border-slate-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-sky-400 outline-none"
      hx-get="{% url 'reports_table' %}"
      hx-trigger="keyup changed delay:400ms"
      hx-target="#tabla-reportes"
      hx-include="[name='plataforma'],[name='tipo'],[name='estado'],[name='severidad']"
      name="q">

    <select name="plataforma"
      hx-get="{% url 'reports_table' %}" hx-trigger="change" hx-target="#tabla-reportes"
      hx-include="[name='q'],[name='tipo'],[name='estado'],[name='severidad']"
      class="border border-slate-300 rounded-lg px-3 py-1.5 text-sm outline-none">
      <option value="">Todas las plataformas</option>
      {% for p in platforms %}
        <option value="{{ p.pk }}">{{ p.nombre }}</option>
      {% endfor %}
    </select>

    <select name="tipo"
      hx-get="{% url 'reports_table' %}" hx-trigger="change" hx-target="#tabla-reportes"
      hx-include="[name='q'],[name='plataforma'],[name='estado'],[name='severidad']"
      class="border border-slate-300 rounded-lg px-3 py-1.5 text-sm outline-none">
      <option value="">Todos los tipos</option>
      {% for val, label in tipo_choices %}<option value="{{ val }}">{{ label }}</option>{% endfor %}
    </select>

    <select name="estado"
      hx-get="{% url 'reports_table' %}" hx-trigger="change" hx-target="#tabla-reportes"
      hx-include="[name='q'],[name='plataforma'],[name='tipo'],[name='severidad']"
      class="border border-slate-300 rounded-lg px-3 py-1.5 text-sm outline-none">
      <option value="">Todos los estados</option>
      {% for val, label in estado_choices %}<option value="{{ val }}">{{ label }}</option>{% endfor %}
    </select>

    <select name="severidad"
      hx-get="{% url 'reports_table' %}" hx-trigger="change" hx-target="#tabla-reportes"
      hx-include="[name='q'],[name='plataforma'],[name='tipo'],[name='estado']"
      class="border border-slate-300 rounded-lg px-3 py-1.5 text-sm outline-none">
      <option value="">Toda severidad</option>
      {% for val, label in sev_choices %}<option value="{{ val }}">{{ label }}</option>{% endfor %}
    </select>
  </div>

  <div id="tabla-reportes">
    {% include 'partials/reports_table.html' %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 6: Create templates/partials/reports_table.html**

```html
<table class="w-full">
  <thead class="bg-slate-50 text-xs font-bold text-slate-500 uppercase tracking-wide">
    <tr>
      <th class="px-4 py-3 text-left">ID</th>
      <th class="px-4 py-3 text-left">Título</th>
      <th class="px-4 py-3 text-left">Plataforma</th>
      <th class="px-4 py-3 text-left">Tipo</th>
      <th class="px-4 py-3 text-left">Severidad</th>
      <th class="px-4 py-3 text-left">Estado</th>
      <th class="px-4 py-3 text-left">Fecha</th>
    </tr>
  </thead>
  <tbody>
    {% for r in reports %}
    <tr class="border-t border-slate-100 hover:bg-slate-50 cursor-pointer"
        onclick="window.location='/reportes/{{ r.pk }}/'">
      <td class="px-4 py-3 text-slate-400 font-mono text-xs">#{{ r.pk }}</td>
      <td class="px-4 py-3">
        <div class="font-semibold text-sm max-w-xs truncate">{{ r.titulo }}</div>
        <div class="text-xs text-slate-400">{{ r.reportado_por.email }}</div>
      </td>
      <td class="px-4 py-3">
        <span class="text-xs font-semibold px-2 py-1 rounded"
          style="background:{{ r.plataforma.color }}22;color:{{ r.plataforma.color }}">
          {{ r.plataforma.nombre }}
        </span>
      </td>
      <td class="px-4 py-3">
        <span class="text-xs font-semibold px-2 py-1 rounded
          {% if r.tipo == 'BUG' %}bg-red-50 text-red-500
          {% elif r.tipo == 'SUGERENCIA' %}bg-blue-50 text-blue-600
          {% else %}bg-purple-50 text-purple-600{% endif %}">
          {{ r.get_tipo_display }}
        </span>
      </td>
      <td class="px-4 py-3">
        <span class="text-xs font-semibold px-2 py-1 rounded
          {% if r.severidad == 'CRITICA' %}bg-red-50 text-red-500
          {% elif r.severidad == 'ALTA' %}bg-orange-50 text-orange-500
          {% elif r.severidad == 'MEDIA' %}bg-yellow-50 text-yellow-600
          {% else %}bg-green-50 text-green-600{% endif %}">
          {{ r.get_severidad_display }}
        </span>
      </td>
      <td class="px-4 py-3">
        <span class="flex items-center gap-1.5 text-xs font-medium">
          <span class="w-2 h-2 rounded-full
            {% if r.estado == 'ABIERTO' %}bg-red-500
            {% elif r.estado == 'EN_REVISION' %}bg-yellow-500
            {% elif r.estado == 'RESUELTO' %}bg-green-500
            {% else %}bg-slate-400{% endif %}"></span>
          {{ r.get_estado_display }}
        </span>
      </td>
      <td class="px-4 py-3 text-xs text-slate-400">{{ r.creado_en|date:"d M, H:i" }}</td>
    </tr>
    {% empty %}
    <tr><td colspan="7" class="px-4 py-8 text-center text-slate-400 text-sm">Sin reportes</td></tr>
    {% endfor %}
  </tbody>
</table>
```

- [ ] **Step 7: Run tests — expect PASS**

```bash
python manage.py test apps.reports.tests.DashboardViewTest -v 2
```
Expected: `4 tests OK`

- [ ] **Step 8: Commit**

```bash
git add apps/reports/views.py apps/reports/urls.py templates/reports/dashboard.html templates/partials/
git commit -m "feat: add dashboard with HTMX filtering"
```

---

### Task 9: New Report Form

**Files:**
- Create: `apps/reports/forms.py`
- Modify: `apps/reports/views.py` (replace new_report stub)
- Create: `templates/reports/new_report.html`
- Modify: `apps/reports/tests.py`

- [ ] **Step 1: Write failing tests**

Add to `apps/reports/tests.py`:
```python
class NewReportViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.plat = Platform.objects.create(nombre='EVE 360', color='#0ea5e9')
        self.usuario = User.objects.create_user(
            username='u', email='u@t.com', password='p', rol=User.USUARIO)
        self.tester = User.objects.create_user(
            username='t', email='t@t.com', password='p', rol=User.TESTER)

    def test_usuario_can_create_basic_report(self):
        self.client.force_login(self.usuario)
        r = self.client.post(reverse('new_report'), {
            'titulo': 'Login falla', 'descripcion': 'No redirige',
            'plataforma': self.plat.pk, 'tipo': Report.BUG,
            'severidad': Report.ALTA,
        })
        self.assertEqual(Report.objects.count(), 1)
        report = Report.objects.first()
        self.assertEqual(report.reportado_por, self.usuario)
        self.assertRedirects(r, f'/reportes/{report.pk}/')

    def test_tester_can_create_full_report(self):
        self.client.force_login(self.tester)
        r = self.client.post(reverse('new_report'), {
            'titulo': 'Error XML', 'descripcion': 'Falla al exportar',
            'plataforma': self.plat.pk, 'tipo': Report.BUG,
            'severidad': Report.CRITICA,
            'pasos_reproducir': '1. Ir a exportar\n2. Click en XML',
            'resultado_esperado': 'Descarga el archivo',
            'resultado_obtenido': 'Error 500',
        })
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(Report.objects.first().pasos_reproducir, '1. Ir a exportar\n2. Click en XML')
```

- [ ] **Step 2: Run — expect FAIL**

```bash
python manage.py test apps.reports.tests.NewReportViewTest -v 2
```
Expected: `HttpResponse('TODO')` — redirects won't match.

- [ ] **Step 3: Create form**

`apps/reports/forms.py`:
```python
from django import forms
from apps.reports.models import Report
from apps.platforms.models import Platform

class ReportForm(forms.ModelForm):
    class Meta:
        model  = Report
        fields = [
            'titulo', 'descripcion', 'plataforma', 'tipo', 'severidad',
            'url_pagina', 'pasos_reproducir', 'resultado_esperado', 'resultado_obtenido',
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plataforma'].queryset = Platform.objects.filter(activa=True)
        # Simplify form for basic users — hide technical fields
        if user and user.is_usuario:
            for f in ['url_pagina','pasos_reproducir','resultado_esperado','resultado_obtenido']:
                self.fields[f].required = False
                self.fields[f].widget = forms.HiddenInput()
```

- [ ] **Step 4: Replace new_report stub in views.py**

Remove the stub and add:
```python
from apps.reports.forms import ReportForm

@login_required
def new_report_view(request):
    form = ReportForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        report = form.save(commit=False)
        report.reportado_por = request.user
        report.save()
        # Handle screenshots
        for img in request.FILES.getlist('screenshots'):
            from apps.reports.models import Screenshot
            Screenshot.objects.create(reporte=report, imagen=img)
        return redirect('report_detail', pk=report.pk)
    return render(request, 'reports/new_report.html', {'form': form})
```

- [ ] **Step 5: Create templates/reports/new_report.html**

```html
{% extends 'dashboard_base.html' %}
{% block page_title %}Nuevo Reporte{% endblock %}
{% block nav_new %}active{% endblock %}
{% block main_content %}
<div class="max-w-2xl bg-white rounded-xl border border-slate-200 p-8">
  <form method="post" enctype="multipart/form-data">
    {% csrf_token %}

    <div class="mb-4">
      <label class="block text-sm font-medium text-slate-700 mb-1">Título *</label>
      <input name="titulo" type="text" required
        class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-sky-400 outline-none">
    </div>

    <div class="grid grid-cols-3 gap-4 mb-4">
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Plataforma *</label>
        <select name="plataforma" required
          class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none">
          {% for p in form.plataforma.field.queryset %}
            <option value="{{ p.pk }}">{{ p.nombre }}</option>
          {% endfor %}
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Tipo *</label>
        <select name="tipo" required class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none">
          {% for val, label in form.fields.tipo.choices %}
            <option value="{{ val }}">{{ label }}</option>
          {% endfor %}
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Severidad *</label>
        <select name="severidad" required class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none">
          {% for val, label in form.fields.severidad.choices %}
            <option value="{{ val }}">{{ label }}</option>
          {% endfor %}
        </select>
      </div>
    </div>

    <div class="mb-4">
      <label class="block text-sm font-medium text-slate-700 mb-1">Descripción *</label>
      <textarea name="descripcion" rows="4" required
        class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-sky-400 outline-none"></textarea>
    </div>

    <!-- Technical fields: hidden for USUARIO via form, shown for TESTER/ADMIN -->
    {% if not user.is_usuario %}
    <div class="border-t border-slate-100 pt-4 mt-4">
      <p class="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">Campos técnicos</p>
      <div class="mb-4">
        <label class="block text-sm font-medium text-slate-700 mb-1">URL de la página</label>
        <input name="url_pagina" type="url"
          class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-sky-400 outline-none"
          placeholder="https://...">
      </div>
      <div class="mb-4">
        <label class="block text-sm font-medium text-slate-700 mb-1">Pasos para reproducir</label>
        <textarea name="pasos_reproducir" rows="3"
          class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-sky-400 outline-none"
          placeholder="1. Ir a...\n2. Click en..."></textarea>
      </div>
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Resultado esperado</label>
          <textarea name="resultado_esperado" rows="2"
            class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-sky-400 outline-none"></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Resultado obtenido</label>
          <textarea name="resultado_obtenido" rows="2"
            class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-sky-400 outline-none"></textarea>
        </div>
      </div>
    </div>
    {% endif %}

    <!-- Screenshots -->
    <div class="mb-6" x-data="{ files: [] }">
      <label class="block text-sm font-medium text-slate-700 mb-1">Capturas de pantalla</label>
      <input type="file" name="screenshots" multiple accept="image/*"
        @change="files = Array.from($event.target.files).map(f => URL.createObjectURL(f))"
        class="block w-full text-sm text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-[#0a1628] file:text-white hover:file:bg-[#162d5a]">
      <div class="mt-2 flex flex-wrap gap-2">
        <template x-for="url in files">
          <img :src="url" class="h-16 w-24 object-cover rounded border border-slate-200">
        </template>
      </div>
    </div>

    <div class="flex gap-3">
      <button type="submit"
        class="bg-[#0a1628] text-white font-semibold px-6 py-2.5 rounded-lg hover:bg-[#162d5a] transition text-sm">
        Enviar Reporte
      </button>
      <a href="/" class="border border-slate-300 text-slate-600 font-semibold px-6 py-2.5 rounded-lg hover:bg-slate-50 transition text-sm">
        Cancelar
      </a>
    </div>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 6: Run tests — expect PASS**

```bash
python manage.py test apps.reports.tests.NewReportViewTest -v 2
```
Expected: `2 tests OK`

- [ ] **Step 7: Commit**

```bash
git add apps/reports/forms.py apps/reports/views.py templates/reports/new_report.html
git commit -m "feat: add new report form with role-based fields"
```

---

### Task 10: Report Detail + Status Change

**Files:**
- Modify: `apps/reports/views.py` (replace detail and change_status stubs)
- Create: `templates/reports/report_detail.html`
- Modify: `apps/reports/tests.py`

- [ ] **Step 1: Write failing tests**

Add to `apps/reports/tests.py`:
```python
class ReportDetailTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.plat = Platform.objects.create(nombre='EVE 360', color='#0ea5e9')
        self.admin = User.objects.create_user(
            username='a', email='a@t.com', password='p', rol=User.ADMIN)
        self.usuario = User.objects.create_user(
            username='u', email='u@t.com', password='p', rol=User.USUARIO)
        self.report = Report.objects.create(
            titulo='Bug test', descripcion='desc',
            plataforma=self.plat, tipo=Report.BUG,
            severidad=Report.ALTA, reportado_por=self.usuario,
        )

    def test_detail_loads(self):
        self.client.force_login(self.usuario)
        r = self.client.get(reverse('report_detail', args=[self.report.pk]))
        self.assertContains(r, 'Bug test')

    def test_change_status_requires_tester_or_admin(self):
        self.client.force_login(self.usuario)
        r = self.client.post(reverse('change_status', args=[self.report.pk]),
            {'estado': Report.EN_REVISION})
        self.assertEqual(r.status_code, 403)

    def test_admin_can_change_status(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('change_status', args=[self.report.pk]),
            {'estado': Report.EN_REVISION})
        self.report.refresh_from_db()
        self.assertEqual(self.report.estado, Report.EN_REVISION)
        self.assertEqual(StatusHistory.objects.filter(reporte=self.report).count(), 1)
```

- [ ] **Step 2: Run — expect FAIL**

```bash
python manage.py test apps.reports.tests.ReportDetailTest -v 2
```
Expected: responses are `HttpResponse('TODO')` — tests fail.

- [ ] **Step 3: Replace stubs in views.py**

```python
@login_required
def report_detail_view(request, pk):
    report = get_object_or_404(Report, pk=pk)
    # Usuarios can only see their own reports
    if request.user.is_usuario and report.reportado_por != request.user:
        from django.http import HttpResponseForbidden
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
        'reports': reports, 'platforms': platforms,
        'estado_choices': Report.ESTADO_CHOICES,
        'tipo_choices': Report.TIPO_CHOICES,
        'sev_choices': Report.SEV_CHOICES,
    })
```

- [ ] **Step 4: Create templates/reports/report_detail.html**

```html
{% extends 'dashboard_base.html' %}
{% block page_title %}Reporte #{{ report.pk }}{% endblock %}
{% block page_subtitle %}{{ report.plataforma.nombre }} · {{ report.creado_en|date:"d M Y, H:i" }}{% endblock %}
{% block main_content %}
<div class="grid grid-cols-3 gap-6">

  <!-- Main info -->
  <div class="col-span-2 space-y-4">
    <div class="bg-white rounded-xl border border-slate-200 p-6">
      <div class="flex gap-2 mb-4 flex-wrap">
        <span class="text-xs font-semibold px-2 py-1 rounded
          {% if report.tipo == 'BUG' %}bg-red-50 text-red-500
          {% elif report.tipo == 'SUGERENCIA' %}bg-blue-50 text-blue-600
          {% else %}bg-purple-50 text-purple-600{% endif %}">
          {{ report.get_tipo_display }}
        </span>
        <span class="text-xs font-semibold px-2 py-1 rounded
          {% if report.severidad == 'CRITICA' %}bg-red-50 text-red-500
          {% elif report.severidad == 'ALTA' %}bg-orange-50 text-orange-500
          {% elif report.severidad == 'MEDIA' %}bg-yellow-50 text-yellow-600
          {% else %}bg-green-50 text-green-600{% endif %}">
          {{ report.get_severidad_display }}
        </span>
      </div>
      <h3 class="text-lg font-bold mb-3">{{ report.titulo }}</h3>
      <p class="text-slate-600 text-sm leading-relaxed">{{ report.descripcion }}</p>

      {% if report.url_pagina %}
      <p class="mt-4 text-sm"><span class="font-medium text-slate-700">URL:</span>
        <a href="{{ report.url_pagina }}" class="text-sky-500 hover:underline text-xs">{{ report.url_pagina }}</a>
      </p>
      {% endif %}

      {% if report.pasos_reproducir %}
      <div class="mt-4">
        <p class="text-sm font-semibold text-slate-700 mb-1">Pasos para reproducir</p>
        <pre class="bg-slate-50 text-xs rounded p-3 text-slate-600 whitespace-pre-wrap">{{ report.pasos_reproducir }}</pre>
      </div>
      {% endif %}

      {% if report.resultado_esperado %}
      <div class="grid grid-cols-2 gap-4 mt-4">
        <div>
          <p class="text-sm font-semibold text-slate-700 mb-1">Resultado esperado</p>
          <p class="text-sm text-slate-600 bg-green-50 p-3 rounded">{{ report.resultado_esperado }}</p>
        </div>
        <div>
          <p class="text-sm font-semibold text-slate-700 mb-1">Resultado obtenido</p>
          <p class="text-sm text-slate-600 bg-red-50 p-3 rounded">{{ report.resultado_obtenido }}</p>
        </div>
      </div>
      {% endif %}
    </div>

    <!-- Screenshots -->
    {% if report.screenshots.all %}
    <div class="bg-white rounded-xl border border-slate-200 p-6">
      <h4 class="font-semibold mb-3 text-sm">Capturas de pantalla</h4>
      <div class="flex flex-wrap gap-3">
        {% for s in report.screenshots.all %}
        <a href="{{ s.imagen.url }}" target="_blank">
          <img src="{{ s.imagen.url }}" class="h-32 w-48 object-cover rounded-lg border border-slate-200 hover:opacity-90 transition">
        </a>
        {% endfor %}
      </div>
    </div>
    {% endif %}
  </div>

  <!-- Sidebar -->
  <div class="space-y-4">

    <!-- Status -->
    <div class="bg-white rounded-xl border border-slate-200 p-5">
      <h4 class="text-sm font-semibold mb-3">Estado actual</h4>
      <div id="status-badge" class="mb-3">
        {% include 'partials/status_badge.html' %}
      </div>
      {% if user.is_tester or user.is_admin %}
      <form hx-post="{% url 'change_status' report.pk %}"
            hx-target="#status-badge"
            hx-swap="outerHTML">
        {% csrf_token %}
        <select name="estado"
          class="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-sm outline-none mb-2">
          {% for val, label in estado_choices %}
            <option value="{{ val }}" {% if report.estado == val %}selected{% endif %}>{{ label }}</option>
          {% endfor %}
        </select>
        <button type="submit"
          class="w-full bg-[#0a1628] text-white text-sm font-semibold py-2 rounded-lg hover:bg-[#162d5a] transition">
          Actualizar estado
        </button>
      </form>
      {% endif %}
    </div>

    <!-- Meta -->
    <div class="bg-white rounded-xl border border-slate-200 p-5">
      <h4 class="text-sm font-semibold mb-3">Información</h4>
      <div class="space-y-2 text-xs text-slate-500">
        <div><span class="font-medium text-slate-700">Plataforma:</span> {{ report.plataforma.nombre }}</div>
        <div><span class="font-medium text-slate-700">Reportado por:</span> {{ report.reportado_por.email }}</div>
        <div><span class="font-medium text-slate-700">Creado:</span> {{ report.creado_en|date:"d M Y, H:i" }}</div>
        <div><span class="font-medium text-slate-700">Actualizado:</span> {{ report.actualizado_en|date:"d M Y, H:i" }}</div>
      </div>
    </div>

    <!-- History -->
    {% if report.historial.all %}
    <div class="bg-white rounded-xl border border-slate-200 p-5">
      <h4 class="text-sm font-semibold mb-3">Historial de estados</h4>
      <div class="space-y-2">
        {% for h in report.historial.all %}
        <div class="text-xs text-slate-500 flex gap-2">
          <span>{{ h.fecha|date:"d M, H:i" }}</span>
          <span class="text-slate-300">→</span>
          <span class="font-medium text-slate-700">{{ h.estado_nuevo }}</span>
          <span class="text-slate-400">por {{ h.cambiado_por.email }}</span>
        </div>
        {% endfor %}
      </div>
    </div>
    {% endif %}

  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Create templates/partials/status_badge.html**

```html
<span class="inline-flex items-center gap-1.5 text-sm font-semibold
  {% if report.estado == 'ABIERTO' %}text-red-600
  {% elif report.estado == 'EN_REVISION' %}text-yellow-600
  {% elif report.estado == 'RESUELTO' %}text-green-600
  {% else %}text-slate-500{% endif %}">
  <span class="w-2 h-2 rounded-full
    {% if report.estado == 'ABIERTO' %}bg-red-500
    {% elif report.estado == 'EN_REVISION' %}bg-yellow-500
    {% elif report.estado == 'RESUELTO' %}bg-green-500
    {% else %}bg-slate-400{% endif %}"></span>
  {{ report.get_estado_display }}
</span>
```

- [ ] **Step 6: Create templates/reports/admin_reports.html**

```html
{% extends 'dashboard_base.html' %}
{% block page_title %}Todos los Reportes{% endblock %}
{% block nav_admin_rep %}active{% endblock %}
{% block main_content %}
<div class="bg-white rounded-xl border border-slate-200">
  <div class="p-4 border-b border-slate-100 flex flex-wrap gap-3 items-center">
    <select name="plataforma"
      hx-get="{% url 'reports_table' %}" hx-trigger="change" hx-target="#tabla-reportes"
      class="border border-slate-300 rounded-lg px-3 py-1.5 text-sm outline-none">
      <option value="">Todas las plataformas</option>
      {% for p in platforms %}<option value="{{ p.pk }}">{{ p.nombre }}</option>{% endfor %}
    </select>
    <select name="estado"
      hx-get="{% url 'reports_table' %}" hx-trigger="change" hx-target="#tabla-reportes"
      class="border border-slate-300 rounded-lg px-3 py-1.5 text-sm outline-none">
      <option value="">Todos los estados</option>
      {% for val, label in estado_choices %}<option value="{{ val }}">{{ label }}</option>{% endfor %}
    </select>
    <select name="tipo"
      hx-get="{% url 'reports_table' %}" hx-trigger="change" hx-target="#tabla-reportes"
      class="border border-slate-300 rounded-lg px-3 py-1.5 text-sm outline-none">
      <option value="">Todos los tipos</option>
      {% for val, label in tipo_choices %}<option value="{{ val }}">{{ label }}</option>{% endfor %}
    </select>
  </div>
  <div id="tabla-reportes">
    {% include 'partials/reports_table.html' %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 7: Run tests — expect PASS**

```bash
python manage.py test apps.reports.tests -v 2
```
Expected: all report tests pass.

- [ ] **Step 8: Commit**

```bash
git add apps/reports/views.py templates/reports/ templates/partials/status_badge.html
git commit -m "feat: add report detail, status change, admin reports"
```

---

### Task 11: PDF Export

**Files:**
- Create: `apps/exports/views.py`
- Modify: `apps/exports/urls.py`
- Create: `apps/exports/tests.py`
- Create: `templates/exports/pdf_form.html`
- Create: `templates/pdf/report.html`

- [ ] **Step 1: Write failing tests**

`apps/exports/tests.py`:
```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.reports.models import Report

class PDFExportTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='a', email='a@t.com', password='p', rol=User.ADMIN)
        self.usuario = User.objects.create_user(
            username='u', email='u@t.com', password='p', rol=User.USUARIO)
        self.plat = Platform.objects.create(nombre='EVE 360', color='#0ea5e9')
        Report.objects.create(
            titulo='Bug SAT', descripcion='desc',
            plataforma=self.plat, tipo=Report.BUG,
            severidad=Report.CRITICA, reportado_por=self.admin,
        )

    def test_pdf_form_loads_for_admin(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse('pdf_form'))
        self.assertEqual(r.status_code, 200)

    def test_pdf_form_blocked_for_usuario(self):
        self.client.force_login(self.usuario)
        r = self.client.get(reverse('pdf_form'))
        self.assertEqual(r.status_code, 403)

    def test_pdf_download_returns_pdf(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse('pdf_download'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/pdf')
        self.assertIn('attachment', r['Content-Disposition'])
```

- [ ] **Step 2: Run — expect FAIL**

```bash
python manage.py test apps.exports.tests -v 2
```
Expected: `NoReverseMatch`

- [ ] **Step 3: Create views**

`apps/exports/views.py`:
```python
import base64
import os
from io import BytesIO
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML
from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.reports.models import Report

@role_required(User.ADMIN)
def pdf_form_view(request):
    platforms = Platform.objects.filter(activa=True)
    return render(request, 'exports/pdf_form.html', {
        'platforms': platforms,
        'estado_choices': Report.ESTADO_CHOICES,
        'sev_choices': Report.SEV_CHOICES,
    })

@role_required(User.ADMIN)
def pdf_download_view(request):
    qs = Report.objects.select_related('plataforma', 'reportado_por').prefetch_related('screenshots')
    plataforma = request.GET.get('plataforma')
    estado     = request.GET.get('estado')
    severidad  = request.GET.get('severidad')
    desde      = request.GET.get('desde')
    hasta      = request.GET.get('hasta')

    if plataforma: qs = qs.filter(plataforma_id=plataforma)
    if estado:     qs = qs.filter(estado=estado)
    if severidad:  qs = qs.filter(severidad=severidad)
    if desde:      qs = qs.filter(creado_en__date__gte=desde)
    if hasta:      qs = qs.filter(creado_en__date__lte=hasta)

    # Embed screenshots as base64 for PDF
    reports_data = []
    for r in qs:
        shots = []
        for s in r.screenshots.all():
            if s.imagen and os.path.exists(s.imagen.path):
                with open(s.imagen.path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode()
                    shots.append(f'data:image/jpeg;base64,{b64}')
        reports_data.append({'report': r, 'screenshots_b64': shots})

    html_string = render_to_string('pdf/report.html', {
        'reports_data': reports_data,
        'generado_en': timezone.now(),
        'filtros': {
            'plataforma': Platform.objects.filter(pk=plataforma).first() if plataforma else None,
            'estado': estado, 'severidad': severidad, 'desde': desde, 'hasta': hasta,
        },
        'totales': {
            'total': qs.count(),
            'bugs': qs.filter(tipo=Report.BUG).count(),
            'sugerencias': qs.filter(tipo=Report.SUGERENCIA).count(),
            'quejas': qs.filter(tipo=Report.QUEJA).count(),
            'criticos': qs.filter(severidad=Report.CRITICA).count(),
            'resueltos': qs.filter(estado=Report.RESUELTO).count(),
        },
    })

    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)
    pdf_file.seek(0)

    filename = f"reporte-feedbackeve-{timezone.now().strftime('%Y-%m-%d')}.pdf"
    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
```

- [ ] **Step 4: Create URLs**

`apps/exports/urls.py`:
```python
from django.urls import path
from apps.exports import views

urlpatterns = [
    path('exports/pdf/',          views.pdf_form_view,     name='pdf_form'),
    path('exports/pdf/download/', views.pdf_download_view, name='pdf_download'),
]
```

- [ ] **Step 5: Create templates/exports/pdf_form.html**

```html
{% extends 'dashboard_base.html' %}
{% block page_title %}Exportar PDF{% endblock %}
{% block nav_pdf %}active{% endblock %}
{% block main_content %}
<div class="max-w-lg bg-white rounded-xl border border-slate-200 p-8">
  <p class="text-slate-500 text-sm mb-6">
    Filtra los reportes que deseas incluir en el PDF y descárgalo.
  </p>
  <form action="{% url 'pdf_download' %}" method="get" target="_blank">

    <div class="mb-4">
      <label class="block text-sm font-medium text-slate-700 mb-1">Plataforma</label>
      <select name="plataforma"
        class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none">
        <option value="">Todas</option>
        {% for p in platforms %}<option value="{{ p.pk }}">{{ p.nombre }}</option>{% endfor %}
      </select>
    </div>

    <div class="mb-4">
      <label class="block text-sm font-medium text-slate-700 mb-1">Estado</label>
      <select name="estado"
        class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none">
        <option value="">Todos</option>
        {% for val, label in estado_choices %}<option value="{{ val }}">{{ label }}</option>{% endfor %}
      </select>
    </div>

    <div class="mb-4">
      <label class="block text-sm font-medium text-slate-700 mb-1">Severidad</label>
      <select name="severidad"
        class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none">
        <option value="">Todas</option>
        {% for val, label in sev_choices %}<option value="{{ val }}">{{ label }}</option>{% endfor %}
      </select>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-6">
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Desde</label>
        <input type="date" name="desde"
          class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none">
      </div>
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Hasta</label>
        <input type="date" name="hasta"
          class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none">
      </div>
    </div>

    <button type="submit"
      class="w-full bg-[#0a1628] text-white font-semibold py-2.5 rounded-lg hover:bg-[#162d5a] transition">
      Descargar PDF
    </button>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 6: Create templates/pdf/report.html**

```html
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 11px; color: #0f172a; }
  .header { background: #0a1628; color: white; padding: 24px 32px; margin-bottom: 24px; }
  .header h1 { font-size: 20px; font-weight: 800; margin-bottom: 4px; }
  .header p  { font-size: 11px; color: #94a3b8; }
  .filters   { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px; margin: 0 32px 20px; display: flex; gap: 16px; flex-wrap: wrap; }
  .filter-item span:first-child { font-weight: 600; color: #475569; }
  .totals    { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; margin: 0 32px 24px; }
  .total-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; text-align: center; }
  .total-box .val { font-size: 20px; font-weight: 800; color: #0a1628; }
  .total-box .lbl { font-size: 9px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
  .section-title { font-size: 12px; font-weight: 700; color: #0a1628; padding: 0 32px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
  .report-card { margin: 0 32px 16px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; page-break-inside: avoid; }
  .report-header { background: #f8fafc; padding: 10px 16px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #e2e8f0; }
  .report-id   { font-size: 10px; font-family: monospace; color: #94a3b8; }
  .badge       { font-size: 9px; font-weight: 700; padding: 2px 6px; border-radius: 3px; }
  .badge.bug        { background: #fef2f2; color: #ef4444; }
  .badge.sugerencia { background: #eff6ff; color: #2563eb; }
  .badge.queja      { background: #fdf4ff; color: #9333ea; }
  .badge.critica { background: #fef2f2; color: #ef4444; }
  .badge.alta    { background: #fff7ed; color: #f97316; }
  .badge.media   { background: #fefce8; color: #ca8a04; }
  .badge.baja    { background: #f0fdf4; color: #16a34a; }
  .badge.abierto     { background: #fef2f2; color: #ef4444; }
  .badge.en_revision { background: #fefce8; color: #ca8a04; }
  .badge.resuelto    { background: #f0fdf4; color: #16a34a; }
  .badge.cerrado     { background: #f1f5f9; color: #64748b; }
  .report-title  { font-weight: 700; font-size: 12px; flex: 1; }
  .report-body   { padding: 12px 16px; }
  .report-desc   { color: #475569; margin-bottom: 8px; line-height: 1.5; }
  .meta-row      { display: flex; gap: 16px; font-size: 10px; color: #64748b; margin-bottom: 6px; }
  .meta-row strong { color: #334155; }
  .field-label { font-weight: 700; font-size: 10px; color: #475569; margin-top: 8px; margin-bottom: 2px; }
  .field-val   { background: #f8fafc; padding: 6px 8px; border-radius: 4px; line-height: 1.4; white-space: pre-wrap; }
  .screenshots { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
  .screenshots img { height: 80px; width: 120px; object-fit: cover; border-radius: 4px; border: 1px solid #e2e8f0; }
  .footer { margin-top: 32px; padding: 16px 32px; border-top: 1px solid #e2e8f0; font-size: 10px; color: #94a3b8; text-align: center; }
</style>
</head>
<body>

<div class="header">
  <h1>FeedbackEve — Reporte de Calidad</h1>
  <p>Generado el {{ generado_en|date:"d/m/Y H:i" }}</p>
</div>

<div class="filters">
  <div class="filter-item"><span>Plataforma:</span> {{ filtros.plataforma.nombre|default:"Todas" }}</div>
  <div class="filter-item"><span>Estado:</span> {{ filtros.estado|default:"Todos" }}</div>
  <div class="filter-item"><span>Severidad:</span> {{ filtros.severidad|default:"Todas" }}</div>
  {% if filtros.desde %}<div class="filter-item"><span>Desde:</span> {{ filtros.desde }}</div>{% endif %}
  {% if filtros.hasta %}<div class="filter-item"><span>Hasta:</span> {{ filtros.hasta }}</div>{% endif %}
</div>

<div class="totales">
  <div class="total-box"><div class="val">{{ totales.total }}</div><div class="lbl">Total</div></div>
  <div class="total-box"><div class="val" style="color:#ef4444">{{ totales.bugs }}</div><div class="lbl">Bugs</div></div>
  <div class="total-box"><div class="val" style="color:#2563eb">{{ totales.sugerencias }}</div><div class="lbl">Sugerencias</div></div>
  <div class="total-box"><div class="val" style="color:#9333ea">{{ totales.quejas }}</div><div class="lbl">Quejas</div></div>
  <div class="total-box"><div class="val" style="color:#ef4444">{{ totales.criticos }}</div><div class="lbl">Críticos</div></div>
  <div class="total-box"><div class="val" style="color:#22c55e">{{ totales.resueltos }}</div><div class="lbl">Resueltos</div></div>
</div>

<p class="section-title">Detalle de Reportes ({{ totales.total }})</p>

{% for item in reports_data %}
{% with r=item.report %}
<div class="report-card">
  <div class="report-header">
    <span class="report-id">#{{ r.pk }}</span>
    <span class="report-title">{{ r.titulo }}</span>
    <span class="badge {{ r.tipo|lower }}">{{ r.get_tipo_display }}</span>
    <span class="badge {{ r.severidad|lower }}">{{ r.get_severidad_display }}</span>
    <span class="badge {{ r.estado|lower }}">{{ r.get_estado_display }}</span>
  </div>
  <div class="report-body">
    <p class="report-desc">{{ r.descripcion }}</p>
    <div class="meta-row">
      <span><strong>Plataforma:</strong> {{ r.plataforma.nombre }}</span>
      <span><strong>Reportado por:</strong> {{ r.reportado_por.email }}</span>
      <span><strong>Fecha:</strong> {{ r.creado_en|date:"d/m/Y H:i" }}</span>
    </div>
    {% if r.pasos_reproducir %}
      <p class="field-label">Pasos para reproducir</p>
      <div class="field-val">{{ r.pasos_reproducir }}</div>
    {% endif %}
    {% if r.resultado_esperado %}
      <p class="field-label">Resultado esperado</p>
      <div class="field-val">{{ r.resultado_esperado }}</div>
      <p class="field-label">Resultado obtenido</p>
      <div class="field-val">{{ r.resultado_obtenido }}</div>
    {% endif %}
    {% if item.screenshots_b64 %}
    <p class="field-label">Capturas de pantalla</p>
    <div class="screenshots">
      {% for src in item.screenshots_b64 %}
        <img src="{{ src }}">
      {% endfor %}
    </div>
    {% endif %}
  </div>
</div>
{% endwith %}
{% endfor %}

<div class="footer">FeedbackEve · Portal Unificado de Calidad e Incidencias</div>
</body>
</html>
```

- [ ] **Step 7: Run tests — expect PASS**

```bash
python manage.py test apps.exports.tests -v 2
```
Expected: `3 tests OK`

- [ ] **Step 8: Run all tests**

```bash
python manage.py test apps -v 2
```
Expected: all tests pass.

- [ ] **Step 9: Commit**

```bash
git add apps/exports/ templates/exports/ templates/pdf/
git commit -m "feat: add PDF export with WeasyPrint"
```

---

### Task 12: Create Superuser + Smoke Test

- [ ] **Step 1: Create admin superuser**

```bash
python manage.py createsuperuser
```
When prompted, enter email, username, and password.

Then in Django shell, set its role:
```bash
python manage.py shell
```
```python
from apps.accounts.models import User
u = User.objects.get(email='your@email.com')
u.rol = User.ADMIN
u.save()
```

- [ ] **Step 2: Run server and smoke test**

```bash
python manage.py runserver
```

Visit in order:
1. `http://localhost:8000/login/` — should show login form
2. Login with admin credentials → redirects to `/`
3. `http://localhost:8000/admin/plataformas/` → add EVE 360, Medical, Órbita
4. `http://localhost:8000/reportes/nuevo/` → create a bug report with a screenshot
5. `http://localhost:8000/` → report appears in table; try filters
6. Click report → detail page; change status → badge updates via HTMX
7. `http://localhost:8000/exports/pdf/` → generate PDF → verify it downloads with screenshots

- [ ] **Step 3: Final commit**

```bash
git add .
git commit -m "feat: complete FeedbackEve v1 — bug tracker with HTMX + PDF export"
```
