from factory.django import DjangoModelFactory

from apps.entities.choices import EntityTypesChoices
from apps.entities.models import Entity


class EntityFactory(DjangoModelFactory):
    entity_email = "factory@test_email"
    fiscal_name = "fiscal_name_test"
    nif = "12345678M"
    town = "Barcelona"
    postal_code = int("08080")
    address = "Address Test"
    country = "Country Test"
    entity_type = EntityTypesChoices.HOSTED

    class Meta:
        model = Entity
