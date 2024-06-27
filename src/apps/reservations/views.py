from datetime import timedelta, datetime


from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse, NoReverseMatch
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View
from django.views.generic.list import ListView

from apps.reservations.forms import ReservationForm
from apps.reservations.models import Reservation
from apps.reservations.services import send_confirmation_reservation
from apps.rooms.models import Room
from project.views import StandardSuccess


class ReservationsListView(ListView):
    model = Reservation
    template_name = "reservations/reservations_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reservations"] = Reservation.objects.filter(
            entity=self.request.user.entity
        )
        return context

    def post(self, request, *args, **kwargs):
        if "create" in request.POST:
            return redirect("reservations:create_reservation")
        if "calendar" in request.POST:
            return redirect("reservations:reservations_calendar")


def create_reservation_view(request):
    if request.method == "GET":
        form = ReservationForm()
    else:
        form = ReservationForm(request.POST)

        # Validation of room availability
        room = Reservation.objects.filter(
            (
                Q(start_time__gte=form.data["start_time"])
                & (Q(start_time__lte=form.data["end_time"]))
                | Q(end_time__lte=form.data["end_time"])
                & (Q(end_time__gte=form.data["start_time"]))
            ),
            room__id=form.data["room"],
            date=form.data["date"],
        ).exists()
        if room:
            form.add_error(
                "end_time", _("The room is not available for this time period.")
            )
            return render(
                request,
                "reservations/create_reserves.html",
                {"form": form},
            )

        if form.is_valid():
            reservation = form.save(commit=False)
            # User is assigned to the reservation
            reservation.reserved_by = request.user

            # Entity is assigned to the reservation
            reservation.entity = request.user.entity

            # Reserve price is assigned
            room = Room.objects.get(id=form.data["room"])
            room_time = datetime.strptime(
                form.data["end_time"], "%H:%M"
            ) - datetime.strptime(form.data["start_time"], "%H:%M")
            room_time_hours = room_time.total_seconds() // 3600
            reservation.total_price = room_time_hours * float(room.price)

            # The end of the reservation is modified according to full reservation hours
            reservation.end_time = datetime.strptime(
                form.data["start_time"], "%H:%M"
            ) + timedelta(hours=room_time_hours)

            reservation.save()
            form.save()
            # send_confirmation_reservation(form.data)
        return redirect("reservations:reservations_success")
    return render(
        request,
        "reservations/create_reserves.html",
        {"form": form},
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


class ReservationsCalendarView(TemplateView):
    template_name = "reservations/full_calendar.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        reservations = Reservation.objects.all()
        context["reservations"] = reservations
        return context


class AjaxCalendarFeed(View):
    def get(self, request, *args, **kwargs):
        data = []

        # FullCalendar passes ISO8601 formatted date strings
        try:
            start = parse_datetime(request.GET["start"])
            end = parse_datetime(request.GET["end"])
        except:
            return JsonResponse(data, safe=False)

        reservations = Reservation.objects.all()
        for reservation in reservations:
            reservation_data = {
                "room": reservation.room.name,
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
            }
            data.append(reservation_data)
        return JsonResponse(data, safe=False)


def date_to_full_calendar_format(date_obj):
    aware_date = timezone.localtime(date_obj)
    return aware_date.strftime("%Y-%m-%dT%H:%M:%S")
