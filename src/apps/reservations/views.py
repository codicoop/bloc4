import uuid
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import NoReverseMatch, reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.views.generic.list import ListView

from apps.entities.choices import EntityTypesChoices
from apps.reservations.forms import ReservationForm
from apps.reservations.models import Reservation
from apps.reservations.services import (
    calculate_discount_price,
    calculate_reservation_price,
    date_to_full_calendar_format,
    delete_zeros,
    send_mail_reservation,
)
from apps.rooms.choices import RoomTypeChoices
from apps.rooms.constanst import CALENDAR_TEXT_COLOR
from apps.rooms.models import Room
from project.views import StandardSuccess


class ReservationsListView(ListView):
    model = Reservation
    template_name = "reservations/reservations_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reservations"] = Reservation.objects.filter(
            entity=self.request.user.entity
        ).order_by("-date")
        return context

    def post(self, request, *args, **kwargs):
        if "create" in request.POST:
            return redirect("reservations:create_reservation")
        if "calendar" in request.POST:
            return redirect("reservations:reservations_calendar")
        if "cancel_reservation" in request.POST:
            try:
                reservation = Reservation.objects.get(
                    id=request.POST.get("cancel_reservation")
                )
            except Reservation.DoesNotExist:
                return JsonResponse({"error": _("Reservation not found.")}, status=404)
            reservation.status = Reservation.StatusChoices.CANCELED
            reservation.canceled_by = request.user
            reservation.canceled_at = timezone.now()
            reservation.save()
            send_mail_reservation(reservation, "reservation_canceled_user")
            send_mail_reservation(reservation, "reservation_canceled_bloc4")
            return redirect("reservations:reservations_list")


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
        start_time = start_datetime.time()
        end_time = end_datetime.time()
        price_discount = calculate_discount_price(entity_type, room.price)
        total_price = calculate_reservation_price(
            start_datetime, end_datetime, price_discount
        )
        form = ReservationForm(
            initial={
                "date": date,
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "entity": request.user.entity,
                "room": room.id,
            }
        )
    if request.method == "POST":
        form = ReservationForm(request.POST)
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
            reservation.room = room
            reservation.save()
            form.save()
            send_mail_reservation(reservation, "reservation_request_user")
            send_mail_reservation(reservation, "reservation_request_bloc4")
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
    return render(
        request,
        "reservations/details.html",
        {"reservation": reservation, "is_staff": is_staff},
    )


def calculate_total_price(request):
    total_price = 0
    if request.htmx:
        selected_price = request.POST.get("selected_price")
        element_id = request.POST.get("id")
        if (
            element_id == "hourly-day"
            or element_id == "start-hourly-day"
            or element_id == "end-hourly-day"
        ):
            start_time_str = request.POST.get("start_time")
            end_time_str = request.POST.get("end_time")
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            today = datetime.today().date()
            start_datetime = datetime.combine(today, start_time)
            end_datetime = datetime.combine(today, end_time)
            total_price = calculate_reservation_price(
                start_datetime, end_datetime, selected_price
            )
        else:
            total_price = delete_zeros(selected_price)
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


def reservations_calendar_view(request):
    context = {}
    room_types = Room.objects.values_list("room_type", flat=True).distinct()
    unique_room_types = {
        room_type: RoomTypeChoices(room_type).label for room_type in room_types
    }
    unique_room_types = {"all": _("All")} | unique_room_types
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
