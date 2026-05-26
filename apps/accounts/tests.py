from django.test import TestCase
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
