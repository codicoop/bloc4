from django.utils import formats, timezone

from project.post_office import send


def send_confirmation_reservation(reservation):
    context = {
        "reserved_by": reservation["reserved_by"],
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
        "date_reservation": reservation["date"],
        "start_time_reservation": reservation["start_time"],
        "end_time_reservation": reservation["end_time"],
        "room": reservation["room"],
        "entity": reservation["entity"],
        "total_price": reservation["total_price"],
        "status": reservation["status"],
    }
    send(
        recipients=[
            reservation["entity__email"],
        ],
        template="created_reservation",
        context=context,
    )
