from datetime import datetime
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.db.models import Q, Sum
from django.db.models.functions import ExtractYear
from django.urls import reverse
from django.utils import formats, timezone
from extra_settings.models import Setting

from apps.entities.choices import EntityTypesChoices
from apps.entities.models import MonthlyBonus
from apps.reservations import constants
from apps.reservations.choices import (
    ReservationTypeChoices,
)
from apps.reservations.constants import MONTHS
from apps.reservations.models import Reservation
from apps.rooms.choices import RoomTypeChoices
from project.post_office import send


def send_mail_reservation(reservation, action):
    payment_info = ""
    entity_type = reservation.entity.entity_type
    recipients = [reservation.reserved_by.email]
    if "bloc4" in action:
        if not Setting.get("RESERVATIONS_EMAIL"):
            return
        recipients = [Setting.get("RESERVATIONS_EMAIL")]
    if Setting.get("PAYMENT_INFORMATION") and entity_type in [
        EntityTypesChoices.GENERAL,
        EntityTypesChoices.OUTSIDE,
    ]:
        payment_info = Setting.get("PAYMENT_INFORMATION")
    context = {
        "reserved_by": reservation.reserved_by,
        "canceled_by": reservation.canceled_by,
        "current_date": str(
            formats.date_format(
                timezone.now().date(),
                format="SHORT_DATE_FORMAT",
                use_l10n=True,
            )
        ),
        "current_time": str(
            formats.time_format(timezone.localtime(timezone.now()).time())
        ),
        "date_reservation": reservation.date,
        "start_time_reservation": reservation.start_time,
        "end_time_reservation": reservation.end_time,
        "room": reservation.room,
        "entity": reservation.entity.fiscal_name,
        "user_email": reservation.reserved_by.email,
        "total_price": reservation.total_price(),
        "status": reservation.get_status_display().lower(),
        "payment_info": payment_info,
        "reservation_url_admin": f"{settings.ABSOLUTE_URL}/"
        f"admin/reservations/reservation/{reservation.id}",
    }
    send(
        recipients=recipients,
        template=action,
        context=context,
    )


def date_to_full_calendar_format(date_obj):
    aware_date = timezone.localtime(date_obj)
    return aware_date.strftime("%Y-%m-%dT%H:%M:%S")


def calculate_reservation_price(start_time, end_time, price):
    if end_time <= start_time:
        return 0
    if isinstance(price, str):
        price = float(price.replace(",", "."))
    base_price = price * Decimal((end_time - start_time).total_seconds() / 3600)
    return base_price


def calculate_discount_price(entity_type, price):
    discount = EntityTypesChoices(entity_type).get_discount_percentage()
    price = Decimal(price)
    return price + price * discount


def get_total_price(reservation_type, entity_type, room, start_time, end_time):
    if reservation_type == ReservationTypeChoices.WHOLE_DAY:
        total_price = calculate_discount_price(entity_type, room.price_all_day)
    elif reservation_type in [
        ReservationTypeChoices.MORNING,
        ReservationTypeChoices.AFTERNOON,
    ]:
        total_price = calculate_discount_price(entity_type, room.price_half_day)
    else:
        start_time = datetime.combine(datetime.today(), start_time)
        end_time = datetime.combine(datetime.today(), end_time)
        price = calculate_discount_price(entity_type, room.price)
        total_price = calculate_reservation_price(start_time, end_time, price)
    return total_price


def parse_time(time_str):
    if not time_str:
        return False
    try:
        return datetime.strptime(time_str, "%H:%M:%S").time()
    except ValueError:
        return datetime.strptime(time_str, "%H:%M").time()


def get_years_and_months(reservations):
    current_year = datetime.now().year
    current_month = datetime.now().month
    years_with_reservations = (
        reservations.annotate(year=ExtractYear("date"))
        .values_list("year", flat=True)
        .distinct()
    )
    years_list = [
        {"year": year, "current": (year == current_year)}
        for year in sorted(set(years_with_reservations))
    ]
    if current_year not in [year["year"] for year in years_list]:
        years_list.append({"year": current_year, "current": True})

    months_list = [
        {"month": month, "name": MONTHS[month], "current": (month == current_month)}
        for month in range(1, 13)
    ]
    return months_list, years_list


def get_monthly_bonus(monthly_bonus, reservations):
    amount_left = monthly_bonus.amount
    bonus_price = 0
    if amount_left > 0:
        for reservation in reservations:
            today = datetime.today().date()
            # reservation.start_time and reservation.end_time contain only the
            # time, i.e. 11:00, but we need a full date object with that time.
            # The .combine creates it, i.e.
            # reservation.start_time=datetime.time(11, 0)
            # After the combine:
            # start_datetime=datetime.datetime(2025, 4, 3, 11, 0).
            start_datetime = datetime.combine(today, reservation.start_time)
            end_datetime = datetime.combine(today, reservation.end_time)
            # Getting the duration of the reservation in hours:
            reservation_time = Decimal(
                (end_datetime - start_datetime).total_seconds() / 3600
            )
            if amount_left - reservation_time < 0:
                bonus_price += amount_left * reservation.base_price / reservation_time
                return bonus_price, 0
            amount_left -= reservation_time
            bonus_price += reservation.base_price
            if amount_left == 0:
                break
    return bonus_price, amount_left


