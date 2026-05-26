from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.platforms.models import Platform

class PlatformModelTest(TestCase):
    def test_create_platform(self):
        p = Platform.objects.create(nombre='EVE 360', color='#0ea5e9')
        self.assertEqual(str(p), 'EVE 360')
        self.assertTrue(p.activa)

class PlatformCRUDTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='adm', email='adm@t.com', password='p', rol=User.ADMIN)
        self.client.force_login(self.admin)

    def test_list_platforms(self):
        Platform.objects.create(nombre='EVE 360', color='#0ea5e9')
        r = self.client.get(reverse('admin_platforms'))
        self.assertContains(r, 'EVE 360')

    def test_create_platform_post(self):
        r = self.client.post(reverse('admin_platforms'), {
            'nombre': 'Medical', 'color': '#a855f7', 'descripcion': 'Consultorio',
        })
        self.assertEqual(Platform.objects.filter(nombre='Medical').count(), 1)

    def test_toggle_platform_active(self):
        p = Platform.objects.create(nombre='Órbita', color='#f97316', activa=True)
        self.client.post(reverse('platform_toggle', args=[p.pk]))
        p.refresh_from_db()
        self.assertFalse(p.activa)
