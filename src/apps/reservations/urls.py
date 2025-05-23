import uuid

from django.contrib.auth.decorators import login_required
from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.reservations.views import (
    AjaxCalendarFeed,
    ReservationCancelledView,
    ReservationRedirectSuccessView,
    ReservationSuccessView,
    calculate_total_price,
    create_reservation_view,
    filter_my_reservations,
    filter_reservations_summary,
    mark_reservations_as_billed,
    reservation_detail_view,
    reservations_calendar_view,
    reservations_list,
    reservations_list_summary,
)

app_name = "reservations"
urlpatterns = [
    # Reservations
    path("", login_required(reservations_list), name="reservations_list"),
    path(_("summary"), reservations_list_summary, name="list_summary"),
    path(
        _("calendar/"),
        login_required(reservations_calendar_view),
        name="reservations_calendar",
    ),
    path(
        "ajax/calendar/<str:id>/",
        login_required(AjaxCalendarFeed.as_view()),
        name="ajax_room_calendar_feed",
    ),
    path(
        # This view has one required parameter: id, and 2 optional ones: start
        # and end. They're passed via query parameters instead of the path
        # because there are multiple JS features that need to generate the URL
        # dynamically client-side: when you select a span of time in the calendar
        # and when you click the "book a room" button that is visible for mobile
        # resolutions.
        _("create/"),
        login_required(create_reservation_view),
        name="create_reservation",
    ),
    path(
        _("details/<uuid:id>/"),
        login_required(reservation_detail_view),
        name="reservations_details",
    ),
    path(
        # This view is only used to obtain the reservation details URL without
        # the uuid part, because the fullcalendar JS needs it to dynamically
        # compose the URLs when you click on a reservation at the calendar.
        # Therefore, this URL is only meant for reversing it. Accessing it
        # directly is expected to return a 404.
        _("details/"),
        login_required(reservation_detail_view),
        {"id": uuid.uuid4()},
        name="base_reservations_details",
    ),
    path(
        _("success/"),
        login_required(ReservationSuccessView.as_view()),
        name="reservations_success",
    ),
    path(
        _("success/redirect/"),
        login_required(ReservationRedirectSuccessView.as_view()),
        name="reservations_redirect_success",
    ),
    path(
        _("cancelled/"),
        login_required(ReservationCancelledView.as_view()),
        name="reservations_cancelled",
    ),
    # HTMX
    path(
        _("price/"), login_required(calculate_total_price), name="calculate_total_price"
    ),
    path(
        _("filter_summary/"),
        filter_reservations_summary,
        name="filter_reservations_summary",
    ),
    path(
        _("filter_my_reservations/"),
        filter_my_reservations,
        name="filter_my_reservations",
    ),
    path(
        _("mark_reservations_as_billed/<int:year>/<int:month>/<uuid:entity>/"),
        mark_reservations_as_billed,
        name="mark_reservations_as_billed",
    ),
]
