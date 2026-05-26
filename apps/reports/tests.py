from django.test import TestCase
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
