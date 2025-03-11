import uuid
from datetime import datetime
from urllib.parse import urlencode

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import NoReverseMatch, reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from extra_settings.models import Setting

from apps.entities.choices import EntityTypesChoices
from apps.reservations.constants import MONTHS
from apps.reservations.forms import ReservationForm
from apps.reservations.models import Reservation
from apps.reservations.services import (
    calculate_discount_price,
    calculate_reservation_price,
    convert_datetime_to_str,
    date_to_full_calendar_format,
    delete_zeros,
    get_monthly_bonus_totals,
    get_total_price,
    get_years_and_months,
    parse_time,
    send_mail_reservation,
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
        "amount_left": 0,
        "total_price": 0,
        "bonus_price": 0,
        "reservations": reservations,
        "months": months_list,
        "years": years_list,
        "month": MONTHS.get(now.month, "")[:3] + ".",
        "year": now.year,
    }
    bonuses = get_monthly_bonus_totals(reservations, entity, now.month, now.year)
    context.update(bonuses)
    return render(
        request,
        "reservations/reservations_list.html",
        context,
    )


# htmx
def filter_reservations(request):
    bonuses = {}
    entity = request.user.entity
    context = {"is_monthly_bonus": False}
    filter_year = request.POST.get("filter_year")
    filter_month = request.POST.get("filter_month")
    reservations = Reservation.objects.filter(
        entity=entity, date__month=filter_month, date__year=filter_year
    ).order_by("date")
    context = {
        "is_monthly_bonus": False,
        "amount_left": 0,
        "total_price": 0,
        "bonus_price": 0,
        "reservations": reservations,
        "month": MONTHS.get(int(filter_month), "")[:3] + ".",
        "year": filter_year,
    }
    bonuses = get_monthly_bonus_totals(reservations, entity, filter_month, filter_year)
    context.update(bonuses)
    return render(
        request,
        "reservations/components/reservations.html",
        context,
    )


def create_reservation_view(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    if not start or not end:
        return redirect("reservations:reservations_calendar")
    try:
        id = uuid.UUID(request.GET.get("id"))
    except ValueError:
        return redirect("reservations:reservations_calendar")
    room = get_object_or_404(Room, id=id)
    entity_type = request.user.entity.entity_type
    if start and end:
        start_datetime = datetime.fromisoformat(start)
        end_datetime = datetime.fromisoformat(end)
        date = start_datetime.date().strftime("%Y-%m-%d")
        price_discount = calculate_discount_price(entity_type, room.price)
        total_price = calculate_reservation_price(
            start_datetime, end_datetime, price_discount
        )
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
            reservation.total_price = get_total_price(
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
                (
                    reservation.room.room_type == RoomTypeChoices.CLASSROOM
                    and class_reservation_privilege
                ) or (
                    # In March 2025, they decide that all meeting room reservations
                    # will be automatically confirmed.
                    reservation.room.room_type == RoomTypeChoices.MEETING_ROOM
                )
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
        elif form.data.get("end_time") and form.data.get("start_time"):
            total_price = get_total_price(
                form.data.get("reservation_type"),
                entity_type,
                room,
                parse_time(form.data.get("start_time")),
                parse_time(form.data.get("end_time")),
            )
    return render(
        request,
        "reservations/create_reserves.html",
        {
            "form": form,
            "room": room,
            "total_price": delete_zeros(total_price),
        },
    )


def reservation_detail_view(request, id):
    is_staff = request.user.is_staff
    try:
        reservation_id = uuid.UUID(id)
        if is_staff:
            reservation = get_object_or_404(Reservation, id=reservation_id)
        else:
            entity = request.user.entity
            reservation = get_object_or_404(
                Reservation, id=reservation_id, entity=entity
            )
    except ValueError:
        return redirect("reservations:reservations_list")
    payment_info = None
    if (
        reservation.entity.entity_type
        in [EntityTypesChoices.GENERAL, EntityTypesChoices.OUTSIDE]
        and reservation.status == Reservation.StatusChoices.CONFIRMED
        and not reservation.is_paid
    ):
        payment_info = Setting.get("PAYMENT_INFORMATION")
    if "cancel_reservation" in request.POST:
        id = request.POST.get("cancel_reservation")
        reservation = get_object_or_404(Reservation, id=id)
        reservation.status = Reservation.StatusChoices.CANCELED
        reservation.canceled_by = request.user
        reservation.canceled_at = timezone.now()
        reservation.save()
        send_mail_reservation(reservation, "reservation_canceled_user")
        send_mail_reservation(reservation, "reservation_canceled_bloc4")
        return redirect("reservations:reservations_cancelled")
    return render(
        request,
        "reservations/details.html",
        {
            "reservation": reservation,
            "is_staff": is_staff,
            "payment_info": payment_info,
        },
    )


# htmx
def calculate_total_price(request):
    total_price = 0
    if request.htmx:
        entity_type = request.user.entity.entity_type
        room = get_object_or_404(Room, id=request.POST.get("room"))
        reservation_type = request.POST.get("reservation_type")
        start_time = parse_time(request.POST.get("start_time"))
        end_time = parse_time(request.POST.get("end_time"))
        if start_time and end_time:
            total_price = get_total_price(
                reservation_type, entity_type, room, start_time, end_time
            )
    return render(
        request,
        "reservations/total_price.html",
        {
            "total_price": delete_zeros(total_price),
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
    context["is_staff"] = request.user.is_staff
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
                "is_staff": request.user.is_staff,
                "reservation_id": reservation.id,
            }
            if request.user.is_staff:
                reservation_data["entity"] = reservation.entity.fiscal_name
            data.append(reservation_data)
        return JsonResponse(data, safe=False)
