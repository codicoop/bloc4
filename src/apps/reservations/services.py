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
            sender=config.RESERVATIONS_EMAIL,
            recipients=recipients,
            template=action,
            context=context,
        )
