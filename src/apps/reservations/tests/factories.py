from datetime import date, time

from factory.django import DjangoModelFactory

from apps.entities.tests.factories import EntityFactory
from apps.reservations.choices import (
    ActivityTypeChoices,
    ReservationTypeChoices,
)
from apps.reservations.models import Reservation
from apps.rooms.tests.factories import RoomFactory
from apps.users.tests.factories import UserFactory


class ReservationFactory(DjangoModelFactory):
    class Meta:
        model = Reservation
