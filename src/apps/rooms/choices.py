from django.db import models
from django.utils.translation import gettext_lazy as _


class RoomTypeChoices(models.TextChoices):
    """
    List of room types
    """

    EVENT_ROOM = "event_room", _("Event Room")
    CLASSROOM = "classroom", _("Classroom")
    MEETING_ROOM = "meeting_room", _("Meeting room")
