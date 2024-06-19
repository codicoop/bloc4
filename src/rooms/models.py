from django.core.validators import validate_image_file_extension
from django.db import models
from django.utils.translation import gettext_lazy as _

from project.fields import flowbite
from project.models import BaseModel
from project.storage_backends import PrivateMediaStorage


class Room(BaseModel):
    class RoomTypeChoices(models.TextChoices):
        """
        List of room types
        """

        EVENT_ROOM = "event_room", _("Event Room")

    name = flowbite.ModelCharField(
        _("Name"),
        max_length=50,
        blank=False,
        null=False,
        unique=True,
        help_text=_("Name of the room"),
    )
    location = flowbite.ModelCharField(
        _("Location"),
        max_length=50,
        blank=True,
        default="",
        null=False,
        help_text=_("Room location"),
    )
    price = flowbite.ModelFloatField(
        _("Price"),
        blank=False,
        null=False,
        help_text=_("Hourly price"),
    )
    capacity = flowbite.ModelIntegerField(
        _("Capacity"),
        blank=False,
        default=0,
        null=False,
        help_text=_("Maximum seating capacity of the room"),
    )
    picture = flowbite.ModelImageField(
        _("Picture"),
        blank=True,
        null=False,
        storage=PrivateMediaStorage(),
        validators=[validate_image_file_extension],
        help_text=_("Photo of the room"),
    )
    equipment = flowbite.ModelCharField(
        _("Equipment"),
        max_length=500,
        blank=False,
        null=False,
        help_text=_("Equipment available in the room"),
    )
    room_type = flowbite.ModelCharField(
        _("Room type"),
        max_length=50,
        choices=RoomTypeChoices,
        blank=False,
        null=False,
        help_text=_("Room type"),
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("room")
        verbose_name_plural = _("rooms")

    def __str__(self):
        return f"{self.name}"
