from django.db import models
from django.utils.translation import gettext_lazy as _


class EntityTypesChoices(models.TextChoices):
    GENERAL = "general", _("General entity")
    HOSTED = "hosted", _("Hosted entity")
    BLOC4 = "bloc4", _("Bloc4 entity")
    OUTSIDE = "outside", _("Entity outside the ESS and public sector")

    def get_discount_percentage(self):
        discounts = {
            self.GENERAL: 0,
            self.HOSTED: -0.4,
            self.BLOC4: -0.5,
            self.OUTSIDE: 0.15,
        }
        return discounts.get(self, 0)
