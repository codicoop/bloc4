from django.test import TestCase

from apps.entities.models import Entity
from apps.entities.tests.factories import EntityFactory
from apps.provinces_towns.models import Town
from apps.users.models import User


class EntityTest(TestCase):
    def setUp(self):
        self.full_data = EntityFactory(
            email="mock@tests.tests",
            fiscal_name="Entity Test",
            nif="12345678X",
            town=Town.objects.filter(name="Barcelona").first(),
            postal_code=int("08080"),
            address="Address Test",
            country="Country Test",
            person_responsible=User.objects.create_user(
                name="Andrew",
                surnames="McTest",
                email="andrew@codi.coop",
                password="0pl#9okm8ijn",
                email_verification_code="1234",
                email_verified=True,
                is_active=True,
                is_staff=True,
                is_superuser=True,
            ),
            is_resident=True,
        )
        self.empty_data = EntityFactory(
            email="",
            fiscal_name="",
            nif="",
            town=Town.objects.filter(name="Barcelona").first(),
            postal_code=int("08080"),
            address="",
            country="",
            person_responsible=User.objects.create_user(
                name="Tom",
                surnames="McTest",
                email="Tom@codi.coop",
                password="0pl#9okm8ijn",
                email_verification_code="1234",
                email_verified=True,
                is_active=True,
                is_staff=True,
                is_superuser=True,
            ),
        )

    def test_save(self):
        with self.subTest("Full_data"):
            self.assertIsInstance(self.full_data, Entity)
            self.assertEqual(self.full_data.email, "mock@tests.tests")
            self.assertEqual(self.full_data.fiscal_name, "Entity Test")
            self.assertEqual(self.full_data.nif, "12345678X")
            self.assertEqual(self.full_data.town.name, "Barcelona")
            self.assertEqual(self.full_data.town.county.name, "Barcelonès ")
            self.assertEqual(self.full_data.town.county.province.name, "Barcelona")
            self.assertEqual(self.full_data.postal_code, int("08080"))
            self.assertEqual(self.full_data.address, "Address Test")
            self.assertEqual(self.full_data.country, "Country Test")
            self.assertEqual(self.full_data.person_responsible.name, "Andrew")
            self.assertEqual(self.full_data.person_responsible.surnames, "McTest")
            self.assertTrue(self.full_data.is_resident)

        with self.subTest("Empty_data"):
            self.assertIsInstance(self.empty_data, Entity)
            self.assertEqual(self.empty_data.email, "")
            self.assertEqual(self.empty_data.fiscal_name, "")
            self.assertEqual(self.empty_data.nif, "")
            self.assertEqual(self.empty_data.town.name, "Barcelona")
            self.assertEqual(self.empty_data.town.county.name, "Barcelonès ")
            self.assertEqual(self.empty_data.town.county.province.name, "Barcelona")
            self.assertEqual(self.empty_data.postal_code, int("08080"))
            self.assertEqual(self.empty_data.address, "")
            self.assertEqual(self.empty_data.country, "")
            self.assertEqual(self.empty_data.person_responsible.name, "Tom")
            self.assertEqual(self.empty_data.person_responsible.surnames, "McTest")
            self.assertFalse(self.empty_data.is_resident)
