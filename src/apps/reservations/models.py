from datetime import date, datetime, timedelta

from django.core.validators import (
    MinValueValidator,
    ValidationError,
    validate_image_file_extension,
)
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from extra_settings.models import Setting

from apps.entities.choices import EntityTypesChoices
from apps.reservations import constants
from apps.reservations.choices import (
    ActivityTypeChoices,
    Bloc4TypeChoices,
    ReservationTypeChoices,
)
from apps.reservations.constants import (
    END_TIME,
    END_TIME_MINUS_ONE,
    START_TIME,
    START_TIME_PLUS_ONE,
)
from apps.rooms.choices import RoomTypeChoices
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

    title = models.CharField(
        _("Title"),
        max_length=100,
        blank=False,
        default="",
    )
    reservation_type = models.CharField(
        _("Choose the option that interests you most"),
        choices=ReservationTypeChoices,
        default=ReservationTypeChoices.HOURLY,
        blank=False,
        max_length=10,
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
    )
    end_time = models.TimeField(
        _("End time"),
        null=False,
        blank=False,
    )
    assistants = models.IntegerField(
        _("Assistants"),
        blank=False,
        null=False,
        default=1,
        validators=[MinValueValidator(1)],
    )
    room = models.ForeignKey(
        "rooms.Room",
        verbose_name=_("room"),
        null=False,
        on_delete=models.CASCADE,
        related_name="reservation_room",
        help_text=_(
            "If you want to change the room and notify the user,"
            " first, change the room, save and then click the button to notify."
        ),
    )
    is_budgeted = models.BooleanField(
        _("Is budgeted?"),
        null=False,
        default=False,
    )
    is_paid = models.BooleanField(
        _("Is paid?"),
        null=False,
        default=False,
    )
    catering = models.BooleanField(
        _("Do I need catering service?"),
        blank=True,
        default=False,
    )
    notes = models.TextField(
        _("Do you need to tell us something?"),
        max_length=500,
        blank=False,
        default="",
    )
    activity_type = models.CharField(
        _("Ateneu's activity"),
        choices=ActivityTypeChoices,
        default=ActivityTypeChoices.BLOC4,
        blank=False,
        max_length=10,
    )
    bloc4_type = models.CharField(
        _("Service type Bloc4BCN"),
        choices=Bloc4TypeChoices,
        default="",
        blank=True,
        max_length=20,
    )
    privacy = models.CharField(
        _("Type of event"),
        choices=PrivacyChoices,
        blank=False,
        null=False,
        default=PrivacyChoices.PRIVATE,
        help_text=_(
            "Public events must be open to all citizens and will "
            "be published in the Bloc4BCN Agenda, subject to approval."
        ),
        max_length=20,
    )
    # Only for public training
    description = models.CharField(
        _("Description"),
        max_length=500,
        blank=True,
        help_text=_(
            "This information will be used in the Bloc4BCN Agenda"
            " publication of this event."
        ),
    )
    poster = models.ImageField(
        _("Poster"),
        blank=True,
        storage=PublicMediaStorage(),
        validators=[validate_image_file_extension],
        help_text=_(
            "This information will be used in the Bloc4BCN Agenda"
            " publication of this event."
        ),
    )
    url = models.URLField(
        _("URL of the activity"),
        max_length=200,
        blank=True,
        default="",
        help_text=_(
            "This information will be used in the Bloc4BCN Agenda"
            " publication of this event."
        ),
    )
    base_price = models.DecimalField(
        _("Total price"),
        null=False,
        blank=False,
        default=0,
        validators=[MinValueValidator(0.0)],
        decimal_places=2,
        max_digits=6,
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
    status = models.CharField(
        choices=StatusChoices,
        null=False,
        blank=False,
        default=StatusChoices.PENDING,
        help_text=_("The Status can only be modified by using the buttons below."),
        verbose_name=_("status"),
        max_length=20,
    )
    checked_in = models.BooleanField(_("checked in"), default=False)
    is_billed = models.BooleanField(_("billed"), default=False)
    billed_at = models.DateTimeField(
        _("billed at"),
        null=True,
        editable=False,
    )
    billed_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        related_name="billed_reservations",
        on_delete=models.SET_NULL,
        verbose_name=_("billed by"),
        editable=False,
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

    def save(self, *args, **kwargs):
        from apps.entities.models import EntityPrivilege, MonthlyBonus

        if self.entity.entity_type in [
            EntityTypesChoices.BLOC4,
            EntityTypesChoices.HOSTED,
        ]:
            try:
                entity_privilege = self.entity.entity_privilege
                monthly_bonus, created = MonthlyBonus.objects.get_or_create(
                    entity=self.entity,
                    date__year=self.date.year,
                    date__month=self.date.month,
                    defaults={
                        "amount": 0,
                        "date": datetime(self.date.year, self.date.month, 1),
                    },
                )
                if created:
                    amount = entity_privilege.monthly_hours_meeting
                    monthly_bonus.amount = amount
                    monthly_bonus.save()
            except EntityPrivilege.DoesNotExist:
                pass
        super(Reservation, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        super().clean()
        errors = {}
        if self.privacy == Reservation.PrivacyChoices.PRIVATE:
            self.url = ""
            self.description = ""
            self.poster = ""
        if self.activity_type != ActivityTypeChoices.BLOC4:
            self.bloc4_type = ""
        if self.activity_type == ActivityTypeChoices.BLOC4 and not self.bloc4_type:
            errors.update(
                {
                    "bloc4_type": ValidationError(
                        _(
                            "If ateneus'activity is "
                            "{activity} this field is required."
                        ).format(activity=ActivityTypeChoices.BLOC4.label),
                    )
                }
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
                                "The reservation must have a minimum "
                                "duration of one hour."
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
                                "{start_time} and {end_time}."
                            ).format(
                                start_time=START_TIME.strftime("%H:%M"),
                                end_time=END_TIME_MINUS_ONE.strftime("%H:%M"),
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
                                "{start_time} and {end_time}."
                            ).format(
                                start_time=START_TIME_PLUS_ONE.strftime("%H:%M"),
                                end_time=END_TIME.strftime("%H:%M"),
                            )
                        )
                    },
                )
                raise ValidationError(errors)
            valid_minutes = [0, 15, 30, 45]
            if self.start_time.minute not in valid_minutes:
                errors.update(
                    {
                        "start_time": ValidationError(
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
                if room.room_type != RoomTypeChoices.MEETING_ROOM:
                    if (
                        self.privacy == Reservation.PrivacyChoices.PUBLIC
                        and not self.description
                    ):
                        errors.update(
                            {
                                "description": ValidationError(
                                    _("If training is public, this field is required.")
                                )
                            },
                        )
                        raise ValidationError(errors)
                if (
                    room.room_type == RoomTypeChoices.MEETING_ROOM
                    and self.privacy == Reservation.PrivacyChoices.PUBLIC
                ):
                    errors.update(
                        {
                            "privacy": ValidationError(
                                _(
                                    "{room_type} cannot be used in public trainings."
                                ).format(room_type=RoomTypeChoices.MEETING_ROOM.label)
                            )
                        },
                    )
                    raise ValidationError(errors)
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
                if self.assistants > room.capacity:
                    errors.update(
                        {
                            "assistants": ValidationError(
                                _(
                                    "The maximum capacity for this room "
                                    "is {capacity}."
                                ).format(capacity=room.capacity)
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
                            "entity": ValidationError(
                                _("This user belong to {entity}.").format(
                                    entity=user_entity
                                )
                            )
                        },
                    )
                    raise ValidationError(errors)
        except AttributeError:
            pass
        try:
            entity = self.entity
            if self.date:
                # Validation reservation is made within maximum day
                # in advance configured.
                future_date = date.today() + timedelta(
                    days=Setting.get("MAXIMUM_ADVANCE_RESERVATION_DAYS"),
                )
                if not entity.reservation_privilege and self.date > future_date:
                    errors.update(
                        {
                            "date": ValidationError(
                                _(
                                    "The maximum advance reservation "
                                    "period is %(days)s days."
                                )
                                % {
                                    "days": Setting.get(
                                        "MAXIMUM_ADVANCE_RESERVATION_DAYS"
                                    )
                                }
                            )
                        },
                    )
                    raise ValidationError(errors)
        except AttributeError:
            pass

    def vat(self):
        return self.base_price * constants.VAT

    def total_price(self):
        return self.base_price + self.vat()

    def mark_as_billed(self, user=None):
        if user:
            self.billed_by = user
        self.billed_at = datetime.now()
        self.is_billed = True
        self.save()
