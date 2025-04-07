import uuid
from datetime import datetime
from urllib.parse import urlencode

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseNotFound, HttpResponseRedirect, JsonResponse, \
    HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import NoReverseMatch, reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from extra_settings.models import Setting

from apps.entities.choices import EntityTypesChoices
from apps.entities.models import Entity
from apps.reservations import constants
from apps.reservations.constants import MONTHS
from apps.reservations.forms import ReservationForm
from apps.reservations.models import Reservation
from apps.reservations.services import (
    calculate_discount_price,
    convert_datetime_to_str,
    date_to_full_calendar_format,
    get_total_price,
    get_years_and_months,
    parse_time,
    send_mail_reservation, get_filter_reservations_context,
)
from apps.rooms.choices import RoomTypeChoices
from apps.rooms.constanst import ALL_COLOR, CALENDAR_TEXT_COLOR
from apps.rooms.models import Room
from project.views import StandardSuccess


def reservations_list(request):
    entity = request.user.entity
    now = timezone.now()
    reservations_all = Reservation.objects.filter(entity=entity)
    months_list, years_list = get_years_and_months(reservations_all)
    reservations = reservations_all.filter(
        date__year=now.year, date__month=now.month
    ).order_by("date")
    context = {
        "is_monthly_bonus": False,
        "reservations": None,  # The month filter dropdown triggers on load
        "months": months_list,
        "years": years_list,
        "month": MONTHS.get(now.month, "")[:3] + ".",
        "year": now.year,
        "filter_reservations_url": reverse("reservations:filter_my_reservations"),
    }
    return render(
        request,
        "reservations/reservations_list.html",
        context,
    )


@user_passes_test(lambda u: u.is_staff)
def reservations_list_summary(request):
    now = timezone.now()
    reservations_all = Reservation.objects.all()
    months_list, years_list = get_years_and_months(reservations_all)
    context = {
        "amount_left": 0,
        "bonus_price": 0,
        "reservations": None,  # Initial list empty, they have to pick an Entity
        "months": months_list,
        "years": years_list,
        "month": MONTHS.get(now.month, "")[:3] + ".",
        "year": now.year,
        "entities": Entity.objects.all(),
        "filter_reservations_url": reverse("reservations:filter_reservations_summary"),
    }
    return render(
        request,
        "reservations/reservations_list_summary.html",
        context,
    )


def filter_my_reservations(request):
    filter_year = request.POST.get("filter_year")
    filter_month = request.POST.get("filter_month")
    context = get_filter_reservations_context(
        filter_year,
        filter_month,
        request.user.entity,
    )
    return render(
        request,
        "reservations/components/my_reservations.html",
        context,
    )


@user_passes_test(lambda u: u.is_staff)
def filter_reservations_summary(request):
    if not request.POST.get("filter_entity"):
        return HttpResponse('')

    # In the reservations_list_summary view (only accessible by is_staff
    # users) the organization filter dropdown is included.
    # In the reservations_list view, it's not.
    # Both views are based in the same template that will trigger the htmx
    # request pointing to this filter_reservations view.
    # Therefore, the filter_entity POST value should only arrive when we're
    # in the Monthly summary section, meaning that only is_staff users can
    # access it.
    filter_entity = request.POST.get("filter_entity")
    entity = get_object_or_404(Entity, id=filter_entity)
    filter_year = request.POST.get("filter_year")
    filter_month = request.POST.get("filter_month")
    context = get_filter_reservations_context(filter_year, filter_month, entity)
    return render(
        request,
        "reservations/components/reservations_summary.html",
        context,
    )


