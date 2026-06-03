from django.urls import path
from apps.exports import views

urlpatterns = [
    path('admin/pdf/',      views.exportar_pdf, name='admin_pdf'),
    path('superadmin/pdf/', views.exportar_pdf, name='sa_pdf'),
]
