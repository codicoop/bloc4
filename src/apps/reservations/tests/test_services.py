from datetime import date, time

from django.test import TestCase

from apps.entities.choices import EntityTypesChoices
from apps.entities.tests.factories import EntityFactory
from apps.reservations.choices import (
    ReservationTypeChoices,
)
from apps.reservations.services import get_total_price
from apps.reservations.tests.factories import ReservationFactory
from apps.rooms.tests.factories import RoomFactory
from apps.users.tests.factories import UserFactory


class ServicesTest(TestCase):
    def setUp(self):
        self.room = RoomFactory(
            price=10.0,
            price_half_day=30.0,
            price_all_day=50.0,
        )
        self.entity = EntityFactory(
            entity_type=EntityTypesChoices.HOSTED,
        )
        self.reservation = ReservationFactory(
            reservation_type=ReservationTypeChoices.HOURLY,
            date=date(2025, 12, 25),
            start_time=time(8, 0),
            end_time=time(12, 0),
            assistants=10,
            room=self.room,
            entity=self.entity,
            reserved_by=UserFactory(),
        )

    def test_get_total_price(self):
        with self.subTest("Hosted Entity (40%) | 4hr Hourly reservation (10€/h)"):
            result = get_total_price(self.reservation)
            self.assertEqual(result, 24)
        with self.subTest("Bloc4 Entity (50%) | Morning reservation (30€/h)"):
            self.entity.entity_type = EntityTypesChoices.BLOC4
            self.reservation.reservation_type = ReservationTypeChoices.MORNING
            result = get_total_price(self.reservation)
            self.assertEqual(result, 15)
        with self.subTest("General Entity (0%) | Afternoon reservation (30€/h)"):
            self.entity.entity_type = EntityTypesChoices.GENERAL
            self.reservation.reservation_type = ReservationTypeChoices.AFTERNOON
            result = get_total_price(self.reservation)
            self.assertEqual(result, 30)
        with self.subTest("Outside Entity (+15%) | Whole day reservation (50€/h)"):
            self.entity.entity_type = EntityTypesChoices.OUTSIDE
            self.reservation.reservation_type = ReservationTypeChoices.WHOLE_DAY
            result = get_total_price(self.reservation)
            self.assertEqual(result, 57.5)
