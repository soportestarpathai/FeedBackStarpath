from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.reports.models import Report, Screenshot, StatusHistory

class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='u', email='u@t.com', password='p')
        self.platform = Platform.objects.create(nombre='EVE 360', color='#0ea5e9')

    def test_create_report(self):
        r = Report.objects.create(
            titulo='Error en login',
            descripcion='No redirige',
            plataforma=self.platform,
            tipo=Report.BUG,
            severidad=Report.CRITICA,
            reportado_por=self.user,
        )
        self.assertEqual(r.estado, Report.ABIERTO)
        self.assertEqual(str(r), 'Error en login')

    def test_status_history_on_change(self):
        report = Report.objects.create(
            titulo='T', descripcion='D', plataforma=self.platform,
            tipo=Report.BUG, severidad=Report.ALTA, reportado_por=self.user,
        )
        report.cambiar_estado(Report.EN_REVISION, self.user)
        self.assertEqual(report.estado, Report.EN_REVISION)
        h = StatusHistory.objects.get(reporte=report)
        self.assertEqual(h.estado_anterior, Report.ABIERTO)
        self.assertEqual(h.estado_nuevo, Report.EN_REVISION)

class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='u', email='u@t.com', password='p', rol=User.USUARIO)
        self.admin = User.objects.create_user(
            username='a', email='a@t.com', password='p', rol=User.ADMIN)
        self.plat = Platform.objects.create(nombre='EVE 360', color='#0ea5e9')

    def test_dashboard_requires_login(self):
        r = self.client.get(reverse('dashboard'))
        self.assertRedirects(r, '/login/?next=/')

    def test_dashboard_usuario_sees_only_own_reports(self):
        other = User.objects.create_user(username='o', email='o@t.com', password='p')
        Report.objects.create(titulo='Mío', descripcion='d',
            plataforma=self.plat, tipo=Report.BUG, severidad=Report.ALTA,
            reportado_por=self.user)
        Report.objects.create(titulo='Otro', descripcion='d',
            plataforma=self.plat, tipo=Report.BUG, severidad=Report.ALTA,
            reportado_por=other)
        self.client.force_login(self.user)
        r = self.client.get(reverse('dashboard'))
        self.assertContains(r, 'Mío')
        self.assertNotContains(r, 'Otro')

    def test_dashboard_admin_sees_all_reports(self):
        Report.objects.create(titulo='Mío', descripcion='d',
            plataforma=self.plat, tipo=Report.BUG, severidad=Report.ALTA,
            reportado_por=self.user)
        self.client.force_login(self.admin)
        r = self.client.get(reverse('dashboard'))
        self.assertContains(r, 'Mío')

    def test_htmx_filter_by_platform(self):
        plat2 = Platform.objects.create(nombre='Medical', color='#a855f7')
        Report.objects.create(titulo='EVE bug', descripcion='d',
            plataforma=self.plat, tipo=Report.BUG, severidad=Report.ALTA,
            reportado_por=self.admin)
        Report.objects.create(titulo='Medical bug', descripcion='d',
            plataforma=plat2, tipo=Report.BUG, severidad=Report.ALTA,
            reportado_por=self.admin)
        self.client.force_login(self.admin)
        r = self.client.get(
            reverse('reports_table'),
            {'plataforma': self.plat.pk},
            HTTP_HX_REQUEST='true',
        )
        self.assertContains(r, 'EVE bug')
        self.assertNotContains(r, 'Medical bug')
