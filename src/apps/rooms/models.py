from django.core.validators import MinValueValidator, validate_image_file_extension
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.rooms.choices import RoomTypeChoices
from project.models import BaseModel
from project.storage_backends import PublicMediaStorage


class Room(BaseModel):
    name = models.CharField(
        _("Name"),
        max_length=50,
        blank=False,
        default="",
        unique=True,
    )
    code = models.CharField(
        _("Room code"),
        max_length=50,
        blank=True,
        default="",
    )
    price = models.DecimalField(
        _("Hourly price (VAT not included)"),
        default=0,
        null=False,
        validators=[MinValueValidator(0.0)],
        decimal_places=2,
        max_digits=6,
    )
    price_half_day = models.DecimalField(
        _("Half day price (VAT not included)"),
        default=0,
        null=False,
        validators=[MinValueValidator(0.0)],
        decimal_places=2,
        max_digits=6,
    )
    price_all_day = models.DecimalField(
        _("All day price (VAT not included)"),
        default=0,
        null=False,
        validators=[MinValueValidator(0.0)],
        decimal_places=2,
        max_digits=6,
    )
    capacity = models.IntegerField(
        _("Capacity"),
        default=0,
        null=False,
        help_text=_("Maximum seating capacity of the room"),
    )
    picture = models.ImageField(
        _("Picture"),
        blank=False,
        default="",
        storage=PublicMediaStorage(),
        validators=[validate_image_file_extension],
    )
    equipment = models.CharField(
        _("Equipment"),
        max_length=500,
        blank=True,
        default="",
        help_text=_("Available equipment in the room"),
    )
    description = models.CharField(
        _("Description"),
        max_length=500,
        blank=False,
        default="",
    )
    room_type = models.CharField(
        _("Room type"),
        max_length=50,
        choices=RoomTypeChoices,
        blank=False,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("room")
        verbose_name_plural = _("rooms")

    def __str__(self):
        return f"{self.name}"