def create_reservation_view(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    try:
        id = uuid.UUID(request.GET.get("id"))
    except ValueError:
        return redirect("reservations:reservations_calendar")
    room = get_object_or_404(Room, id=id)
    start_datetime = None
    if start:
        start_datetime = datetime.fromisoformat(start)
    end_datetime = None
    if end:
        end_datetime = datetime.fromisoformat(end)
    date = None
    defined_datetime = start_datetime or end_datetime
    if defined_datetime:
        date = defined_datetime.date().strftime("%Y-%m-%d")
    form = ReservationForm(
        initial={
            "date": date,
            "start_time": start_datetime,
            "end_time": end_datetime,
            "entity": request.user.entity,
            "room": room.id,
        },
        request=request,
    )
    if request.method == "POST":
        form = ReservationForm(request.POST, request.FILES, request=request)
        # Validation of the date format
        try:
            datetime.strptime(form.data["date"], "%Y-%m-%d")
        except Exception:
            form.add_error("date", "")
            return render(
                request,
                "reservations/create_reserves.html",
                {"form": form},
            )
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.reserved_by = request.user
            reservation.base_price = get_total_price(
                reservation.reservation_type,
                reservation.entity.entity_type,
                reservation.room,
                reservation.start_time,
                reservation.end_time,
            )
            privilege = getattr(reservation.entity, "entity_privilege", None)
            class_reservation_privilege = getattr(
                privilege,
                "class_reservation_privilege",
                None,
            )
            if (
                reservation.room.room_type == RoomTypeChoices.CLASSROOM
                and class_reservation_privilege
            ) or (
                # In March 2025, they decide that all meeting room reservations
                # will be automatically confirmed.
                reservation.room.room_type == RoomTypeChoices.MEETING_ROOM
            ):
                reservation.status = Reservation.StatusChoices.CONFIRMED
                send_mail_reservation(reservation, "reservation_confirmed_user")
            else:
                send_mail_reservation(reservation, "reservation_request_user")
            send_mail_reservation(reservation, "reservation_request_bloc4")
            reservation.save()
            form.save()
            if reservation.catering and Setting.get("CATERING_ROOM"):
                try:
                    catering_id = uuid.UUID(Setting.get("CATERING_ROOM"))
                    catering_room = Room.objects.filter(id=catering_id)
                    if catering_room.exists():
                        base_url = reverse("reservations:reservations_redirect_success")
                        start_time_str, end_time_str = convert_datetime_to_str(
                            reservation
                        )
                        query_params = {
                            "start": start_time_str,
                            "end": end_time_str,
                            "id": catering_id,
                        }
                        url = f"{base_url}?{urlencode(query_params)}"
                        return redirect(url)
                except ValueError:
                    return redirect("reservations:reservations_success")
            return redirect("reservations:reservations_success")
    return render(
        request,
        "reservations/create_reserves.html",
        {
            "form": form,
            "room": room,
        },
    )


def reservation_detail_view(request, id):
    filter_params = {"id": id}
    has_access_to_all_reservations = request.user.is_staff or request.user.is_janitor
    if not has_access_to_all_reservations:
        try:
            entity = request.user.entity
        except ValueError:
            return redirect("reservations:reservations_list")
        filter_params.update({"entity": entity})
    reservation = get_object_or_404(Reservation, **filter_params)

    payment_info = None
    if (
        reservation.entity.entity_type
        in [EntityTypesChoices.GENERAL, EntityTypesChoices.OUTSIDE]
        and reservation.status == Reservation.StatusChoices.CONFIRMED
        and not reservation.is_paid
    ):
        payment_info = Setting.get("PAYMENT_INFORMATION")

    # Context and status vars
    can_be_cancelled = not request.user.is_janitor and reservation.status in (
        Reservation.StatusChoices.PENDING,
        Reservation.StatusChoices.CONFIRMED,
    )
    can_be_checked_in = request.user.is_janitor

    # POST actions
    if "cancel_reservation" in request.POST:
        if not can_be_cancelled:
            return HttpResponseNotFound(_("This reservation cannot be cancelled."))
        reservation.status = Reservation.StatusChoices.CANCELED
        reservation.canceled_by = request.user
        reservation.canceled_at = timezone.now()
        reservation.save()
        send_mail_reservation(reservation, "reservation_canceled_user")
        send_mail_reservation(reservation, "reservation_canceled_bloc4")
        return redirect("reservations:reservations_cancelled")
    if "check_in_reservation" in request.POST:
        if not can_be_checked_in:
            return HttpResponseNotFound(_("This reservation cannot be checked in."))
        reservation.checked_in = True
        reservation.save()
        return HttpResponseRedirect(request.path_info)

    return render(
        request,
        "reservations/details.html",
        {
            "reservation": reservation,
            "payment_info": payment_info,
            "can_be_cancelled": can_be_cancelled,
            "can_be_checked_in": can_be_checked_in,
        },
    )


# htmx
def calculate_total_price(request):
    base_price = 0
    if request.htmx:
        entity_type = request.user.entity.entity_type
        room = get_object_or_404(Room, id=request.POST.get("room"))
        reservation_type = request.POST.get("reservation_type")
        start_time = parse_time(request.POST.get("start_time"))
        end_time = parse_time(request.POST.get("end_time"))
        if start_time and end_time:
            base_price = get_total_price(
                reservation_type, entity_type, room, start_time, end_time
            )
    discounted_base_price = calculate_discount_price(entity_type, base_price)
    return render(
        request,
        "reservations/total_price.html",
        {
            "base_price": discounted_base_price,
            "tax": discounted_base_price * constants.VAT,
            "total_price": discounted_base_price * (constants.VAT + 1),
        },
    )


class ReservationSuccessView(StandardSuccess):
    page_title = _("Successful reservation")
    description = _("Successful reservation.")
    url = reverse_lazy("reservations:reservations_list")

    def get_url(self):
        try:
            reversed_url = reverse(self.url)
        except NoReverseMatch:
            return self.url
        return reversed_url


class ReservationRedirectSuccessView(StandardSuccess):
    page_title = _("Successful reservation")
    description = _(
        "Successful reservation.<br><br> As you've selected you need "
        " catering space outside the room, it's mandatory to make a "
        "reservation for it."
    )
    link_text = _("Continue")
    page_title = _("Successful reservation")
    url = "reservations:create_reservation"

    def get_url(self):
        try:
            reversed_url = reverse(self.url)
            request = self.request
            query_params = {
                "id": request.GET.get("id"),
                "start": request.GET.get("start"),
                "end": request.GET.get("end"),
            }
            return f"{reversed_url}?{urlencode(query_params)}"
        except NoReverseMatch:
            return self.url
        return reversed_url


class ReservationCancelledView(StandardSuccess):
    page_title = _("Reservation cancelled")
    description = _("Reservation cancelled.")
    url = reverse_lazy("reservations:reservations_list")
    page_title = _("Reservation cancelled")

    def get_url(self):
        try:
            reversed_url = reverse(self.url)
        except NoReverseMatch:
            return self.url
        return reversed_url


def reservations_calendar_view(request):
    context = {}
    room_types = Room.objects.values_list("room_type", flat=True).distinct()
    unique_room_types = {
        room_type: {
            "label": RoomTypeChoices(room_type).label,
            "color": RoomTypeChoices(room_type).get_room_color(),
        }
        for room_type in room_types
    }
    unique_room_types = {
        "all": {"label": _("All"), "color": ALL_COLOR}
    } | unique_room_types
    context["room_types"] = unique_room_types
    context["rooms"] = Room.objects.all()
    context["discount"] = EntityTypesChoices(
        request.user.entity.entity_type
    ).get_discount_percentage()
    if request.htmx:
        room_type = request.POST.get("room_type")
        if room_type != "all":
            context["rooms"] = Room.objects.filter(room_type=room_type)
        return render(request, "rooms/rooms_filtered.html", context)
    return render(request, "reservations/full_calendar.html", context)


class AjaxCalendarFeed(View):
    def get(self, request, *args, **kwargs):
        data = []
        id = kwargs.get("id")
        reservations = Reservation.objects.exclude(
            status__in=[
                Reservation.StatusChoices.CANCELED,
                Reservation.StatusChoices.REFUSED,
            ]
        )
        try:
            room_id = uuid.UUID(id)
            reservations = reservations.filter(room__id=room_id)
        except ValueError:
            if id != "all":
                reservations = reservations.filter(room__room_type=id)
        for reservation in reservations:
            color = RoomTypeChoices(reservation.room.room_type).get_room_color()
            reservation_data = {
                "room": reservation.room.name,
                "title": reservation.title,
                "start": date_to_full_calendar_format(
                    timezone.make_aware(
                        datetime.combine(reservation.date, reservation.start_time)
                    )
                ),
                "end": date_to_full_calendar_format(
                    timezone.make_aware(
                        datetime.combine(reservation.date, reservation.end_time)
                    )
                ),
                "backgroundColor": color,
                "borderColor": color,
                "textColor": CALENDAR_TEXT_COLOR,
                "reservation_id": reservation.id,
            }
            if request.user.is_staff or request.user.is_janitor:
                reservation_data["entity"] = reservation.entity.fiscal_name
            data.append(reservation_data)
        return JsonResponse(data, safe=False)


# htmx
@user_passes_test(lambda u: u.is_staff)
def mark_reservations_as_billed(request, year, month, entity):
    entity = get_object_or_404(Entity, id=entity)
    Reservation.objects.filter(
        entity=entity,
        date__month=month,
        date__year=year,
    ).update(
        is_billed=True,
        billed_by=request.user,
        billed_at=datetime.now(),
    )
    context = get_filter_reservations_context(year, month, entity)
    return render(
        request,
        "reservations/components/reservations_summary.html",
        context,
    )
