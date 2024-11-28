from datetime import date, time

from django.test import TestCase

from apps.entities.choices import EntityTypesChoices
from apps.entities.tests.factories import EntityFactory, MonthlyBonusFactory
from apps.reservations.choices import ReservationTypeChoices
from apps.reservations.models import Reservation
from apps.reservations.services import get_monthly_bonus_totals, get_total_price
from apps.reservations.tests.factories import ReservationFactory
from apps.rooms.choices import RoomTypeChoices
from apps.rooms.models import Room
from apps.rooms.tests.factories import RoomFactory
from apps.users.tests.factories import UserFactory


class ServicesTest(TestCase):
    def setUp(self):
        self.room = RoomFactory(
            price=10.0,
            price_half_day=30.0,
            price_all_day=50.0,
            room_type=RoomTypeChoices.EVENT_ROOM,
        )
        self.entity = EntityFactory(
            entity_type=EntityTypesChoices.HOSTED,
        )
        self.monthly_bonus = MonthlyBonusFactory(
            entity=self.entity, amount=20, date=date(2025, 12, 1)
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
            result = get_total_price(
                self.reservation.reservation_type,
                self.reservation.entity.entity_type,
                self.reservation.room,
                self.reservation.start_time,
                self.reservation.end_time,
            )
            self.assertEqual(result, 24)
        with self.subTest("Bloc4 Entity (50%) | Morning reservation (30€)"):
            self.entity.entity_type = EntityTypesChoices.BLOC4
            self.reservation.reservation_type = ReservationTypeChoices.MORNING
            result = get_total_price(
                self.reservation.reservation_type,
                self.reservation.entity.entity_type,
                self.reservation.room,
                self.reservation.start_time,
                self.reservation.end_time,
            )
            self.assertEqual(result, 15)
        with self.subTest("General Entity (0%) | Afternoon reservation (30€)"):
            self.entity.entity_type = EntityTypesChoices.GENERAL
            self.reservation.reservation_type = ReservationTypeChoices.AFTERNOON
            result = get_total_price(
                self.reservation.reservation_type,
                self.reservation.entity.entity_type,
                self.reservation.room,
                self.reservation.start_time,
                self.reservation.end_time,
            )
            self.assertEqual(result, 30)
        with self.subTest("Outside Entity (+15%) | Whole day reservation (50€)"):
            self.entity.entity_type = EntityTypesChoices.OUTSIDE
            self.reservation.reservation_type = ReservationTypeChoices.WHOLE_DAY
            result = get_total_price(
                self.reservation.reservation_type,
                self.reservation.entity.entity_type,
                self.reservation.room,
                self.reservation.start_time,
                self.reservation.end_time,
            )
            self.assertEqual(result, 57.5)

    def test_get_monthly_bonus_totals(self):
        Reservation.objects.create(
            reservation_type=ReservationTypeChoices.HOURLY,
            date=date(2025, 12, 1),
            start_time=time(8, 0),
            end_time=time(12, 0),
            assistants=10,
            room=self.room,
            entity=self.entity,
            reserved_by=UserFactory(),
            status=Reservation.StatusChoices.CONFIRMED,
            total_price=20,
        )
        Reservation.objects.create(
            reservation_type=ReservationTypeChoices.MORNING,
            date=date(2025, 12, 2),
            start_time=time(8, 0),
            end_time=time(14, 0),
            assistants=10,
            room=self.room,
            entity=self.entity,
            reserved_by=UserFactory(),
            status=Reservation.StatusChoices.CONFIRMED,
            total_price=50,
        )
        reservations = Reservation.objects.filter()
        with self.subTest("Event rooms & hosted entity"):
            result = get_monthly_bonus_totals(reservations, self.entity, 12, 2025)
            self.assertEqual(
                result,
                {
                    "amount": 20,
                    "amount_left": 20,
                    "bonus_price": 70,
                    "is_monthly_bonus": True,
                    "total_price": 70,
                },
            )
        with self.subTest("Event & meeting rooms & hosted entity"):
            self.room.room_type = RoomTypeChoices.MEETING_ROOM
            meeting_room = Room.objects.create(
                name="Room 2",
                room_type=RoomTypeChoices.MEETING_ROOM,
            )
            Reservation.objects.create(
                reservation_type=ReservationTypeChoices.AFTERNOON,
                date=date(2025, 12, 3),
                start_time=time(14, 0),
                end_time=time(18, 0),
                assistants=10,
                room=meeting_room,
                entity=self.entity,
                reserved_by=UserFactory(),
                status=Reservation.StatusChoices.CONFIRMED,
                total_price=23,
            )
            result = get_monthly_bonus_totals(
                Reservation.objects.filter(), self.entity, 12, 2025
            )
            self.assertEqual(
                result,
                {
                    "amount": 20,
                    "amount_left": 16,
                    "bonus_price": 70,
                    "is_monthly_bonus": True,
                    "total_price": 93,
                },
            )
        with self.subTest("Not hosted entity"):
            self.entity.entity_type = EntityTypesChoices.OUTSIDE
            result = get_monthly_bonus_totals(reservations, self.entity, 12, 2025)
            self.assertEqual(result, {})
