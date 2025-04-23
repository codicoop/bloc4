import copy
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.test import TestCase
from django.urls import reverse
from django.test.client import RequestFactory

from apps.entities.tests.factories import EntityFactory
from apps.reservations import constants
from apps.reservations.choices import (
    ActivityTypeChoices,
    Bloc4TypeChoices,
    ReservationTypeChoices,
)
from apps.reservations.forms import ReservationForm
from apps.reservations.models import Reservation
from apps.rooms.tests.factories import RoomFactory
from apps.users.tests.factories import UserFactory


class ReservationModelTest(TestCase):
    def setUp(self):
        room = RoomFactory()
        entity = EntityFactory()
        # The groups are created in a post_migrations signal, so if you try to
        # create a Group using FactoryBoy with name=Administrators it throws the
        # error that the unique name already exists.
        # So, querying the existing one instead of using FactoryBoy.
        # Also, we're using .filter() because we have to use the groups.set()
        # method if we want to assign the group from the user object, so we need
        # it to be a list.
        admins_group = Group.objects.filter(name=settings.GROUP_ADMINS)
        admin_user = UserFactory()
        admin_user.groups.set(admins_group)
        admin_user.entity = entity
        request = RequestFactory().get(reverse("reservations:create_reservation"))
        user = UserFactory()
        user.entity = entity
        request.user = user
        base_data_yesterday = {
            "title": "Test reservation",
            "reservation_type": ReservationTypeChoices.HOURLY,
            "date": date.today() + timedelta(days=-1),
            "start_time": "10:00",
            "end_time": "11:00",
            "room": room.id,
            "entity": entity.id,
            "notes": "Test notes",
            "assistants": 10,
            "activity_type": ActivityTypeChoices.BLOC4,
            "bloc4_type": Bloc4TypeChoices.TRAINING,
            "base_price": 100,
            "privacy": Reservation.PrivacyChoices.PRIVATE,
            "reserved_by": 1,
            "status": Reservation.StatusChoices.PENDING,
            "data_policy": True,
            "terms_use": True,
        }
        self.form_error_greater_current_date = ReservationForm(
            data=base_data_yesterday,
            request=request,
            room=room,
        )
        base_data_tomorrow = base_data_yesterday.copy()
        base_data_tomorrow["date"] = date.today() + timedelta(days=+1)
        form_error_no_full_hour_data = base_data_tomorrow.copy()
        form_error_no_full_hour_data["start_time"] = "10:00"
        form_error_no_full_hour_data["end_time"] = "10:30"
        self.form_error_no_full_hour = ReservationForm(
            data=form_error_no_full_hour_data,
            request=request,
            room=room,
        )
        form_error_too_early_data = base_data_tomorrow.copy()
        form_error_too_early_data["start_time"] = "02:00"
        form_error_too_early_data["end_time"] = "10:00"
        self.form_error_too_early = ReservationForm(
            data=form_error_too_early_data,
            request=request,
            room=room,
        )
        form_error_too_late_data = base_data_tomorrow.copy()
        form_error_too_late_data["start_time"] = "14:00"
        form_error_too_late_data["end_time"] = "22:00"
        self.form_error_too_late = ReservationForm(
            data=form_error_too_late_data,
            request=request,
            room=room,
        )
        # Switching to an administrator user
        request_admin = copy.copy(request)
        request_admin.user = admin_user
        form_allowed_before_initial_hour_data = base_data_tomorrow.copy()
        form_allowed_before_initial_hour_data["start_time"] = "02:00"
        form_allowed_before_initial_hour_data["end_time"] = "10:00"
        self.form_allowed_before_initial_hour = ReservationForm(
            data=form_allowed_before_initial_hour_data,
            request=request_admin,
            room=room,
        )
        form_allowed_after_last_hour_data = base_data_tomorrow.copy()
        form_allowed_after_last_hour_data["start_time"] = "14:00"
        form_allowed_after_last_hour_data["end_time"] = "22:00"
        self.form_allowed_after_last_hour = ReservationForm(
            data=form_allowed_after_last_hour_data,
            request=request_admin,
            room=room,
        )
        # This test was originally done with a standard user, but a normal
        # user cannot make a reservation for more than 20 hours because it would
        # require to make it earlier than the minimum starting time or later than
        # the maximum ending time.
        # So this test is moved here so the user making this reservation is an
        # admin and therefore not constraint by the minimum and maximum hours.
        form_error_more_20_hours_data = base_data_tomorrow.copy()
        form_error_more_20_hours_data["start_time"] = "02:00"
        form_error_more_20_hours_data["end_time"] = "23:00"
        self.form_error_more_20_hours = ReservationForm(
            data=form_error_more_20_hours_data,
            request=request_admin,
            room=room,
        )

    def test_form_errors(self):
        self.assertFalse(self.form_error_greater_current_date.is_valid())
        self.assertFalse(self.form_error_no_full_hour.is_valid())
        self.assertFalse(self.form_error_more_20_hours.is_valid())
        self.assertFalse(self.form_error_too_early.is_valid())
        self.assertFalse(self.form_error_too_late.is_valid())

        with self.subTest("Model validations"):
            self.assertEqual(
                self.form_error_greater_current_date.errors["date"],
                [_("The date must be greater than the current date.")],
            )
            self.assertEqual(
                self.form_error_no_full_hour.errors["end_time"],
                [_("The reservation must have a minimum duration of one hour.")],
            )
            self.assertEqual(
                self.form_error_more_20_hours.errors["end_time"],
                [_("The maximum standby time is 20 hours.")],
            )
            self.assertEqual(
                self.form_error_too_early.errors["start_time"],
                [
                    _(
                        "The start time must be between "
                        "{start_time} and {end_time}."
                    ).format(
                        start_time=constants.START_TIME.strftime("%H:%M"),
                        end_time=constants.END_TIME_MINUS_ONE.strftime("%H:%M"),
                    )
                ],
            )
            self.assertEqual(
                self.form_error_too_late.errors["end_time"],
                [
                    _(
                        "The end time must be between "
                        "{start_time} and {end_time}."
                    ).format(
                        start_time=constants.START_TIME_PLUS_ONE.strftime("%H:%M"),
                        end_time=constants.END_TIME.strftime("%H:%M"),
                    ),
                ],
            )

        # Thinks that should be allowed to do because is Administrator
        self.assertTrue(self.form_allowed_before_initial_hour.is_valid())
        self.assertTrue(self.form_allowed_after_last_hour.is_valid())
