from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.entities.choices import EntityTypesChoices
from project.models import BaseModel
from project.storage_backends import PublicMediaStorage


class Entity(BaseModel):
    entity_email = models.EmailField(
        _("Email address"),
        max_length=100,
        blank=False,
        null=False,
        unique=True,
    )
    fiscal_name = models.CharField(
        _("Fiscal name"),
        max_length=50,
        blank=False,
        null=False,
    )
    nif = models.CharField(
        verbose_name=_("NIF"),
        unique=True,
        max_length=9,
        blank=False,
        null=False,
        help_text=_("Tax identification number"),
    )
    town = models.CharField(
        _("Town"),
        blank=True,
        default="",
    )
    postal_code = models.CharField(
        _("Postal Code"),
        max_length=5,
        blank=False,
        null=False,
    )
    address = models.CharField(
        _("Address"),
        max_length=150,
        blank=False,
        null=False,
    )
    country = models.CharField(
        _("Country"),
        max_length=50,
        blank=False,
        null=False,
        default=_("Spain"),
    )
    person_responsible = models.ForeignKey(
        "users.User",
        verbose_name=_("person responsible"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="person_responsible",
    )
    entity_type = models.CharField(
        choices=EntityTypesChoices,
        null=False,
        blank=False,
        default=EntityTypesChoices.GENERAL,
        verbose_name=_("Entity type"),
        max_length=20,
    )
    reservation_privilege = models.BooleanField(
        _("Reservation privilege"),
        null=False,
        default=False,
        help_text=_("Allows reservations without date restrictions"),
    )
    logo = models.ImageField(
        _("Logo"),
        blank=True,
        storage=PublicMediaStorage(),
        validators=[validate_image_file_extension],
        help_text=_("Logo of the entity"),
    )

    def __str__(self):
        return f"{self.fiscal_name}"

    class Meta:
        ordering = ["fiscal_name"]
        unique_together = ("id", "person_responsible")
        verbose_name = _("entity")
        verbose_name_plural = _("entities")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.entity_type in [
            EntityTypesChoices.HOSTED,
            EntityTypesChoices.BLOC4,
        ] and not hasattr(self, "entity_privilege"):
            EntityPrivilege.objects.create(entity=self)

    def clean(self, *args, **kwargs):
        super().clean()
        errors = {}
        try:
            user_entity = self.person_responsible.entity
            if self != self.person_responsible.entity:
                errors.update(
                    {
                        "person_responsible": ValidationError(
                            _(
                                "This user belong to {entity}. To be "
                                "person responsible the user must belong to "
                                "the entity first."
                            ).format(entity=user_entity)
                        )
                    },
                )
            raise ValidationError(errors)
        except AttributeError:
            pass


class EntityPrivilege(BaseModel):
    entity = models.OneToOneField(
        Entity, on_delete=models.CASCADE, related_name="entity_privilege"
    )
    monthly_hours_meeting = models.DecimalField(
        _("Free monthly hours for meeting rooms"),
        max_digits=5,
        decimal_places=2,
        default=10,
    )
    anual_hours_class = models.DecimalField(
        _("Free annual hours for classrooms"),
        max_digits=5,
        decimal_places=2,
        default=100,
    )
    class_reservation_privilege = models.BooleanField(
        _("Classroom privilege"),
        help_text=_("Classrooms can be reserved without prior authorization"),
        default=False,
    )

    def __str__(self):
        return _("Entity privilege for %(name)s") % {"name": self.entity.fiscal_name}


class MonthlyBonus(BaseModel):
    entity = models.ForeignKey(
        Entity,
        verbose_name=_("Entity monthly bonus"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="monthly_bonus",
    )
    date = models.DateField(_("Date"))
    amount = models.FloatField(_("Amount"))

    class Meta:
        ordering = ["entity", "date"]
        verbose_name = _("Monthly bonus")
        verbose_name_plural = _("Monthly bonuses")

    def __str__(self):
        return _("Monthly bonus for %(entity)s in %(date)s") % {
            "date": self.date.strftime("%B %Y"),
            "entity": self.entity.fiscal_name,
        }

    @property
    def month_and_year(self):
        return self.date.strftime("%B %Y")

    def clean(self, *args, **kwargs):
        super().clean()
        existing_objects = MonthlyBonus.objects.filter(
            entity=self.entity, date__year=self.date.year, date__month=self.date.month
        ).exclude(pk=self.pk)
        if existing_objects.exists():
            raise ValidationError(
                {
                    "date": ValidationError(
                        _(
                            f"A record for {self.entity} "
                            f"for {self.month_and_year} already exists."
                        )
                    )
                },
            )
