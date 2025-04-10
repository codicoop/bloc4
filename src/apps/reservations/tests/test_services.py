from datetime import date, time
from decimal import Decimal

from django.test import TestCase

from apps.entities.choices import EntityTypesChoices
from apps.entities.models import Entity, MonthlyBonus
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
        self.maxDiff = None
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

    def test_get_total_price(self):
        Reservation.objects.all().delete()
        reservation = ReservationFactory(
            reservation_type=ReservationTypeChoices.HOURLY,
            date=date(2025, 12, 25),
            start_time=time(8, 0),
            end_time=time(12, 0),
            assistants=10,
            room=self.room,
            entity=self.entity,
            reserved_by=UserFactory(),
            base_price=60,
        )
        with self.subTest("Hosted Entity (40%) | 4hr Hourly reservation (10€/h)"):
            result = get_total_price(
                reservation.reservation_type,
                reservation.entity.entity_type,
                reservation.room,
                reservation.start_time,
                reservation.end_time,
            )
            self.assertEqual(round(result, 2), 24)
        with self.subTest("Bloc4 Entity (50%) | Morning reservation (30€)"):
            self.entity.entity_type = EntityTypesChoices.BLOC4
            reservation.reservation_type = ReservationTypeChoices.MORNING
            result = get_total_price(
                reservation.reservation_type,
                reservation.entity.entity_type,
                reservation.room,
                reservation.start_time,
                reservation.end_time,
            )
            self.assertEqual(result, 15)
        with self.subTest("General Entity (0%) | Afternoon reservation (30€)"):
            self.entity.entity_type = EntityTypesChoices.GENERAL
            reservation.reservation_type = ReservationTypeChoices.AFTERNOON
            result = get_total_price(
                reservation.reservation_type,
                reservation.entity.entity_type,
                reservation.room,
                reservation.start_time,
                reservation.end_time,
            )
            self.assertEqual(result, 30)
        with self.subTest("Outside Entity (+15%) | Whole day reservation (50€)"):
            self.entity.entity_type = EntityTypesChoices.OUTSIDE
            reservation.reservation_type = ReservationTypeChoices.WHOLE_DAY
            result = get_total_price(
                reservation.reservation_type,
                reservation.entity.entity_type,
                reservation.room,
                reservation.start_time,
                reservation.end_time,
            )
            self.assertEqual(round(result, 2), 57.5)

    def test_get_monthly_bonus_totals(self):
        """
        The situation with this test is quite dramatical.
        The get_monthly_bonus_totals function instead of taking care of calculating
        the discounts for the meeting room reservations (as these are the only
        ones having a monthly discount), it's used to process batches of reservations
        of every kind, so you could do something like passing it a list of classroom
        reservations and with the parameter "room_type=Event rooms".
        The parameters reservations and room_type of the function should not exist,
        and the function should be repurposed so it only does what the name of it
        says.
        The problem with that is that a considerable part of the current code is
        coupled with this function, so making this changes implies a quite bigger
        refactor.
        This test needed a heavy refactor to adapt to some of the changes, which
        ended up with this current situation:
        - Some things that are being tested here make no sense, i.e., testing the
          discounts for EVENT_ROOM reservations.
        - Many other tests that could be useful are missing.

        It's such a headache to write tests with the current structure that it will
        be better to wait until a biggger refactor is done (probable necessary to
        implement the yearly discounts for classrooms) and then write this test
        from scratch.
        """
        Reservation.objects.all().delete()
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
            base_price=20,
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
            base_price=50,
        )
        reservations = Reservation.objects.all()

        with self.subTest("Event rooms & hosted entity"):
            """
            Event rooms don't have any monthly discount.
            They have (or will have) yearly discounts.
            """
            result = get_monthly_bonus_totals(
                reservations,
                self.entity,
                12,
                2025,
                self.room.room_type,
            )
            result["vat"] = round(result["vat"], 2)
            result["total_price"] = round(result["total_price"], 2)
            self.assertEqual(
                result,
                {
                    "discounted_hours_amount": 0,
                    "discounted_hours_amount_left": 0,
                    "base_price": round(Decimal(70), 2),
                    "vat": round(Decimal(14.7), 2),  # base_price * constants.VAT
                    "total_price": round(Decimal(84.7), 2),  # with VAT
                },
            )
        with self.subTest("Event & meeting rooms & hosted entity"):
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
                base_price=23,
            )
            result = get_monthly_bonus_totals(
                Reservation.objects.filter(),
                self.entity,
                12,
                2025,
                meeting_room.room_type,
            )
            result["base_price"] = round(result["base_price"], 2)
            result["vat"] = round(result["vat"], 2)
            result["total_price"] = round(result["total_price"], 2)
            self.assertEqual(
                result,
                {
                    "discounted_hours_amount": Decimal(20),
                    "discounted_hours_amount_left": Decimal(16),
                    "base_price": round(Decimal(0)),
                    "vat": round(Decimal(0)),
                    "total_price": round(Decimal(0)),
                },
            )
        with self.subTest("November reservation. New entity"):
            meeting_room = Room.objects.create(
                name="Room 3",
                room_type=RoomTypeChoices.MEETING_ROOM,
            )
            new_entity = Entity.objects.create(
                entity_email="test@example.com",
                fiscal_name="New entity",
                nif="12345N",
                postal_code="00000",
                country="Country",
                entity_type=EntityTypesChoices.HOSTED,
            )
            Reservation.objects.create(
                reservation_type=ReservationTypeChoices.AFTERNOON,
                date=date(2025, 11, 1),
                start_time=time(14, 0),
                end_time=time(18, 0),
                assistants=10,
                room=meeting_room,
                entity=new_entity,
                reserved_by=UserFactory(),
                status=Reservation.StatusChoices.CONFIRMED,
                base_price=50,
            )
            MonthlyBonus.objects.create(
                entity=new_entity, amount=10, date=date(2025, 11, 1)
            )
            result = get_monthly_bonus_totals(
                Reservation.objects.filter(
                    entity=new_entity, date__month=11, date__year=2025
                ),
                new_entity,
                11,
                2025,
                meeting_room.room_type,
            )
            result["base_price"] = round(result["base_price"], 2)
            result["vat"] = round(result["vat"], 2)
            result["total_price"] = round(result["total_price"], 2)
            self.assertEqual(
                result,
                {
                    "discounted_hours_amount": Decimal(10),
                    "discounted_hours_amount_left": Decimal(6),
                    "base_price": round(Decimal(0)),
                    "vat": round(Decimal(0)),
                    "total_price": round(Decimal(0)),
                },
            )
        with self.subTest("Not hosted entity"):
            self.entity.entity_type = EntityTypesChoices.OUTSIDE
            result = get_monthly_bonus_totals(
                reservations,
                self.entity,
                12,
                2025,
                RoomTypeChoices.MEETING_ROOM,
            )
            self.assertEqual(
                result,
        {
                    "discounted_hours_amount": Decimal(20),
                    "discounted_hours_amount_left": Decimal(12),
                    "base_price": round(Decimal(0)),
                    "vat": round(Decimal(0)),
                    "total_price": round(Decimal(0)),
                },
            )
