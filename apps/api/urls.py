from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import views

urlpatterns = [
    # ── JWT auth ────────────────────────────────────────────────────────────
    path('auth/token/',         TokenObtainPairView.as_view(),  name='api_token'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),     name='api_token_refresh'),
    path('auth/me/',            views.me_view,                  name='api_me'),

    # ── Plataformas ─────────────────────────────────────────────────────────
    path('plataformas/',        views.PlatformListView.as_view(),   name='api_platforms'),
    path('plataformas/crear/',  views.PlatformCreateView.as_view(), name='api_platform_create'),

    # ── Reportes ────────────────────────────────────────────────────────────
    path('reportes/',                           views.ReportListView.as_view(),         name='api_reports'),
    path('reportes/crear/',                     views.ReportCreateView.as_view(),       name='api_report_create'),
    path('reportes/<int:pk>/',                  views.ReportDetailView.as_view(),       name='api_report_detail'),
    path('reportes/<int:pk>/estado/',           views.ReportChangeStatusView.as_view(), name='api_report_status'),
    path('reportes/<int:pk>/asignar/',          views.ReportAssignView.as_view(),       name='api_report_assign'),

    # ── Usuarios ────────────────────────────────────────────────────────────
    path('usuarios/',           views.UserListView.as_view(),   name='api_users'),

    # ── Swagger / OpenAPI ────────────────────────────────────────────────────
    path('schema/',             SpectacularAPIView.as_view(),   name='api_schema'),
    path('docs/',               SpectacularSwaggerView.as_view(url_name='api_schema'), name='api_swagger'),
    path('redoc/',              SpectacularRedocView.as_view(url_name='api_schema'),   name='api_redoc'),
]
