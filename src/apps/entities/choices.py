from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.reservations import constants


class EntityTypesChoices(models.TextChoices):
    HOSTED = "hosted", _("Hosted entity")
    BLOC4 = "bloc4", _("Bloc4 entity")
    GENERAL = "general", _("Public sector and social economy entities")
    FEDERATED = "federated", _("Coòpolis and federated cooperatives")
    OUTSIDE = "outside", _("Other entities")

    def get_discount_percentage(self):
        discounts = {
            self.HOSTED: constants.HOSTED_DISCOUNT,
            self.BLOC4: constants.BLOC4_DISCOUNT,
            self.GENERAL: constants.GENERAL_DISCOUNT,
            self.FEDERATED: constants.FEDERATED_DISCOUNT,
            self.OUTSIDE: constants.OUTSIDE_DISCOUNT,
        }
        return discounts.get(self, 0)