def get_monthly_bonus_totals(reservations, entity, month, year, room_type):
    totals = {
        "discounted_hours_amount": 0,
        "discounted_hours_amount_left": 0,
        "base_price": 0,
        "vat": 0,
        "total_price": 0,
    }
    reservation_model = apps.get_model("reservations", "Reservation")
    active_reservations = reservations.filter(
        Q(
            status__in=[
                reservation_model.StatusChoices.PENDING,
                reservation_model.StatusChoices.CONFIRMED,
            ]
        ) & Q(
            room__room_type=room_type
        )
    )
    totals["base_price"] = Decimal(
        active_reservations.aggregate(total_sum=Sum("base_price"))["total_sum"]
        or
        0
    )
    if room_type is RoomTypeChoices.MEETING_ROOM:
        """ Monthly discount of hours only applies to meeting rooms. """
        monthly_bonus = MonthlyBonus.objects.filter(
            entity=entity,
            date__year=year,
            date__month=month,
        ).first()
        if active_reservations and monthly_bonus:
            bonus_price, amount_left = get_monthly_bonus(
                monthly_bonus,
                active_reservations,
            )
            totals["base_price"] = totals["base_price"] - bonus_price
            totals["discounted_hours_amount"] = monthly_bonus.amount
            totals["discounted_hours_amount_left"] = amount_left
    totals["vat"] = totals["base_price"] * constants.VAT
    totals["total_price"] = totals["base_price"] + totals["vat"]
    return totals


def convert_datetime_to_str(reservation):
    reservation_date = reservation.date
    start_time = reservation.start_time
    end_time = reservation.end_time
    start_datetime = datetime.combine(reservation_date, start_time).replace(tzinfo=None)
    end_datetime = datetime.combine(reservation_date, end_time).replace(tzinfo=None)
    start_time_str = start_datetime.isoformat() + "+01:00"
    end_time_str = end_datetime.isoformat() + "+01:00"
    return start_time_str, end_time_str


def get_filter_reservations_context(filter_year, filter_month, entity):
    """
    entity: an Entity instance
    """
    reservations = Reservation.objects.filter(
        entity=entity, date__month=filter_month, date__year=filter_year
    ).order_by("date")
    unbilled_reservations = reservations.filter(is_billed=False).first()

    # This refactor would show the discounts card if the entity have free
    # monthly hours assigned. Still, this, the if for is_monthly_bonus in the
    # template and the context var might be removed if we decide that this card
    # is not a "discounts card" but a monthly totals card and we display it to
    # everyone.
    is_monthly_bonus = False
    if (
        hasattr(entity, "entity_privilege")
        and entity.entity_privilege.monthly_hours_meeting
    ):
        is_monthly_bonus = True
    meeting_rooms_totals = get_monthly_bonus_totals(
        reservations,
        entity,
        filter_month,
        filter_year,
        RoomTypeChoices.MEETING_ROOM,
    )
    classrooms_totals = get_monthly_bonus_totals(
        reservations,
        entity,
        filter_month,
        filter_year,
        RoomTypeChoices.CLASSROOM,
    )
    event_rooms_totals = get_monthly_bonus_totals(
        reservations,
        entity,
        filter_month,
        filter_year,
        RoomTypeChoices.EVENT_ROOM,
    )
    context = {
        "is_monthly_bonus": is_monthly_bonus,
        "amount_left": 0,
        "base_price": 0,
        "bonus_price": 0,
        "reservations": reservations,
        "month": MONTHS.get(int(filter_month), "")[:3] + ".",
        "year": filter_year,
        "entity": entity,
        "meeting_rooms_totals": meeting_rooms_totals,
        "classrooms_totals": classrooms_totals,
        "event_rooms_totals": event_rooms_totals,
        "totals": {
            "meeting_rooms": meeting_rooms_totals["total_price"],
            "classrooms": classrooms_totals["total_price"],
            "event_rooms": event_rooms_totals["total_price"],
            "sum": (
                meeting_rooms_totals["total_price"]
                + classrooms_totals["total_price"]
                + event_rooms_totals["total_price"]
            ),
        },
        # Context only used by the "Monthly summary" section:
        "mark_month_as_billed_url": reverse(
            "reservations:mark_reservations_as_billed",
            kwargs={
                "year": filter_year,
                "month": filter_month,
                "entity": entity.pk,
            },
        ),
        # If a single reservation is not billed, we consider the month as not
        # billed.
        "month_is_billed": not unbilled_reservations,
    }
    return context
