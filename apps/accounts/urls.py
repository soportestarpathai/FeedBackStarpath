from django.urls import path
from apps.accounts import views

urlpatterns = [
    path('',                             views.home_view,            name='home'),
    path('login/',                       views.login_view,           name='login'),
    path('logout/',                      views.logout_view,          name='logout'),
    path('registro/',                    views.registro_view,        name='registro'),
    path('verificar-correo/',            views.verificar_correo_view, name='verificar_correo'),
    path('admin/usuarios/',              views.usuarios_admin,       name='admin_usuarios'),
    path('admin/usuarios/<int:pk>/rol/', views.cambiar_rol,          name='cambiar_rol'),
]
