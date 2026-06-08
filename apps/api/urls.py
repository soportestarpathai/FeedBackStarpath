from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import views

urlpatterns = [
    # ── Raíz ────────────────────────────────────────────────────────────────
    path('',                            views.api_root,                 name='api_root'),

    # ── JWT auth ────────────────────────────────────────────────────────────
    path('auth/token/',                 TokenObtainPairView.as_view(),  name='api_token'),
    path('auth/token/refresh/',         TokenRefreshView.as_view(),     name='api_token_refresh'),
    path('auth/me/',                    views.me_view,                  name='api_me'),

    # ── Plataformas ─────────────────────────────────────────────────────────
    path('plataformas/',                views.PlatformListView.as_view(),   name='api_platforms'),
    path('plataformas/crear/',          views.PlatformCreateView.as_view(), name='api_platform_create'),
    path('plataformas/<int:pk>/editar/',views.PlatformUpdateView.as_view(), name='api_platform_update'),
    path('plataformas/<int:pk>/eliminar/', views.PlatformDeleteView.as_view(), name='api_platform_delete'),
    path('plataformas/<int:pk>/toggle/',views.PlatformToggleView.as_view(), name='api_platform_toggle'),

    # ── Reportes ────────────────────────────────────────────────────────────
    path('reportes/',                       views.ReportListView.as_view(),         name='api_reports'),
    path('reportes/crear/',                 views.ReportCreateView.as_view(),       name='api_report_create'),
    path('reportes/<int:pk>/',              views.ReportDetailView.as_view(),       name='api_report_detail'),
    path('reportes/<int:pk>/editar/',       views.ReportUpdateView.as_view(),       name='api_report_update'),
    path('reportes/<int:pk>/eliminar/',     views.ReportDeleteView.as_view(),       name='api_report_delete'),
    path('reportes/<int:pk>/estado/',       views.ReportChangeStatusView.as_view(), name='api_report_status'),
    path('reportes/<int:pk>/asignar/',      views.ReportAssignView.as_view(),       name='api_report_assign'),

    # ── Usuarios ────────────────────────────────────────────────────────────
    path('usuarios/',                   views.UserListView.as_view(),       name='api_users'),
    path('usuarios/<int:pk>/',          views.UserDetailView.as_view(),     name='api_user_detail'),
    path('usuarios/<int:pk>/editar/',   views.UserUpdateView.as_view(),     name='api_user_update'),
    path('usuarios/<int:pk>/desactivar/', views.UserDeactivateView.as_view(), name='api_user_deactivate'),

    # ── Swagger / OpenAPI ────────────────────────────────────────────────────
    path('schema/',   SpectacularAPIView.as_view(),                                 name='api_schema'),
    path('docs/',     SpectacularSwaggerView.as_view(url_name='api_schema'),        name='api_swagger'),
    path('redoc/',    SpectacularRedocView.as_view(url_name='api_schema'),          name='api_redoc'),
]
