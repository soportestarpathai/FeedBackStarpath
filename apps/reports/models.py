from django.db import models
from django.conf import settings

class Report(models.Model):
    BUG        = 'BUG'
    SUGERENCIA = 'SUGERENCIA'
    QUEJA      = 'QUEJA'
    TIPO_CHOICES = [(BUG,'Bug'),(SUGERENCIA,'Sugerencia'),(QUEJA,'Queja')]

    BAJA    = 'BAJA'
    MEDIA   = 'MEDIA'
    ALTA    = 'ALTA'
    CRITICA = 'CRITICA'
    SEV_CHOICES = [(BAJA,'Baja'),(MEDIA,'Media'),(ALTA,'Alta'),(CRITICA,'Crítica')]

    ABIERTO     = 'ABIERTO'
    EN_REVISION = 'EN_REVISION'
    RESUELTO    = 'RESUELTO'
    CERRADO     = 'CERRADO'
    ESTADO_CHOICES = [
        (ABIERTO,'Abierto'),(EN_REVISION,'En revisión'),
        (RESUELTO,'Resuelto'),(CERRADO,'Cerrado'),
    ]

    titulo             = models.CharField(max_length=200)
    descripcion        = models.TextField()
    plataforma         = models.ForeignKey('platforms.Platform', on_delete=models.CASCADE)
    tipo               = models.CharField(max_length=15, choices=TIPO_CHOICES)
    severidad          = models.CharField(max_length=10, choices=SEV_CHOICES, default=MEDIA)
    estado             = models.CharField(max_length=15, choices=ESTADO_CHOICES, default=ABIERTO)
    url_pagina         = models.URLField(blank=True)
    pasos_reproducir   = models.TextField(blank=True)
    resultado_esperado = models.TextField(blank=True)
    resultado_obtenido = models.TextField(blank=True)
    entorno            = models.JSONField(default=dict, blank=True)
    reportado_por      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creado_en          = models.DateTimeField(auto_now_add=True)
    actualizado_en     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return self.titulo

    def cambiar_estado(self, nuevo_estado, usuario):
        StatusHistory.objects.create(
            reporte=self,
            estado_anterior=self.estado,
            estado_nuevo=nuevo_estado,
            cambiado_por=usuario,
        )
        self.estado = nuevo_estado
        self.save()

class Screenshot(models.Model):
    reporte   = models.ForeignKey(Report, related_name='screenshots', on_delete=models.CASCADE)
    imagen    = models.ImageField(upload_to='screenshots/')
    subido_en = models.DateTimeField(auto_now_add=True)

class StatusHistory(models.Model):
    reporte         = models.ForeignKey(Report, related_name='historial', on_delete=models.CASCADE)
    estado_anterior = models.CharField(max_length=15)
    estado_nuevo    = models.CharField(max_length=15)
    cambiado_por    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha           = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
