from django.conf import settings
from django.shortcuts import reverse
from django.test import Client, TestCase

from apps.entities.tests.factories import EntityFactory
from apps.reservations.choices import (
    ActivityTypeChoices,
    Bloc4TypeChoices,
    ReservationTypeChoices,
)
from apps.reservations.models import Reservation
from apps.rooms.tests.factories import RoomFactory
from apps.users.models import User


class ReservationsListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = self.client.login(
            username=settings.DJANGO_SUPERUSER_EMAIL,
            password=settings.DJANGO_SUPERUSER_PASSWORD,
            entity=EntityFactory(),
        )

    def test_get(self):
        response = self.client.get(reverse("reservations:reservations_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/ca/reserves/")
        self.assertTemplateUsed(response, "reservations/reservations_list.html")


class CreateReservationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.entity = EntityFactory()

        self.user = User.objects.create_superuser(
            name="Test",
            email="test@codi.coop",
            password=settings.DJANGO_SUPERUSER_PASSWORD,
            entity=self.entity,
        )
        self.user = self.client.login(
            username="test@codi.coop",
            password=settings.DJANGO_SUPERUSER_PASSWORD,
        )
        self.room = RoomFactory()
        self.url = reverse("reservations:create_reservation")
        self.data = {
            "title": "Test title",
            "reservation_type": ReservationTypeChoices.HOURLY,
            "date": "2024-12-27",
            "start_time": "8:00",
            "end_time": "10:00",
            "assistants": 10,
            "room": self.room.id,
            "notes": "Tests notes",
            "activity_type": ActivityTypeChoices.BLOC4,
            "bloc4_type": Bloc4TypeChoices.TRAINING,
            "privacy": Reservation.PrivacyChoices.PRIVATE,
            "entity": self.entity.id,
            "reserved_by": self.user,
            "status": Reservation.StatusChoices.PENDING,
            "data_policy": True,
            "terms_use": True,
        }

    def test_post(self):
        query_params = (
            "?start=2024-12-27T08%3A00%3A00%2B01%3A00&"
            "end=2024-12-27T10%3A00%3A00%2B01%3A00&"
            f"id={self.room.id}"
        )
        full_url = f"{self.url}{query_params}"
        response = self.client.post(full_url, data=self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/ca/reserves/exit/")
        self.assertTemplateUsed(response, "standard_success.html")


class ReservationsCalendarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = self.client.login(
            username=settings.DJANGO_SUPERUSER_EMAIL,
            password=settings.DJANGO_SUPERUSER_PASSWORD,
            entity=EntityFactory(),
        )

    def test_get(self):
        self.room = RoomFactory()
        response = self.client.get(
            reverse("reservations:ajax_room_calendar_feed", kwargs={"id": self.room.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], f"/ca/reserves/ajax/calendar/{self.room.id}/"
        )
