from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.rooms.constanst import (
    CLASSROOM_COLOR,
    EVENT_ROOM_COLOR,
    MEETING_ROOM_COLOR,
)


class RoomTypeChoices(models.TextChoices):
    """
    List of room types
    """

    EVENT_ROOM = "event_room", _("Event Room")
    CLASSROOM = "classroom", _("Classroom")
    MEETING_ROOM = "meeting_room", _("Meeting room")

    def get_room_color(self):
        discounts = {
            self.EVENT_ROOM: EVENT_ROOM_COLOR,
            self.CLASSROOM: CLASSROOM_COLOR,
            self.MEETING_ROOM: MEETING_ROOM_COLOR,
        }
        return discounts.get(self, 0)
