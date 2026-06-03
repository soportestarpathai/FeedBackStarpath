from django.urls import path
from apps.platforms import views

urlpatterns = [
    path('superadmin/dashboard/',               views.dashboard_superadmin, name='sa_dashboard'),
    path('superadmin/plataformas/',             views.lista_plataformas,    name='sa_plataformas'),
    path('superadmin/plataformas/<int:pk>/toggle/', views.toggle_plataforma, name='sa_toggle_plat'),
    path('superadmin/plataformas/<int:pk>/eliminar/', views.eliminar_plataforma, name='sa_eliminar_plat'),
    path('superadmin/admins/',                  views.lista_admins,         name='sa_admins'),
    path('superadmin/admins/crear/',            views.crear_admin,          name='sa_crear_admin'),
    path('superadmin/admins/<int:pk>/toggle/',  views.toggle_admin,         name='sa_toggle_admin'),
    path('superadmin/config/',                  views.config_global,        name='sa_config'),
]
