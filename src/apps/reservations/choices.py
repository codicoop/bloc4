from django.db import models
from django.utils.translation import gettext_lazy as _


class ReservationTypeChoices(models.TextChoices):
    HOURLY = "hourly", _("Hourly reservation")
    MORNING = "morning", _("Morning reservation")
    AFTERNOON = "afternoon", _("Afternoon reservation")
    WHOLE_DAY = "whole_day", _("Whole day reservation")
