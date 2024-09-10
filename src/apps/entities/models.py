from constance import config
from django.core.validators import validate_image_file_extension
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.entities.choices import EntityTypesChoices
from project.fields import flowbite
from project.models import BaseModel
from project.storage_backends import PrivateMediaStorage


class Entity(BaseModel):
    email = flowbite.ModelEmailField(
        max_length=100,
        blank=False,
        null=False,
        unique=True,
        help_text=_("Email address"),
    )
    fiscal_name = flowbite.ModelCharField(
        max_length=50,
        blank=False,
        null=False,
        help_text=_("Fiscal name"),
    )
    nif = flowbite.ModelCharField(
        unique=True,
        max_length=9,
        blank=False,
        null=False,
        verbose_name=_("NIF"),
        help_text=_("Tax identification number"),
    )
    town = models.ForeignKey(
        "provinces_towns.Town",
        verbose_name=_("Town"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="entities",
    )
    postal_code = flowbite.ModelCharField(
        max_length=5,
        blank=False,
        null=False,
        verbose_name=_("Postal Code"),
        help_text=_("Postal Code"),
    )
    address = flowbite.ModelCharField(
        max_length=150,
        blank=False,
        null=False,
        help_text=_("Address"),
    )
    country = flowbite.ModelCharField(
        max_length=50,
        blank=False,
        null=False,
        default=_("Spain"),
        help_text=_("Country"),
    )
    person_responsible = models.ForeignKey(
        "users.User",
        verbose_name=_("person responsible"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="person_responsible",
    )
    entity_type = flowbite.ModelSelectDropdownField(
        choices=EntityTypesChoices,
        null=False,
        blank=False,
        default=EntityTypesChoices.GENERAL,
        verbose_name=_("Entity type"),
        max_length=20,
    )
    reservation_privilege = flowbite.ModelBooleanField(
        _("Reservation privilege"),
        null=False,
        default=False,
        help_text=_(
            f"Allows reservations more than {config.MAXIMUM_ADVANCE_RESERVATION_DAYS} "
            "days in advance"
        ),
    )
    logo = flowbite.ModelImageField(
        _("Logo"),
        blank=True,
        null=True,
        storage=PrivateMediaStorage(),
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
