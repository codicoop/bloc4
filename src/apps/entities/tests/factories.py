from factory.django import DjangoModelFactory

from apps.entities.models import Entity, EntityPrivilege, MonthlyBonus


class EntityFactory(DjangoModelFactory):
    class Meta:
        model = Entity


class EntityPrivilegeFactory(DjangoModelFactory):
    class Meta:
        model = EntityPrivilege


class MonthlyBonusFactory(DjangoModelFactory):
    class Meta:
        model = MonthlyBonus
