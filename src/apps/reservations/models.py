from django.db import models
from django.utils.translation import gettext_lazy as _

from project.fields import flowbite
from project.models import BaseModel


class Reservation(BaseModel):
    class StatusChoices(models.TextChoices):
        """
        List of reservation statuses
        """

        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        CANCELED = "canceled", _("Canceled")
        REFUSED = "refused", _("Refused")

    date = models.DateField(
        _("Date"),
        auto_now_add=True,
        null=False,
        blank=False,
    )
    start_time = models.DateTimeField(
        _("Start time"),
        null=False,
        blank=False,
        help_text=_("Start time of the reservation"),
    )
    end_time = models.DateTimeField(
        _("End time"),
        null=False,
        blank=False,
        help_text=_("End time of the reservation"),
    )
    motivation = flowbite.ModelCharField(
        _("Motivation"),
        max_length=500,
        blank=True,
        null=True,
        default="",
        help_text=_("Motivation for the reservation"),
    )
    assistants = flowbite.ModelCharField(
        _("Assistants"),
        max_length=500,
        blank=True,
        null=True,
        default="",
        help_text=_("Assistants for the reservation"),
    )
    room = models.ForeignKey(
        "rooms.Room",
        verbose_name=_("room"),
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="reservation_room",
    )
    is_paid = flowbite.ModelBooleanField(
        _("Is paid?"),
        null=False,
        blank=False,
        default=False,
        help_text=_("Is the reservation paid?"),
    )
    total_price = flowbite.ModelFloatField(
        _("Total price"),
        null=True,
        blank=True,
        default=0,
        help_text=_("Total price of the reservation"),
    )
    entity = models.ForeignKey(
        "entities.Entity",
        verbose_name=_("entity"),
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="reservation_entity",
    )
    reserved_by = models.ForeignKey(
        "users.User",
        verbose_name=_("reserved by"),
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="reservation_reserved_by",
    )
    status = flowbite.ModelSelectDropdownField(
        choices=StatusChoices,
        null=False,
        blank=False,
        default=StatusChoices.PENDING,
        help_text=_("Status of the reservation"),
        verbose_name=_("status"),
        max_length=20,
    )

    class Meta:
        ordering = ["-date"]
        verbose_name = _("reservation")
        verbose_name_plural = _("reservations")
        unique_together = ["date", "start_time", "end_time", "room_id"]

    def __str__(self):
        return f"{self.room} | {self.date} {self.start_time} {self.end_time}"
