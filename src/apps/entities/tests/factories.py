import factory
from factory.django import DjangoModelFactory

from apps.entities.choices import EntityTypesChoices
from apps.entities.models import Entity, EntityPrivilege, MonthlyBonus


class EntityFactory(DjangoModelFactory):
    entity_email = "factory@test_email.com"
    fiscal_name = "fiscal_name_test"
    nif = "12345678M"
    town = "Barcelona"
    postal_code = int("08080")
    address = "Address Test"
    country = "Country Test"
    entity_type = EntityTypesChoices.HOSTED

    class Meta:
        model = Entity


class EntityPrivilegeFactory(DjangoModelFactory):
    entity = factory.SubFactory(EntityFactory)

    class Meta:
        model = EntityPrivilege


class MonthlyBonusFactory(DjangoModelFactory):
    entity = factory.SubFactory(EntityFactory)

    class Meta:
        model = MonthlyBonus
