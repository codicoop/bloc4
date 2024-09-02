from datetime import datetime, timedelta

from constance import config
from django.conf import settings
from django.utils import formats, timezone

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
        "total_price": reservation.total_price,
        "status": reservation.status,
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


def calculate_reservation_price(start_time, end_time, price):
    if end_time <= start_time:
        return 0
    total_price = price * (end_time - start_time).total_seconds() / 3600
    formatted_price = int(total_price) if total_price.is_integer() else total_price
    return formatted_price
