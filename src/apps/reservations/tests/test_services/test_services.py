from datetime import date, time

from django.test import TestCase

from apps.entities.tests.factories import (
    EntityFactory,
)
from apps.reservations.choices import (
    ActivityTypeChoices,
    ReservationTypeChoices,
)
from apps.reservations.models import Reservation
from apps.reservations.tests.factories import ReservationFactory
from apps.rooms.tests.factories import RoomFactory
from apps.users.tests.factories import UserFactory


class ServicesTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.room = RoomFactory()
        self.entity = EntityFactory()
        self.reservation = ReservationFactory(
            title="Title test",
            reservation_type=ReservationTypeChoices.HOURLY,
            date=date(2024, 12, 25),
            start_time=time(9, 0),
            end_time=time(9, 0),
            assistants=10,
            room=self.room,
            notes="Blablabla",
            activity_type=ActivityTypeChoices.ATENEU,
            privacy=Reservation.PrivacyChoices.PRIVATE,
            status=Reservation.StatusChoices.CONFIRMED,
            entity=self.entity,
            reserved_by=self.user,
            total_price=0,
        )

    def test_get_monthly_bonus(self):
        print("self", self)
