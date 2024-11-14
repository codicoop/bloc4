import uuid
from datetime import datetime

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import NoReverseMatch, reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import View

from apps.entities.choices import EntityTypesChoices
from apps.entities.models import MonthlyBonus
from apps.reservations.choices import ReservationTypeChoices
from apps.reservations.forms import ReservationForm
from apps.reservations.models import Reservation
from apps.reservations.services import (
    calculate_discount_price,
    calculate_reservation_price,
    date_to_full_calendar_format,
    delete_zeros,
    get_monthly_bonus_totals,
    get_years_and_months,
    send_mail_reservation,
)
from apps.rooms.choices import RoomTypeChoices
from apps.rooms.constanst import ALL_COLOR, CALENDAR_TEXT_COLOR
from apps.rooms.models import Room
from project.views import StandardSuccess


def reservations_list(request):
    bonuses = {}
    entity = request.user.entity
    now = timezone.now()
    reservations_all = Reservation.objects.filter(entity=entity)
    months_list, years_list = get_years_and_months(reservations_all)
    reservations = reservations_all.filter(
        date__year=now.year, date__month=now.month
    ).order_by("date")
    active_reservations = reservations.filter(
        Q(
            status__in=[
                Reservation.StatusChoices.PENDING,
                Reservation.StatusChoices.CONFIRMED,
            ]
        )
    )
    monthly_bonus = MonthlyBonus.objects.filter(
        entity=entity,
        date__year=now.year,
        date__month=now.month,
    )
    if (
        entity.entity_type in [EntityTypesChoices.HOSTED, EntityTypesChoices.BLOC4]
        and monthly_bonus.exists()
        and reservations.exists()
    ):
        monthly_bonus = monthly_bonus.first()
        bonuses["amount"] = delete_zeros(monthly_bonus.amount)
        bonuses["amount_left"] = 0
        bonuses["total_price"] = 0
        bonuses["bonus_price"] = 0
        if active_reservations:
            bonuses = get_monthly_bonus_totals(monthly_bonus, active_reservations)
        bonuses["is_monthly_bonus"] = True
    context = {
        "reservations": reservations,
        "months": months_list,
        "years": years_list,
    }
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
    active_reservations = reservations.filter(
        Q(
            status__in=[
                Reservation.StatusChoices.PENDING,
                Reservation.StatusChoices.CONFIRMED,
            ]
        )
    )
    monthly_bonus = MonthlyBonus.objects.filter(
        entity=entity,
        date__year=int(filter_year),
        date__month=int(filter_month),
    )
    if (
        entity.entity_type in [EntityTypesChoices.HOSTED, EntityTypesChoices.BLOC4]
        and monthly_bonus.exists()
        and reservations.exists()
    ):
        monthly_bonus = monthly_bonus.first()
        bonuses["amount"] = delete_zeros(monthly_bonus.amount)
        bonuses["amount_left"] = 0
        bonuses["total_price"] = 0
        bonuses["bonus_price"] = 0
        if active_reservations:
            bonuses = get_monthly_bonus_totals(monthly_bonus, active_reservations)
        bonuses["is_monthly_bonus"] = True
    context["reservations"] = reservations
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
        total_price = calculate_discount_price(entity_type, total_price)
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
        form = ReservationForm(request.POST, request.FILES)
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
            reservation.total_price = reservation.get_total_price
            if (
                reservation.room.room_type == RoomTypeChoices.CLASSROOM
                and reservation.entity.entity_privilege.class_reservation_privilege
            ):
                reservation.status = Reservation.StatusChoices.CONFIRMED
                send_mail_reservation(reservation, "reservation_confirmed_user")
            else:
                send_mail_reservation(reservation, "reservation_request_user")
            send_mail_reservation(reservation, "reservation_request_bloc4")
            reservation.save()
            form.save()
            return redirect("reservations:reservations_success")
    return render(
        request,
        "reservations/create_reserves.html",
        {
            "form": form,
            "room": room,
            "entity": request.user.entity,
            "price": calculate_discount_price(entity_type, room.price),
            "price_half_day": calculate_discount_price(
                entity_type,
                room.price_half_day,
            ),
            "price_all_day": calculate_discount_price(
                entity_type,
                room.price_all_day,
            ),
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
        {"reservation": reservation, "is_staff": is_staff},
    )


# htmx
def calculate_total_price(request):
    entity_type = request.user.entity.entity_type
    total_price = 0
    if request.htmx:
        room = get_object_or_404(Room, id=request.POST.get("room"))
        reservation_type = request.POST.get("reservation_type")
        if reservation_type == ReservationTypeChoices.WHOLE_DAY:
            total_price = calculate_discount_price(entity_type, room.price_all_day)
        elif reservation_type in [
            ReservationTypeChoices.MORNING,
            ReservationTypeChoices.AFTERNOON,
        ]:
            total_price = calculate_discount_price(entity_type, room.price_half_day)
        elif reservation_type == ReservationTypeChoices.HOURLY:
            start_time_str = request.POST.get("start_time")
            end_time_str = request.POST.get("end_time")
            try:
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()
                today = datetime.today().date()
                start_datetime = datetime.combine(today, start_time)
                end_datetime = datetime.combine(today, end_time)
                total_price = calculate_reservation_price(
                    start_datetime, end_datetime, room.price
                )
                total_price = calculate_discount_price(entity_type, total_price)
            except ValueError:
                total_price = 0
        return render(
            request,
            "reservations/total_price.html",
            {
                "total_price": delete_zeros(total_price),
            },
        )
    return JsonResponse({"error": ""}, status=405)


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


class ReservationCancelledView(StandardSuccess):
    page_title = _("Reservation cancelled")
    description = _("Reservation cancelled.")
    url = reverse_lazy("reservations:reservations_list")

    def get_url(self):
        try:
            reversed_url = reverse(self.url)
        except NoReverseMatch:
            return self.url
        return reversed_url


def reservations_calendar_view(request):
    if not request.user.entity:
        return redirect("home")
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
                "is_staff": request.user.is_staff,
                "reservation_id": reservation.id,
            }
            data.append(reservation_data)
        return JsonResponse(data, safe=False)
