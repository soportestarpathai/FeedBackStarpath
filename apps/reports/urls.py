from django.urls import path
from apps.reports import views

urlpatterns = [
    path('',                          views.dashboard_view,        name='dashboard'),
    path('reportes/tabla/',           views.reports_table_partial, name='reports_table'),
    path('reportes/nuevo/',           views.new_report_view,       name='new_report'),
    path('reportes/<int:pk>/',        views.report_detail_view,    name='report_detail'),
    path('admin/reportes/',           views.admin_reports_view,    name='admin_reports'),
    path('reportes/<int:pk>/estado/', views.change_status_view,    name='change_status'),
]
