from django.urls import path
from apps.accounts import views

urlpatterns = [
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('registro/', views.register_view, name='register'),
    path('admin/usuarios/', views.admin_users_view, name='admin_users'),
]
