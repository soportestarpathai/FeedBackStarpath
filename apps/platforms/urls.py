from django.urls import path
from apps.platforms import views

urlpatterns = [
    path('admin/plataformas/', views.admin_platforms_view, name='admin_platforms'),
    path('admin/plataformas/<int:pk>/toggle/', views.platform_toggle_view, name='platform_toggle'),
    path('admin/plataformas/<int:pk>/delete/', views.platform_delete_view, name='platform_delete'),
]
