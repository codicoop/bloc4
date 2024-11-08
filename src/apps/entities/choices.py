from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.reservations.constants import (
    BLOC4_DISCOUNT,
    GENERAL_DISCOUNT,
    HOSTED_DISCOUNT,
    OUTSIDE_DISCOUNT,
)


class EntityTypesChoices(models.TextChoices):
    GENERAL = "general", _("General entity")
    HOSTED = "hosted", _("Hosted entity")
    BLOC4 = "bloc4", _("Bloc4 entity")
    OUTSIDE = "outside", _("Entity outside the ESS and public sector")

    def get_discount_percentage(self):
        discounts = {
            self.GENERAL: GENERAL_DISCOUNT,
            self.HOSTED: HOSTED_DISCOUNT,
            self.BLOC4: BLOC4_DISCOUNT,
            self.OUTSIDE: OUTSIDE_DISCOUNT,
        }
        return discounts.get(self, 0)
