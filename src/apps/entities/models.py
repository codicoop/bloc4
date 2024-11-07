from django.core.validators import validate_image_file_extension
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.entities.choices import EntityTypesChoices
from project.models import BaseModel
from project.storage_backends import PublicMediaStorage


class Entity(BaseModel):
    email = models.EmailField(
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
    town = flowbite.ModelCharField(
        _("Town"),
        null=True,
        blank=True,
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
        null=True,
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
