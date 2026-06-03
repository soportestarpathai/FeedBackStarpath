from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from apps.accounts.models import CustomUser
from apps.platforms.models import Platform
from apps.reports.models import Report, StatusHistory


class Command(BaseCommand):
    help = 'Crea datos de prueba para FeedbackEve'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de prueba...')

        # ── Plataformas ──────────────────────────────────────────────
        eve360, _ = Platform.objects.get_or_create(
            nombre='EVE 360',
            defaults={'descripcion': 'Plataforma principal de cumplimiento PLD', 'color': '#2563eb', 'activa': True}
        )
        evehr, _ = Platform.objects.get_or_create(
            nombre='EVE HR',
            defaults={'descripcion': 'Módulo de recursos humanos', 'color': '#059669', 'activa': True}
        )
        analytics, _ = Platform.objects.get_or_create(
            nombre='EVE Analytics',
            defaults={'descripcion': 'Módulo de análisis y reportes', 'color': '#9ca3af', 'activa': False}
        )
        self.stdout.write(self.style.SUCCESS('  Plataformas: OK'))

        # ── Usuarios ──────────────────────────────────────────────────
        def make_user(email, password, rol, first, last, platforms):
            base = email.split('@')[0]
            username = base
            n = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f'{base}{n}'; n += 1
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': first,
                    'last_name': last,
                    'rol': rol,
                    'is_active': True,
                }
            )
            if created:
                user.set_password(password)
                user.save()
            for p in platforms:
                user.plataformas_asignadas.add(p)
            return user

        sa    = make_user('superadmin@feedbackeve.mx', '1234', CustomUser.SUPERADMIN, 'Super', 'Admin', [eve360, evehr, analytics])
        admin = make_user('admin@eve360.mx',           '1234', CustomUser.ADMIN,      'Juan',  'Admin', [eve360])
        tester= make_user('tester@eve360.mx',          '1234', CustomUser.TESTER,     'Laura', 'Torres', [eve360])
        usuario=make_user('usuario@eve360.mx',         '1234', CustomUser.USUARIO,    'Roberto','López', [eve360])
        self.stdout.write(self.style.SUCCESS('  Usuarios: OK'))

        # ── Reportes ──────────────────────────────────────────────────
        REPORTES = [
            {
                'titulo': 'Login falla en Safari 17',
                'descripcion': 'Al intentar iniciar sesión con Safari 17, la página queda en blanco y no redirige al dashboard.',
                'plataforma': eve360, 'tipo': Report.BUG, 'severidad': Report.ALTA,
                'estado': Report.ABIERTO, 'reportado_por': usuario,
                'url_pagina': 'https://app.eve360.mx/login',
                'navegador': 'Safari 17.2', 'sistema_operativo': 'macOS Sonoma 14.4',
            },
            {
                'titulo': 'Exportar no responde en Firefox',
                'descripcion': 'El botón de exportar PDF no genera el archivo cuando se usa Firefox 122.',
                'plataforma': eve360, 'tipo': Report.BUG, 'severidad': Report.CRITICA,
                'estado': Report.EN_REVISION, 'reportado_por': tester, 'asignado_a': tester,
                'pasos_reproducir': '1. Ir a Exportar PDF\n2. Seleccionar filtros\n3. Click en Generar\n4. Sin respuesta',
                'resultado_esperado': 'Descarga del PDF',
                'resultado_obtenido': 'Spinner infinito',
                'navegador': 'Firefox 122', 'sistema_operativo': 'Windows 11',
                'requisitos_funcionales': ['El sistema debe generar el PDF en menos de 10 segundos'],
            },
            {
                'titulo': 'Agregar filtro por departamento',
                'descripcion': 'Sería muy útil poder filtrar reportes por departamento de la empresa.',
                'plataforma': eve360, 'tipo': Report.SUGERENCIA, 'severidad': Report.BAJA,
                'estado': Report.ABIERTO, 'reportado_por': usuario,
            },
            {
                'titulo': 'Error en carga de imagen de perfil',
                'descripcion': 'Las imágenes de más de 2MB no se cargan correctamente.',
                'plataforma': evehr, 'tipo': Report.BUG, 'severidad': Report.MEDIA,
                'estado': Report.RESUELTO, 'reportado_por': tester, 'asignado_a': tester,
                'navegador': 'Chrome 121', 'sistema_operativo': 'Windows 10',
            },
            {
                'titulo': 'Dashboard muy lento con 500+ usuarios',
                'descripcion': 'El dashboard tarda más de 15 segundos en cargar cuando hay más de 500 usuarios activos.',
                'plataforma': eve360, 'tipo': Report.QUEJA, 'severidad': Report.ALTA,
                'estado': Report.CERRADO, 'reportado_por': usuario,
                'requisitos_no_funcionales': [
                    {'categoria': 'Rendimiento', 'descripcion': 'El dashboard debe cargar en menos de 3 segundos'},
                    {'categoria': 'Escalabilidad', 'descripcion': 'Soportar al menos 1000 usuarios concurrentes'},
                ],
            },
            {
                'titulo': 'Módulo de vacaciones no calcula correctamente',
                'descripcion': 'Los días de vacaciones proporcionales no se calculan bien para empleados de menos de 1 año.',
                'plataforma': evehr, 'tipo': Report.BUG, 'severidad': Report.ALTA,
                'estado': Report.ABIERTO, 'reportado_por': tester,
                'pasos_reproducir': '1. Ir a RRHH > Vacaciones\n2. Seleccionar empleado con menos de 12 meses\n3. Calcular días disponibles',
                'resultado_esperado': 'Días proporcionales correctos',
                'resultado_obtenido': 'Muestra 0 días disponibles',
            },
            {
                'titulo': 'Botón "Nuevo reporte" duplicado en móvil',
                'descripcion': 'En resoluciones menores a 375px aparecen dos botones de "Nuevo reporte".',
                'plataforma': eve360, 'tipo': Report.BUG, 'severidad': Report.BAJA,
                'estado': Report.RESUELTO, 'reportado_por': usuario,
                'navegador': 'Chrome Mobile', 'sistema_operativo': 'Android 14',
            },
            {
                'titulo': 'Añadir modo oscuro al dashboard',
                'descripcion': 'Muchos usuarios trabajan de noche y sería bueno tener un modo oscuro.',
                'plataforma': eve360, 'tipo': Report.SUGERENCIA, 'severidad': Report.BAJA,
                'estado': Report.ABIERTO, 'reportado_por': usuario,
            },
            {
                'titulo': 'Notificaciones por email no llegan',
                'descripcion': 'Las notificaciones automáticas cuando se cambia el estado de un reporte no llegan al correo.',
                'plataforma': evehr, 'tipo': Report.BUG, 'severidad': Report.MEDIA,
                'estado': Report.EN_REVISION, 'reportado_por': tester, 'asignado_a': tester,
            },
            {
                'titulo': 'Tiempo de sesión muy corto',
                'descripcion': 'La sesión expira después de 15 minutos de inactividad, lo que es muy poco para el flujo de trabajo.',
                'plataforma': eve360, 'tipo': Report.QUEJA, 'severidad': Report.MEDIA,
                'estado': Report.ABIERTO, 'reportado_por': usuario,
            },
        ]

        created_count = 0
        for i, data in enumerate(REPORTES):
            if Report.objects.filter(titulo=data['titulo']).exists():
                continue
            r = Report.objects.create(
                titulo=data['titulo'],
                descripcion=data['descripcion'],
                plataforma=data['plataforma'],
                tipo=data['tipo'],
                severidad=data['severidad'],
                estado=data['estado'],
                url_pagina=data.get('url_pagina', ''),
                pasos_reproducir=data.get('pasos_reproducir', ''),
                resultado_esperado=data.get('resultado_esperado', ''),
                resultado_obtenido=data.get('resultado_obtenido', ''),
                navegador=data.get('navegador', ''),
                sistema_operativo=data.get('sistema_operativo', ''),
                requisitos_funcionales=data.get('requisitos_funcionales', []),
                requisitos_no_funcionales=data.get('requisitos_no_funcionales', []),
                reportado_por=data['reportado_por'],
                asignado_a=data.get('asignado_a'),
                creado_en=timezone.now() - timedelta(days=random.randint(1, 30)),
            )
            # Crear historial para estados no ABIERTO
            if r.estado == Report.EN_REVISION:
                StatusHistory.objects.create(
                    reporte=r, estado_anterior=Report.ABIERTO,
                    estado_nuevo=Report.EN_REVISION, cambiado_por=admin,
                    nota='Tomado para revisión',
                    fecha=r.creado_en + timedelta(hours=random.randint(2, 24)),
                )
            elif r.estado == Report.RESUELTO:
                StatusHistory.objects.create(
                    reporte=r, estado_anterior=Report.ABIERTO,
                    estado_nuevo=Report.EN_REVISION, cambiado_por=admin,
                    fecha=r.creado_en + timedelta(hours=4),
                )
                StatusHistory.objects.create(
                    reporte=r, estado_anterior=Report.EN_REVISION,
                    estado_nuevo=Report.RESUELTO, cambiado_por=tester,
                    nota='Solucionado y verificado',
                    fecha=r.creado_en + timedelta(hours=48),
                )
            elif r.estado == Report.CERRADO:
                StatusHistory.objects.create(
                    reporte=r, estado_anterior=Report.ABIERTO,
                    estado_nuevo=Report.RESUELTO, cambiado_por=admin,
                    fecha=r.creado_en + timedelta(hours=6),
                )
                StatusHistory.objects.create(
                    reporte=r, estado_anterior=Report.RESUELTO,
                    estado_nuevo=Report.CERRADO, cambiado_por=admin,
                    nota='Cerrado tras verificación',
                    fecha=r.creado_en + timedelta(hours=72),
                )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'  Reportes: {created_count} creados'))
        self.stdout.write(self.style.SUCCESS('\nDatos de prueba listos. Credenciales:'))
        self.stdout.write('  superadmin@feedbackeve.mx / 1234')
        self.stdout.write('  admin@eve360.mx           / 1234')
        self.stdout.write('  tester@eve360.mx          / 1234')
        self.stdout.write('  usuario@eve360.mx         / 1234')
