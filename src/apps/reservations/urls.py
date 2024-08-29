from django.contrib.auth.decorators import login_required
from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.reservations.views import (
    AjaxCalendarFeed,
    ReservationsListView,
    ReservationSuccessView,
    create_reservation_view,
    reservations_calendar_view,
)

app_name = "reservations"
urlpatterns = [
    # Reservations
    path(
        "", login_required(ReservationsListView.as_view()), name="reservations_list"
    ),
    path(
        _("calendar/"),
        reservations_calendar_view,
        name="reservations_calendar",
    ),
    path(
        "ajax/calendar/<str:id>/",
        login_required(AjaxCalendarFeed.as_view()),
        name="ajax_room_calendar_feed",
    ),
    path(
        _("create/"), login_required(create_reservation_view), name="create_reservation"
    ),
    path(
        _("success/"),
        login_required(ReservationSuccessView.as_view()),
        name="reservations_success",
    ),
]
