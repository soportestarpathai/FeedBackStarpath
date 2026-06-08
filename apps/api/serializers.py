from rest_framework import serializers
from apps.accounts.models import CustomUser
from apps.platforms.models import Platform
from apps.reports.models import Report, Screenshot, StatusHistory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'rol', 'is_active']
        read_only_fields = ['id', 'email']


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Platform
        fields = ['id', 'nombre', 'descripcion', 'color', 'activa', 'creado_en']
        read_only_fields = ['id', 'creado_en']


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Screenshot
        fields = ['id', 'imagen', 'subido_en']
        read_only_fields = ['id', 'subido_en']


class StatusHistorySerializer(serializers.ModelSerializer):
    cambiado_por = serializers.StringRelatedField()

    class Meta:
        model  = StatusHistory
        fields = ['id', 'estado_anterior', 'estado_nuevo', 'cambiado_por', 'nota', 'fecha']
        read_only_fields = ['id', 'fecha']


class ReportListSerializer(serializers.ModelSerializer):
    plataforma    = serializers.StringRelatedField()
    reportado_por = serializers.StringRelatedField()
    asignado_a    = serializers.StringRelatedField()

    class Meta:
        model  = Report
        fields = [
            'id', 'titulo', 'plataforma', 'tipo', 'severidad', 'estado',
            'reportado_por', 'asignado_a', 'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']


class ReportDetailSerializer(serializers.ModelSerializer):
    plataforma    = PlatformSerializer(read_only=True)
    plataforma_id = serializers.PrimaryKeyRelatedField(
        queryset=Platform.objects.filter(activa=True), source='plataforma', write_only=True
    )
    reportado_por = UserSerializer(read_only=True)
    asignado_a    = UserSerializer(read_only=True)
    screenshots   = ScreenshotSerializer(many=True, read_only=True)
    historial     = StatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model  = Report
        fields = [
            'id', 'titulo', 'descripcion',
            'plataforma', 'plataforma_id',
            'tipo', 'severidad', 'estado',
            'url_pagina', 'pasos_reproducir',
            'resultado_esperado', 'resultado_obtenido',
            'navegador', 'sistema_operativo',
            'requisitos_funcionales', 'requisitos_no_funcionales',
            'reportado_por', 'asignado_a',
            'screenshots', 'historial',
            'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['id', 'reportado_por', 'creado_en', 'actualizado_en']


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Report
        fields = [
            'titulo', 'descripcion', 'plataforma', 'tipo', 'severidad',
            'url_pagina', 'pasos_reproducir', 'resultado_esperado',
            'resultado_obtenido', 'navegador', 'sistema_operativo',
            'requisitos_funcionales', 'requisitos_no_funcionales',
        ]

    def validate_severidad(self, value):
        user = self.context['request'].user
        if user.rol == CustomUser.USUARIO:
            return Report.MEDIA
        if user.rol == CustomUser.TESTER and value == Report.CRITICA:
            return Report.ALTA
        return value

    def create(self, validated_data):
        validated_data['reportado_por'] = self.context['request'].user
        return super().create(validated_data)


class EstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Report.ESTADO_CHOICES)
    nota   = serializers.CharField(required=False, allow_blank=True, default='')
