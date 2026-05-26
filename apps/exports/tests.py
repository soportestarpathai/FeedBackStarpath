from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.platforms.models import Platform
from apps.reports.models import Report


class PDFExportTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='a', email='a@t.com', password='p', rol=User.ADMIN)
        self.usuario = User.objects.create_user(
            username='u', email='u@t.com', password='p', rol=User.USUARIO)
        self.plat = Platform.objects.create(nombre='EVE 360', color='#0ea5e9')
        Report.objects.create(
            titulo='Bug SAT', descripcion='desc',
            plataforma=self.plat, tipo=Report.BUG,
            severidad=Report.CRITICA, reportado_por=self.admin,
        )

    def test_pdf_form_loads_for_admin(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse('pdf_form'))
        self.assertEqual(r.status_code, 200)

    def test_pdf_form_blocked_for_usuario(self):
        self.client.force_login(self.usuario)
        r = self.client.get(reverse('pdf_form'))
        self.assertEqual(r.status_code, 403)

    def test_pdf_download_returns_pdf(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse('pdf_download'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/pdf')
        self.assertIn('attachment', r['Content-Disposition'])
