from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
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
@permission_classes([AllowAny])
def api_root(request):
    base = request.build_absolute_uri('/api/v1/')
    return Response({
        'docs':   base + 'docs/',
        'redoc':  base + 'redoc/',
        'schema': base + 'schema/',
        'auth': {
            'token':         base + 'auth/token/',
            'token_refresh': base + 'auth/token/refresh/',
            'me':            base + 'auth/me/',
        },
        'reportes': {
            'list':    base + 'reportes/',
            'crear':   base + 'reportes/crear/',
            'detalle': base + 'reportes/{id}/',
            'editar':  base + 'reportes/{id}/editar/',
            'eliminar':base + 'reportes/{id}/eliminar/',
            'estado':  base + 'reportes/{id}/estado/',
            'asignar': base + 'reportes/{id}/asignar/',
        },
        'plataformas': {
            'list':    base + 'plataformas/',
            'crear':   base + 'plataformas/crear/',
            'editar':  base + 'plataformas/{id}/editar/',
            'eliminar':base + 'plataformas/{id}/eliminar/',
            'toggle':  base + 'plataformas/{id}/toggle/',
        },
        'usuarios': {
            'list':       base + 'usuarios/',
            'detalle':    base + 'usuarios/{id}/',
            'editar':     base + 'usuarios/{id}/editar/',
            'desactivar': base + 'usuarios/{id}/desactivar/',
        },
    })


# ── Auth info ─────────────────────────────────────────────────────────────────

@extend_schema(tags=['auth'], summary='Información del usuario autenticado')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)


# ── Plataformas ───────────────────────────────────────────────────────────────

class PlatformListView(generics.ListAPIView):
    serializer_class   = PlatformSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['plataformas'], summary='Listar plataformas del usuario')
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

    @extend_schema(tags=['plataformas'], summary='Crear plataforma (solo SuperAdmin)')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return Platform.objects.all()


class PlatformUpdateView(generics.UpdateAPIView):
    serializer_class   = PlatformSerializer
    permission_classes = [IsSuperAdmin]
    queryset           = Platform.objects.all()

    @extend_schema(tags=['plataformas'], summary='Editar plataforma completa (PUT)')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(tags=['plataformas'], summary='Editar campos parciales de plataforma (PATCH)')
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class PlatformDeleteView(generics.DestroyAPIView):
    serializer_class   = PlatformSerializer
    permission_classes = [IsSuperAdmin]
    queryset           = Platform.objects.all()

    @extend_schema(tags=['plataformas'], summary='Eliminar plataforma (solo SuperAdmin)')
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class PlatformToggleView(APIView):
    permission_classes = [IsSuperAdmin]

    @extend_schema(
        tags=['plataformas'],
        summary='Activar / desactivar plataforma',
        responses={200: PlatformSerializer},
    )
    def post(self, request, pk):
        platform = generics.get_object_or_404(Platform, pk=pk)
        platform.activa = not platform.activa
        platform.save()
        return Response(PlatformSerializer(platform).data)


# ── Reportes ──────────────────────────────────────────────────────────────────

