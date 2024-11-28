import random
from datetime import date, time

import factory
from django.test import TestCase
from factory import Faker

from apps.entities.choices import EntityTypesChoices
from apps.entities.tests.factories import EntityFactory
from apps.reservations.choices import (
    ActivityTypeChoices,
    ReservationTypeChoices,
)
from apps.reservations.models import Reservation
from apps.reservations.services import get_total_price
from apps.reservations.tests.factories import ReservationFactory
from apps.rooms.choices import RoomTypeChoices
from apps.rooms.tests.factories import RoomFactory
from apps.users.tests.factories import UserFactory


class ServicesTest(TestCase):
    def setUp(self):
        self.room = RoomFactory(
            name=factory.Sequence(lambda n: f"Room test {n}-{random.randint(0, 1000)}"),
            room_type=RoomTypeChoices.EVENT_ROOM,
            price=10.0,
            price_half_day=30.0,
            price_all_day=50.0,
            capacity=10,
            description="Description test",
            equipment="Equipment test",
        )
        self.entity = EntityFactory(
            entity_email=Faker("email"),
            fiscal_name=Faker("company"),
            nif=factory.Faker("numerify", text="########"),
            town="Barcelona",
            postal_code=int("08080"),
            address="Address Test",
            country="Country Test",
            entity_type=EntityTypesChoices.HOSTED,
            reservation_privilege=True,
        )
        self.reservation = ReservationFactory(
            title="Title test",
            reservation_type=ReservationTypeChoices.HOURLY,
            date=date(2025, 12, 25),
            start_time=time(8, 0),
            end_time=time(12, 0),
            assistants=10,
            room=self.room,
            notes="Test notes",
            activity_type=ActivityTypeChoices.ATENEU,
            privacy=Reservation.PrivacyChoices.PRIVATE,
            status=Reservation.StatusChoices.CONFIRMED,
            entity=self.entity,
            reserved_by=UserFactory(),
        )

    def test_get_total_price(self):
        with self.subTest("Hosted Entity (40%) | 4hr Hourly reservation (10€/h)"):
            result = get_total_price(self.reservation)
            self.assertEqual(result, 24)
