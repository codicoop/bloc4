from django.conf import settings
from django.shortcuts import reverse
from django.test import Client, TestCase

from apps.entities.tests.factories import EntityFactory
from apps.reservations.models import Reservation
from apps.rooms.tests.factories import RoomFactory


class ReservationsListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = self.client.login(
            username=settings.DJANGO_SUPERUSER_EMAIL,
            password=settings.DJANGO_SUPERUSER_PASSWORD,
        )

    def test_get(self):
        response = self.client.get(reverse("reservations:reservations_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/ca/reservations/")
        self.assertTemplateUsed(response, "reservations/reservations_list.html")


class CreateReservationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = self.client.login(
            username=settings.DJANGO_SUPERUSER_EMAIL,
            password=settings.DJANGO_SUPERUSER_PASSWORD,
        )
        self.room = RoomFactory()
        self.entity = EntityFactory()
        self.url = reverse("reservations:create_reservation")
        self.data = {
            "room": self.room.id,
            "date": "2024-08-10",
            "start_time": "10:00",
            "end_time": "11:00",
            "is_paid": False,
            "entity": self.entity.id,
            "reserved_by": self.user,
            "status": Reservation.StatusChoices.PENDING,
        }

    def test_post(self):
        response = self.client.post(self.url, data=self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/ca/reservations/create")
        # self.assertTemplateUsed(response, "standard_success.html")


class ReservationsCalendarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = self.client.login(
            username=settings.DJANGO_SUPERUSER_EMAIL,
            password=settings.DJANGO_SUPERUSER_PASSWORD,
        )

    def test_get(self):
        response = self.client.get(reverse("reservations:ajax_calendar_feed"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], "/ca/reservations/ajax/calendar/"
        )
