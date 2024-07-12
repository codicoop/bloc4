from django.test import TestCase
from django.utils.translation import gettext as _

from apps.entities.models import Entity
from apps.users.models import User


class UserManagerTestCase(TestCase):
    def setUp(self):
        self.entity = Entity.objects.filter(email="codi@codi.coop").first()
        self.user = User.objects.create_user(
            name="test_name",
            surnames="test_surnames",
            email="test_user@tests.com",
            password="test_password",
            entity=self.entity,
            is_janitor=True,
        )
        self.superuser = User.objects.create_superuser(
            name="test_name",
            surnames="test_surnames",
            email="test_superuser@tests.com",
            password="test_password",
            entity=self.entity,
            is_janitor=True,
            is_staff=True,
            is_superuser=True,
        )

    def test_create_user(self):
        """
        Test creates and saves a User with the given email, password
        and extra fields.
        """
        with self.subTest("User creation successfully"):
            self.assertEqual(self.user.name, "test_name")
            self.assertEqual(self.user.surnames, "test_surnames")
            self.assertEqual(self.user.email, "test_user@tests.com")
            self.assertEqual(self.user.email_verification_code, "0000")
            self.assertFalse(self.user.email_verified)
            self.assertEqual(self.user.entity.email, "codi@codi.coop")
            self.assertEqual(self.user.entity.fiscal_name, "Codi Cooperatiu SCCL")
            self.assertEqual(self.user.entity.nif, "F67151233")
            self.assertEqual(self.user.entity.town.name, "Barcelona")
            self.assertEqual(self.user.entity.postal_code, "08004")
            self.assertEqual(
                self.user.entity.address, "Carrer de Piquer, núm 27, Sobreatic 2º"
            )
            self.assertEqual(self.user.entity.country, "Spain")
            self.assertFalse(self.user.entity.is_resident)
            self.assertTrue(self.user.is_janitor)
            self.assertTrue(self.user.is_active)
            self.assertFalse(self.user.is_staff)
            self.assertTrue(self.user.check_password("test_password"))

        with self.subTest("User creation failed"):
            with self.assertRaises(ValueError) as error:
                self.user = User.objects.create_user(
                    name="test_name",
                    surnames="test_surnames",
                    email=None,
                    password="test_password",
                )
            self.assertEqual(
                str(error.exception), _("Users must have an email address")
            )

    def test_create_superuser(self):
        """
        Test creates and saves a superuser with the given email, password
        and extra fields.
        """
        with self.subTest("Superuser creation successfully"):
            self.assertTrue(self.user.is_janitor)
            self.assertTrue(self.superuser.is_staff)
            self.assertTrue(self.superuser.is_superuser)

        with self.subTest("Superuser creation failed"):
            with self.assertRaises(ValueError) as error:
                self.superuser = User.objects.create_superuser(
                    name="test_name",
                    surnames="test_surnames",
                    email="tests@tests.com",
                    password=None,
                    is_staff=True,
                    is_superuser=True,
                )
            self.assertEqual(str(error.exception), _("Superusers must have a password"))

    def test_full_name(self):
        """
        Tests the full_name property.
        """
        self.assertEqual(self.user.full_name, "test_name test_surnames")
