from factory.django import DjangoModelFactory

from apps.entities.models import Entity, EntityPrivilege, MonthlyBonus
from apps.reservations.models import Reservation
from apps.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User


class EntityFactory(DjangoModelFactory):
    class Meta:
        model = Entity


class EntityPrivilegeFactory(DjangoModelFactory):
    class Meta:
        model = EntityPrivilege


class MonthlyBonusFactory(DjangoModelFactory):
    class Meta:
        model = MonthlyBonus


class ReservationFactory(DjangoModelFactory):
    class Meta:
        model = Reservation
