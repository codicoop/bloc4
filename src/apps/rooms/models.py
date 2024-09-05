from django.core.validators import MinValueValidator, validate_image_file_extension
from django.utils.translation import gettext_lazy as _

from apps.rooms.choices import RoomTypeChoices
from project.fields import flowbite
from project.models import BaseModel
from project.storage_backends import PublicMediaStorage


class Room(BaseModel):
    name = flowbite.ModelCharField(
        _("Name"),
        max_length=50,
        blank=False,
        default="",
        unique=True,
        help_text=_("Name of the room"),
    )
    code = flowbite.ModelCharField(
        _("Room code"),
        max_length=50,
        blank=True,
        default="",
    )
    price = flowbite.ModelFloatField(
        _("Hourly price"),
        default=0,
        null=False,
        validators=[MinValueValidator(0.0)],
        help_text=_("Price per hour of the room"),
    )
    price_half_day = flowbite.ModelFloatField(
        _("Half day price"),
        default=0,
        null=False,
        validators=[MinValueValidator(0.0)],
        help_text=_("Price per half day of the room"),
    )
    price_all_day = flowbite.ModelFloatField(
        _("All day price"),
        default=0,
        null=False,
        validators=[MinValueValidator(0.0)],
        help_text=_("Price per all day of the room"),
    )
    capacity = flowbite.ModelIntegerField(
        _("Capacity"),
        default=0,
        null=False,
        help_text=_("Maximum seating capacity of the room"),
    )
    picture = flowbite.ModelImageField(
        _("Picture"),
        blank=False,
        default="",
        storage=PublicMediaStorage(),
        validators=[validate_image_file_extension],
        help_text=_("Photo of the room"),
    )
    equipment = flowbite.ModelCharField(
        _("Equipment"),
        max_length=500,
        blank=True,
        default="",
        help_text=_("Available equipment in the room"),
    )
    description = flowbite.ModelCharField(
        _("Description"),
        max_length=500,
        blank=False,
        default="",
        help_text=_("Description of the main aspects of the room."),
    )
    room_type = flowbite.ModelCharField(
        _("Room type"),
        max_length=50,
        choices=RoomTypeChoices,
        blank=False,
        help_text=_("Room type"),
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("room")
        verbose_name_plural = _("rooms")

    def __str__(self):
        return f"{self.name}"
