from datetime import datetime, timedelta

from constance import config
from django.conf import settings
from django.db.models import Q, Sum
from django.db.models.functions import ExtractYear
from django.utils import formats, timezone

from apps.entities.choices import EntityTypesChoices
from apps.entities.models import MonthlyBonus
from apps.reservations.constants import MONTHS
from apps.rooms.choices import RoomTypeChoices
from project.post_office import send


def send_mail_reservation(reservation, action):
    if "bloc4" in action:
        recipients = [config.RESERVATIONS_EMAIL]
    else:
        recipients = [reservation.reserved_by.email]
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
        "total_price": reservation.total_price,
        "status": reservation.get_status_display().lower(),
        "reservation_url_admin": f"{settings.ABSOLUTE_URL}/"
        f"admin/reservations/reservation/{reservation.id}",
    }
    if config.RESERVATIONS_EMAIL:
        send(
            recipients=recipients,
            template=action,
            context=context,
        )


def date_to_full_calendar_format(date_obj):
    aware_date = timezone.localtime(date_obj)
    return aware_date.strftime("%Y-%m-%dT%H:%M:%S")


def adjust_time(time, minutes, operation):
    today = datetime.today().date()
    time_obj = datetime.combine(today, time)
    delta = timedelta(minutes=minutes)

    if operation == "add":
        new_time_obj = time_obj + delta
    elif operation == "subtract":
        new_time_obj = time_obj - delta

    return new_time_obj.time()


def delete_zeros(value):
    if isinstance(value, str):
        value = float(value.replace(",", "."))
    if not isinstance(value, int):
        if value.is_integer():
            value = int(value)
        else:
            value = round(value, 2)
    return value


def calculate_reservation_price(start_time, end_time, price):
    if end_time <= start_time:
        return 0
    if isinstance(price, str):
        price = float(price.replace(",", "."))
    total_price = price * (end_time - start_time).total_seconds() / 3600
    return total_price


def calculate_discount_price(entity_type, price):
    discount = EntityTypesChoices(entity_type).get_discount_percentage()
    return delete_zeros(price + price * discount)


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


def get_monthly_hours_amount_letf(monthly_bonus, reservations):
    amount_left = float(monthly_bonus.amount)
    bonus_price = 0
    if amount_left > 0:
        reservations = reservations.filter(
            room__room_type=RoomTypeChoices.MEETING_ROOM,
            # reservation_type=ReservationTypeChoices.HOURLY,
        ).order_by("created_at")
        for reservation in reservations:
            today = datetime.today().date()
            start_datetime = datetime.combine(today, reservation.start_time)
            end_datetime = datetime.combine(today, reservation.end_time)
            reservation_time = (end_datetime - start_datetime).total_seconds() / 3600
            if amount_left - reservation_time < 0:
                bonus_price += amount_left * reservation.total_price / reservation_time
                return bonus_price, 0
            amount_left -= reservation_time
            bonus_price += reservation.total_price
            if amount_left == 0:
                break
    return bonus_price, amount_left


def get_monthly_bonus_totals(reservations, filter_year, filter_month, entity):
    from apps.reservations.models import Reservation

    bonuses = {}
    monthly_bonus = MonthlyBonus.objects.filter(
        entity=entity,
        date__year=int(filter_year),
        date__month=int(filter_month),
    ).first()
    if monthly_bonus:
        bonuses["is_monthly_bonus"] = True
        active_reservations = reservations.filter(
            Q(
                status__in=[
                    Reservation.StatusChoices.PENDING,
                    Reservation.StatusChoices.CONFIRMED,
                ]
            )
        )
        (
            bonus_price,
            amount_left,
        ) = get_monthly_hours_amount_letf(monthly_bonus, active_reservations)
        total_price = active_reservations.aggregate(
            total_sum=Sum("total_price"),
        )["total_sum"]
        bonuses["total_price"] = delete_zeros(total_price)
        bonuses["bonus_price"] = delete_zeros(total_price - bonus_price)
        bonuses["amount"] = delete_zeros(monthly_bonus.amount)
        bonuses["amount_left"] = delete_zeros(amount_left)
    return bonuses
