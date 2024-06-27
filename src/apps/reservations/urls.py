from django.contrib.auth.decorators import login_required
from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.reservations.views import (
    AjaxCalendarFeed,
    ReservationsCalendarView,
    ReservationsListView,
    ReservationSuccessView,
    create_reservation_view,
)

app_name = "reservations"
urlpatterns = [
    # Reservations
    path(
        _(""), login_required(ReservationsListView.as_view()), name="reservations_list"
    ),
    path(
        _("calendar/"), ReservationsCalendarView.as_view(), name="reservations_calendar"
    ),
    path("ajax/calendar/", AjaxCalendarFeed.as_view(), name="ajax_calendar_feed"),
    path(_("create"), create_reservation_view, name="create_reservation"),
    path(_("success"), ReservationSuccessView.as_view(), name="reservations_success"),
]
