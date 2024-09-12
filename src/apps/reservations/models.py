from datetime import date, datetime, timedelta

from constance import config
from django.core.validators import (
    MinValueValidator,
    ValidationError,
    validate_image_file_extension,
)
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.reservations.constants import (
    END_TIME,
    END_TIME_MINUS_ONE,
    HALF_TIME,
    START_TIME,
    START_TIME_PLUS_ONE,
)
from apps.reservations.services import (
    calculate_discount_price,
    calculate_reservation_price,
)
from project.fields import flowbite
from project.models import BaseModel
from project.storage_backends import PublicMediaStorage


class Reservation(BaseModel):
    class StatusChoices(models.TextChoices):
        """
        List of reservation statuses
        """

        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        CANCELED = "canceled", _("Canceled")
        REFUSED = "refused", _("Refused")

    class PrivacyChoices(models.TextChoices):
        PRIVATE = "private", _("Private training")
        PUBLIC = "public", _("Public training")

    title = flowbite.ModelCharField(
        _("Title"),
        max_length=100,
        blank=False,
        default="",
        help_text=_("Title for the reservation"),
    )
    date = models.DateField(
        _("Date"),
        null=False,
        blank=False,
    )
    start_time = models.TimeField(
        _("Start time"),
        null=False,
        blank=False,
        help_text=_("Start time of the reservation"),
    )
    end_time = models.TimeField(
        _("End time"),
        null=False,
        blank=False,
        help_text=_("End time of the reservation"),
    )
    assistants = flowbite.ModelIntegerField(
        _("Assistants"),
        blank=False,
        null=True,
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_("Assistants for the reservation"),
    )
    room = models.ForeignKey(
        "rooms.Room",
        verbose_name=_("room"),
        null=False,
        on_delete=models.CASCADE,
        related_name="reservation_room",
    )
    is_paid = flowbite.ModelBooleanField(
        _("Is paid?"),
        null=False,
        default=False,
        help_text=_("Is the reservation paid?"),
    )
    catering = flowbite.ModelBooleanField(
        _("Do I need catering service?"),
        null=False,
        blank=False,
        default=False,
    )
    notes = flowbite.ModelCharField(
        _("Notes"),
        max_length=500,
        blank=False,
        default="",
        help_text=_("Notes for the reservation"),
    )
    bloc4_reservation = flowbite.ModelBooleanField(
        _("Reservation for Bloc4 services"),
        null=False,
        blank=False,
        default=False,
    )
    privacy = flowbite.ModelSelectDropdownField(
        choices=PrivacyChoices,
        null=False,
        blank=False,
        default=PrivacyChoices.PRIVATE,
        help_text=_("If the training is public, it will appear in the bloc4 agenda"),
        verbose_name=_("privacy"),
        max_length=20,
    )
    # Only for public training
    description = flowbite.ModelCharField(
        _("Description"),
        max_length=500,
        blank=True,
        null=True,
        help_text=_("Description for the reservation"),
    )
    poster = flowbite.ModelImageField(
        _("Poster"),
        blank=True,
        null=True,
        storage=PublicMediaStorage(),
        validators=[validate_image_file_extension],
    )
    url = flowbite.ModelUrlField(
        _("URL of the activity"), max_length=200, blank=True, null=True, default=""
    )
    total_price = flowbite.ModelFloatField(
        _("Total price"),
        null=False,
        blank=False,
        default=0,
        validators=[MinValueValidator(0.0)],
        help_text=_("Total price will be calculated on save."),
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
    canceled_by = models.ForeignKey(
        "users.User",
        verbose_name=_("canceled by"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reservation_canceled_by",
    )
    canceled_at = models.DateTimeField(
        verbose_name=_("canceled_at"),
        null=True,
        blank=True,
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
        return f"{self.room} | {self.date}"

    def get_admin_url(self):
        return reverse(
            "admin:reservations_reservation_change",
            args=(self.pk,),
        )

    @property
    def calculated_total_price(self):
        total_price = 0
        if self.start_time == START_TIME and self.end_time == END_TIME:
            total_price = calculate_discount_price(
                self.entity.entity_type, self.room.price_all_day
            )
        elif self.start_time == START_TIME and self.end_time == HALF_TIME:
            total_price = calculate_discount_price(
                self.entity.entity_type, self.room.price_half_day
            )
        elif self.start_time == HALF_TIME and self.end_time == END_TIME:
            total_price = calculate_discount_price(
                self.entity.entity_type,
                self.room.price_half_day,
            )
        else:
            start_time = datetime.combine(datetime.today(), self.start_time)
            end_time = datetime.combine(datetime.today(), self.end_time)
            price = calculate_discount_price(self.entity.entity_type, self.room.price)
            total_price = calculate_reservation_price(start_time, end_time, price)
        return total_price

    def save(self, *args, **kwargs):
        self.total_price = self.calculated_total_price
        super(Reservation, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        super().clean()
        errors = {}
        if self.privacy == Reservation.PrivacyChoices.PRIVATE:
            self.url = ""
            self.description = ""
            self.poster = ""
        if self.privacy == Reservation.PrivacyChoices.PUBLIC and not self.description:
            errors.update(
                {
                    "description": ValidationError(
                        _("If training is public, this field is required.")
                    )
                },
            )
            raise ValidationError(errors)
        if self.date:
            # Validation reservation is made within maximum day in advance configured.
            future_date = date.today() + timedelta(
                days=config.MAXIMUM_ADVANCE_RESERVATION_DAYS
            )
            if not self.entity.reservation_privilege and self.date > future_date:
                errors.update(
                    {
                        "date": ValidationError(
                            _(
                                "The maximum advance reservation period is %(days)s "
                                "days."
                            )
                            % {"days": config.MAXIMUM_ADVANCE_RESERVATION_DAYS}
                        )
                    },
                )
                raise ValidationError(errors)
            # Validates that the reservation date is later than the current date.
            if self.date < date.today():
                errors.update(
                    {
                        "date": ValidationError(
                            _("The date must be greater than the current date.")
                        )
                    },
                )
                raise ValidationError(errors)
        if self.start_time and self.end_time:
            # Validates that the reservation end time is later than the start time.
            if self.end_time < self.start_time:
                errors.update(
                    {
                        "end_time": ValidationError(
                            _("The end time must be greater than the start time.")
                        )
                    },
                )
                raise ValidationError(errors)

            # Validates that the reservation duration is between 1 and 20 hours.
            if datetime.strptime(str(self.end_time), "%H:%M:%S") - datetime.strptime(
                str(self.start_time), "%H:%M:%S"
            ) < timedelta(hours=1):
                errors.update(
                    {
                        "end_time": ValidationError(
                            _(
                                "The reservation must have a minimum duration of one "
                                "hour."
                            )
                        )
                    },
                )
                raise ValidationError(errors)
            if datetime.strptime(str(self.end_time), "%H:%M:%S") - datetime.strptime(
                str(self.start_time), "%H:%M:%S"
            ) > timedelta(hours=20):
                errors.update(
                    {
                        "end_time": ValidationError(
                            _("The maximum standby time is 20 hours.")
                        )
                    },
                )
                raise ValidationError(errors)
            if not (START_TIME <= self.start_time <= END_TIME_MINUS_ONE):
                errors.update(
                    {
                        "start_time": ValidationError(
                            _(
                                "The start time must be between "
                                '{START_TIME.strftime("%H:%M")} and '
                                '{END_TIME_MINUS_ONE.strftime("%H:%M")}.'
                            )
                        )
                    },
                )
                raise ValidationError(errors)
            if not START_TIME_PLUS_ONE <= self.end_time <= END_TIME:
                errors.update(
                    {
                        "end_time": ValidationError(
                            _(
                                "The end time must be between "
                                '{START_TIME_PLUS_ONE.strftime("%H:%M")} and '
                                '{END_TIME.strftime("%H:%M")}.'
                            )
                        )
                    },
                )
                raise ValidationError(errors)
            valid_minutes = [0, 15, 30, 45]
            if self.start_time.minute not in valid_minutes:
                errors.update(
                    {
                        "end_time": ValidationError(
                            _("The start time must be in 00, 15, 30 or 45 minutes.")
                        )
                    },
                )
                raise ValidationError(errors)
            if self.end_time.minute not in valid_minutes:
                errors.update(
                    {
                        "end_time": ValidationError(
                            _("The end time must be in 00, 15, 30 or 45 minutes.")
                        )
                    },
                )
                raise ValidationError(errors)
            try:
                room = self.room
                # Validation of room availability
                room_reservation = (
                    Reservation.objects.filter(
                        Q(start_time__lt=self.end_time)
                        & Q(end_time__gt=self.start_time),
                        room__id=room.id,
                        date=self.date,
                    )
                    .exclude(id=self.id)
                    .exclude(
                        status__in=[
                            Reservation.StatusChoices.CANCELED,
                            Reservation.StatusChoices.REFUSED,
                        ]
                    )
                    .exists()
                )
                if room_reservation:
                    errors.update(
                        {
                            "end_time": ValidationError(
                                _("The room is not available for this time period.")
                            )
                        },
                    )
                    raise ValidationError(errors)
                if self.assistants > self.room.capacity:
                    errors.update(
                        {
                            "assistants": ValidationError(
                                _(
                                    f"The maximum capacity for this room "
                                    f"is {self.room.capacity}"
                                )
                            )
                        },
                    )
                    raise ValidationError(errors)
            except AttributeError:
                pass
        try:
            user_entity = self.reserved_by.entity
            if self.entity and user_entity:
                if self.entity != user_entity:
                    errors.update(
                        {
                            "reserved_by": ValidationError(
                                _(f"This user belong to {user_entity} entity.")
                            )
                        },
                    )
                    raise ValidationError(errors)
        except AttributeError:
            pass
