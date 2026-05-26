from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User

class UserModelTest(TestCase):
    def test_create_user_with_rol(self):
        user = User.objects.create_user(
            username='tester1',
            email='tester@example.com',
            password='pass1234',
            rol=User.TESTER,
        )
        self.assertEqual(user.rol, User.TESTER)
        self.assertEqual(user.email, 'tester@example.com')

    def test_default_rol_is_usuario(self):
        user = User.objects.create_user(
            username='u1',
            email='u1@example.com',
            password='pass1234',
        )
        self.assertEqual(user.rol, User.USUARIO)

    def test_is_admin_property(self):
        admin = User.objects.create_user(
            username='adm',
            email='adm@example.com',
            password='p',
            rol=User.ADMIN,
        )
        self.assertTrue(admin.is_admin)
        self.assertFalse(admin.is_tester)

    def test_is_tester_property(self):
        tester = User.objects.create_user(
            username='tst',
            email='tst@example.com',
            password='p',
            rol=User.TESTER,
        )
        self.assertTrue(tester.is_tester)
        self.assertFalse(tester.is_admin)


class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='gustavo',
            email='gustavo@test.com',
            password='testpass123',
        )

    def test_login_page_loads(self):
        r = self.client.get(reverse('login'))
        self.assertEqual(r.status_code, 200)

    def test_login_with_valid_credentials(self):
        r = self.client.post(reverse('login'), {
            'email': 'gustavo@test.com',
            'password': 'testpass123',
        })
        self.assertRedirects(r, '/', fetch_redirect_response=False)

    def test_login_with_wrong_password(self):
        r = self.client.post(reverse('login'), {
            'email': 'gustavo@test.com',
            'password': 'wrong',
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Credenciales incorrectas')

    def test_register_creates_user_as_usuario(self):
        r = self.client.post(reverse('register'), {
            'username': 'nuevo',
            'email': 'nuevo@test.com',
            'password1': 'Seguro123!',
            'password2': 'Seguro123!',
        })
        self.assertRedirects(r, '/login/')
        u = User.objects.get(email='nuevo@test.com')
        self.assertEqual(u.rol, User.USUARIO)

    def test_logout_redirects(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse('logout'))
        self.assertRedirects(r, '/login/')
