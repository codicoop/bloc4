from django.test import TestCase

from apps.entities.choices import EntityTypesChoices
from apps.entities.models import Entity
from apps.entities.tests.factories import EntityFactory
from apps.users.models import User


class EntityTest(TestCase):
    def setUp(self):
        self.full_data = EntityFactory(
            entity_email="mock@tests.tests",
            fiscal_name="Entity Test",
            nif="12345678X",
            town="Barcelona",
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
            entity_type=EntityTypesChoices.HOSTED
        )
        self.empty_data = EntityFactory(
            entity_email="",
            fiscal_name="",
            nif="",
            town="Barcelona",
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
            entity_type=""

        )

    def test_save(self):
        with self.subTest("Full_data"):
            self.assertIsInstance(self.full_data, Entity)
            self.assertEqual(self.full_data.entity_email, "mock@tests.tests")
            self.assertEqual(self.full_data.fiscal_name, "Entity Test")
            self.assertEqual(self.full_data.nif, "12345678X")
            self.assertEqual(self.full_data.town, "Barcelona")
            self.assertEqual(self.full_data.postal_code, int("08080"))
            self.assertEqual(self.full_data.address, "Address Test")
            self.assertEqual(self.full_data.country, "Country Test")
            self.assertEqual(self.full_data.person_responsible.name, "Andrew")
            self.assertEqual(self.full_data.person_responsible.surnames, "McTest")
            self.assertEqual(self.full_data.entity_type, EntityTypesChoices.HOSTED)

        with self.subTest("Empty_data"):
            self.assertIsInstance(self.empty_data, Entity)
            self.assertEqual(self.empty_data.entity_email, "")
            self.assertEqual(self.empty_data.fiscal_name, "")
            self.assertEqual(self.empty_data.nif, "")
            self.assertEqual(self.empty_data.town, "Barcelona")
            self.assertEqual(self.empty_data.postal_code, int("08080"))
            self.assertEqual(self.empty_data.address, "")
            self.assertEqual(self.empty_data.country, "")
            self.assertEqual(self.empty_data.person_responsible.name, "Tom")
            self.assertEqual(self.empty_data.person_responsible.surnames, "McTest")
            self.assertEqual(self.empty_data.entity_type, "")

