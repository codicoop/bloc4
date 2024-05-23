from factory.django import DjangoModelFactory

from apps.entities.models import Entity
from apps.provinces_towns.models import Town
from apps.users.tests.factories import UserManagerFactory, UserFactory


class EntityFactory(DjangoModelFactory):
    email = "factory@test_email"
    fiscal_name = "fiscal_name_test"
    nif = "12345678M"
    town = Town.objects.filter(name="Barcelona").first()
    postal_code = int("08080")
    address = "Address Test"
    country = "Country Test"
    person_responsible = UserFactory()

    class Meta:
        model = Entity
