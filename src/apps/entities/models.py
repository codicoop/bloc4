from django.db import models
from django.utils.translation import gettext_lazy as _

from project.models import BaseModel
from project.fields import flowbite


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
    postal_code = flowbite.ModelIntegerField(
        blank=False,
        null=False,
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
    is_resident = flowbite.ModelBooleanField(
        blank=False,
        null=False,
        default=False,
        help_text=_("The entity has permanent premises in Bloc4"),
    )

    def __str__(self):
        return f"{self.fiscal_name}"

    class Meta:
        ordering = ["fiscal_name"]
        unique_together = ("id", "person_responsible")
        verbose_name = _("entity")
        verbose_name_plural = _("entities")
