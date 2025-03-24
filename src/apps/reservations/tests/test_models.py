from datetime import date, timedelta

from django.test import TestCase

from apps.entities.tests.factories import EntityFactory
from apps.reservations.choices import (
    ActivityTypeChoices,
    Bloc4TypeChoices,
    ReservationTypeChoices,
)
from apps.reservations.forms import ReservationForm
from apps.reservations.models import Reservation
from apps.rooms.tests.factories import RoomFactory


class ReservationModelTest(TestCase):
    def setUp(self):
        # Create a room for testing
        self.room = RoomFactory()

        # Create a entity for testing
        self.entity = EntityFactory()
        self.form_error_greater_current_date = ReservationForm(
            data={
                "tile": "Test reservation",
                "reservation_type": ReservationTypeChoices.HOURLY,
                "date": date.today() + timedelta(days=-1),
                "start_time": "10:00",
                "end_time": "11:00",
                "room": self.room.id,
                "entity": self.entity.id,
                "notes": "Test notes",
                "assistants": 10,
                "activity_type": ActivityTypeChoices.BLOC4,
                "bloc4_type": Bloc4TypeChoices.TRAINING,
                "base_price": 100,
                "privacy": Reservation.PrivacyChoices.PRIVATE,
                "reserved_by": 1,
                "status": Reservation.StatusChoices.PENDING,
            }
        )
        self.form_error_no_full_hour = ReservationForm(
            data={
                "tile": "Test reservation",
                "reservation_type": ReservationTypeChoices.HOURLY,
                "date": date.today() + timedelta(days=+1),
                "start_time": "10:00",
                "end_time": "10:30",
                "room": self.room.id,
                "entity": self.entity.id,
                "notes": "Test notes",
                "assistants": 10,
                "activity_type": ActivityTypeChoices.BLOC4,
                "bloc4_type": Bloc4TypeChoices.TRAINING,
                "base_price": 100,
                "privacy": Reservation.PrivacyChoices.PRIVATE,
                "reserved_by": 1,
                "status": Reservation.StatusChoices.PENDING,
            }
        )
        self.form_error_more_20_hours = ReservationForm(
            data={
                "tile": "Test reservation",
                "reservation_type": ReservationTypeChoices.HOURLY,
                "date": date.today() + timedelta(days=+1),
                "start_time": "02:00",
                "end_time": "23:00",
                "room": self.room.id,
                "entity": self.entity.id,
                "notes": "Test notes",
                "assistants": 10,
                "activity_type": ActivityTypeChoices.BLOC4,
                "bloc4_type": Bloc4TypeChoices.TRAINING,
                "base_price": 100,
                "privacy": Reservation.PrivacyChoices.PRIVATE,
                "reserved_by": 1,
                "status": Reservation.StatusChoices.PENDING,
            }
        )

    def test_form_errors(self):
        self.assertFalse(self.form_error_greater_current_date.is_valid())
        self.assertFalse(self.form_error_no_full_hour.is_valid())
        self.assertFalse(self.form_error_more_20_hours.is_valid())

        with self.subTest("Model validations"):
            self.assertEqual(
                self.form_error_greater_current_date.errors["date"],
                ["La data ha de ser posterior a l'actual."],
            )
            self.assertEqual(
                self.form_error_no_full_hour.errors["end_time"],
                ["La durada mínima d'una reserva és d'una hora."],
            )
            self.assertEqual(
                self.form_error_more_20_hours.errors["end_time"],
                ["La durada máxima d'una reserva és de 20 hores."],
            )