class ReportListView(generics.ListAPIView):
    serializer_class   = ReportListSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['reportes'],
        summary='Listar reportes según rol del usuario',
        parameters=[
            OpenApiParameter('tipo',      description='BUG | SUGERENCIA | QUEJA'),
            OpenApiParameter('estado',    description='ABIERTO | EN_REVISION | RESUELTO | CERRADO'),
            OpenApiParameter('severidad', description='BAJA | MEDIA | ALTA | CRITICA'),
            OpenApiParameter('q',         description='Búsqueda por título'),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs   = Report.objects.select_related('plataforma', 'reportado_por', 'asignado_a')
        if user.rol == CustomUser.USUARIO:
            qs = qs.filter(reportado_por=user)
        elif user.rol in (CustomUser.TESTER, CustomUser.ADMIN):
            ids = user.plataformas_asignadas.values_list('id', flat=True)
            qs  = qs.filter(plataforma_id__in=ids)
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

    @extend_schema(tags=['reportes'], summary='Ver detalle completo de un reporte')
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


class ReportUpdateView(generics.UpdateAPIView):
    serializer_class   = ReportCreateSerializer
    permission_classes = [IsTesterOrAbove]

    @extend_schema(tags=['reportes'], summary='Editar reporte completo (PUT)')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(tags=['reportes'], summary='Editar campos parciales del reporte (PATCH)')
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs   = Report.objects.all()
        if user.rol == CustomUser.TESTER:
            return qs.filter(reportado_por=user)
        if user.rol == CustomUser.ADMIN:
            ids = user.plataformas_asignadas.values_list('id', flat=True)
            return qs.filter(plataforma_id__in=ids)
        return qs


class ReportDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminOrAbove]

    @extend_schema(tags=['reportes'], summary='Eliminar reporte (Admin o SuperAdmin)')
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs   = Report.objects.all()
        if user.rol == CustomUser.ADMIN:
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
        report = generics.get_object_or_404(Report, pk=pk)
        user   = request.user
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
        summary='Asignar o desasignar tester en un reporte',
        request={'application/json': {'type': 'object', 'properties': {
            'tester_id': {'type': 'integer', 'description': 'ID del tester. Enviar null para desasignar.'}
        }}},
        responses={200: ReportDetailSerializer},
    )
    def post(self, request, pk):
        report    = generics.get_object_or_404(Report, pk=pk)
        tester_id = request.data.get('tester_id')
        if tester_id:
            tester = generics.get_object_or_404(CustomUser, pk=tester_id, rol=CustomUser.TESTER)
            report.asignado_a = tester
        else:
            report.asignado_a = None
        report.save()
        return Response(ReportDetailSerializer(report, context={'request': request}).data)


# ── Usuarios ──────────────────────────────────────────────────────────────────

class UserListView(generics.ListAPIView):
    serializer_class   = UserSerializer
    permission_classes = [IsAdminOrAbove]

    @extend_schema(
        tags=['usuarios'],
        summary='Listar usuarios (Admin ve su plataforma, SuperAdmin ve todos)',
        parameters=[
            OpenApiParameter('rol', description='USUARIO | TESTER | ADMIN | SUPERADMIN'),
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


class UserDetailView(generics.RetrieveAPIView):
    serializer_class   = UserSerializer
    permission_classes = [IsAdminOrAbove]
    queryset           = CustomUser.objects.all()

    @extend_schema(tags=['usuarios'], summary='Ver detalle de un usuario')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserUpdateView(generics.UpdateAPIView):
    serializer_class   = UserSerializer
    permission_classes = [IsAdminOrAbove]
    queryset           = CustomUser.objects.all()

    @extend_schema(tags=['usuarios'], summary='Editar rol o datos de usuario (PUT)')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(tags=['usuarios'], summary='Editar campos parciales de usuario (PATCH)')
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        user    = self.request.user
        instance= serializer.instance
        nuevo_rol = serializer.validated_data.get('rol', instance.rol)
        if user.rol == CustomUser.ADMIN and nuevo_rol in (CustomUser.ADMIN, CustomUser.SUPERADMIN):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('No puedes asignar rol Admin o SuperAdmin.')
        serializer.save()


class UserDeactivateView(APIView):
    permission_classes = [IsAdminOrAbove]

    @extend_schema(
        tags=['usuarios'],
        summary='Activar o desactivar cuenta de usuario',
        responses={200: UserSerializer},
    )
    def post(self, request, pk):
        user = generics.get_object_or_404(CustomUser, pk=pk)
        if user.rol in (CustomUser.ADMIN, CustomUser.SUPERADMIN) and request.user.rol == CustomUser.ADMIN:
            return Response({'detail': 'No puedes desactivar a un Admin o SuperAdmin.'}, status=403)
        user.is_active = not user.is_active
        user.save()
        return Response(UserSerializer(user).data)
