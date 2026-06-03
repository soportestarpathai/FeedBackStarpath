from django.urls import path
from apps.reports import views

urlpatterns = [
    # Dispatch / shared
    path('reportes/',                         views.reportes_view,           name='reportes'),
    path('reportes/tabla/',                   views.tabla_reportes_partial,  name='tabla_reportes'),
    path('reportes/nuevo/',                   views.nuevo_reporte_tester,    name='nuevo_reporte'),
    path('reportes/<int:pk>/',                views.detalle_reporte_tester,  name='detalle_reporte'),
    path('reportes/<int:pk>/estado/',         views.cambiar_estado_tester,   name='cambiar_estado'),
    # Tester
    path('tester/plataformas/',               views.mis_plataformas_tester,  name='mis_plataformas'),
    # Admin
    path('admin/resumen/',                    views.resumen_admin,           name='admin_resumen'),
    path('admin/reportes/',                   views.reportes_admin,          name='admin_reportes'),
    path('admin/reportes/tabla/',             views.tabla_admin_partial,     name='admin_tabla'),
    path('admin/reportes/<int:pk>/',          views.detalle_reporte_admin,   name='admin_detalle'),
    path('admin/reportes/<int:pk>/estado/',   views.cambiar_estado_admin,    name='admin_estado'),
    path('admin/reportes/<int:pk>/asignar/',      views.asignar_tester,          name='asignar_tester'),
    # SuperAdmin reports
    path('superadmin/reportes/',                  views.reportes_superadmin,     name='sa_reportes'),
    path('superadmin/reportes/tabla/',            views.tabla_sa_partial,        name='sa_tabla'),
    path('superadmin/reportes/<int:pk>/estado/',  views.cambiar_estado_sa,       name='sa_estado'),
]
