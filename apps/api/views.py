from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes as pc
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.accounts.models import CustomUser
from apps.platforms.models import Platform
from apps.reports.models import Report, StatusHistory
from .serializers import (
    PlatformSerializer, ReportListSerializer, ReportDetailSerializer,
    ReportCreateSerializer, EstadoSerializer, UserSerializer,
)
from .permissions import IsSuperAdmin, IsAdminOrAbove, IsTesterOrAbove


# ── API Root ─────────────────────────────────────────────────────────────────

@extend_schema(exclude=True)
@api_view(['GET'])
@pc([AllowAny])
def api_root(request):
    base = request.build_absolute_uri('/api/v1/')
    return Response({
        'docs':              base + 'docs/',
        'redoc':             base + 'redoc/',
        'schema':            base + 'schema/',
        'auth': {
            'token':         base + 'auth/token/',
            'token_refresh': base + 'auth/token/refresh/',
            'me':            base + 'auth/me/',
        },
        'reportes': {
            'list':          base + 'reportes/',
            'crear':         base + 'reportes/crear/',
            'detalle':       base + 'reportes/{id}/',
            'estado':        base + 'reportes/{id}/estado/',
            'asignar':       base + 'reportes/{id}/asignar/',
        },
        'plataformas': {
            'list':          base + 'plataformas/',
            'crear':         base + 'plataformas/crear/',
        },
        'usuarios': {
            'list':          base + 'usuarios/',
        },
    })


# ── Auth info ────────────────────────────────────────────────────────────────

@extend_schema(tags=['auth'], summary='Información del usuario autenticado')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)


# ── Plataformas ──────────────────────────────────────────────────────────────

class PlatformListView(generics.ListAPIView):
    serializer_class   = PlatformSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['plataformas'], summary='Listar plataformas')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.rol == CustomUser.SUPERADMIN:
            return Platform.objects.all()
        return user.plataformas_asignadas.all()


class PlatformCreateView(generics.CreateAPIView):
    serializer_class   = PlatformSerializer
    permission_classes = [IsSuperAdmin]

    @extend_schema(tags=['plataformas'], summary='Crear plataforma (SuperAdmin)')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return Platform.objects.all()


# ── Reportes ─────────────────────────────────────────────────────────────────

class ReportListView(generics.ListAPIView):
    serializer_class   = ReportListSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['reportes'],
        summary='Listar reportes según rol',
        parameters=[
            OpenApiParameter('tipo',      description='Filtrar por tipo: BUG, SUGERENCIA, QUEJA'),
            OpenApiParameter('estado',    description='Filtrar por estado: ABIERTO, EN_REVISION, RESUELTO, CERRADO'),
            OpenApiParameter('severidad', description='Filtrar por severidad: BAJA, MEDIA, ALTA, CRITICA'),
            OpenApiParameter('q',         description='Búsqueda por título'),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs = Report.objects.select_related('plataforma', 'reportado_por', 'asignado_a')

        if user.rol == CustomUser.USUARIO:
            qs = qs.filter(reportado_por=user)
        elif user.rol == CustomUser.TESTER:
            ids = user.plataformas_asignadas.values_list('id', flat=True)
            qs = qs.filter(plataforma_id__in=ids)
        elif user.rol == CustomUser.ADMIN:
            ids = user.plataformas_asignadas.values_list('id', flat=True)
            qs = qs.filter(plataforma_id__in=ids)

        q         = self.request.GET.get('q')
        tipo      = self.request.GET.get('tipo')
        estado    = self.request.GET.get('estado')
        severidad = self.request.GET.get('severidad')
        if q:         qs = qs.filter(titulo__icontains=q)
        if tipo:      qs = qs.filter(tipo=tipo)
        if estado:    qs = qs.filter(estado=estado)
        if severidad: qs = qs.filter(severidad=severidad)
        return qs


class ReportCreateView(generics.CreateAPIView):
    serializer_class   = ReportCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['reportes'], summary='Crear nuevo reporte')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ReportDetailView(generics.RetrieveAPIView):
    serializer_class   = ReportDetailSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['reportes'], summary='Detalle de un reporte')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs   = Report.objects.select_related('plataforma', 'reportado_por', 'asignado_a')
        if user.rol == CustomUser.USUARIO:
            return qs.filter(reportado_por=user)
        if user.rol in (CustomUser.TESTER, CustomUser.ADMIN):
            ids = user.plataformas_asignadas.values_list('id', flat=True)
            return qs.filter(plataforma_id__in=ids)
        return qs


class ReportChangeStatusView(APIView):
    permission_classes = [IsTesterOrAbove]

    @extend_schema(
        tags=['reportes'],
        summary='Cambiar estado de un reporte',
        request=EstadoSerializer,
        responses={200: ReportDetailSerializer},
    )
    def post(self, request, pk):
        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return Response({'detail': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.rol == CustomUser.TESTER and report.reportado_por != user:
            return Response({'detail': 'Solo puedes cambiar estado de tus propios reportes.'}, status=403)

        ser = EstadoSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        report.cambiar_estado(ser.validated_data['estado'], user, ser.validated_data.get('nota', ''))
        return Response(ReportDetailSerializer(report, context={'request': request}).data)


class ReportAssignView(APIView):
    permission_classes = [IsAdminOrAbove]

    @extend_schema(
        tags=['reportes'],
        summary='Asignar tester a un reporte',
        request={'application/json': {'type': 'object', 'properties': {'tester_id': {'type': 'integer'}}}},
        responses={200: ReportDetailSerializer},
    )
    def post(self, request, pk):
        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return Response({'detail': 'No encontrado.'}, status=404)

        tester_id = request.data.get('tester_id')
        if tester_id:
            try:
                tester = CustomUser.objects.get(pk=tester_id, rol=CustomUser.TESTER)
                report.asignado_a = tester
            except CustomUser.DoesNotExist:
                return Response({'detail': 'Tester no encontrado.'}, status=400)
        else:
            report.asignado_a = None
        report.save()
        return Response(ReportDetailSerializer(report, context={'request': request}).data)


# ── Usuarios ─────────────────────────────────────────────────────────────────

class UserListView(generics.ListAPIView):
    serializer_class   = UserSerializer
    permission_classes = [IsAdminOrAbove]

    @extend_schema(
        tags=['usuarios'],
        summary='Listar usuarios (Admin ve su plataforma, SA ve todos)',
        parameters=[
            OpenApiParameter('rol', description='Filtrar por rol: USUARIO, TESTER, ADMIN, SUPERADMIN'),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.rol == CustomUser.SUPERADMIN:
            qs = CustomUser.objects.all()
        else:
            ids = user.plataformas_asignadas.values_list('id', flat=True)
            qs  = CustomUser.objects.filter(plataformas_asignadas__in=ids).distinct()

        rol = self.request.GET.get('rol')
        if rol:
            qs = qs.filter(rol=rol)
        return qs.order_by('rol', 'email')
