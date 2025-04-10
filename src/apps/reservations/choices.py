from django.db import models
from django.utils.translation import gettext_lazy as _


class ReservationTypeChoices(models.TextChoices):
    HOURLY = "hourly", _("Hourly reservation")
    MORNING = "morning", _("Morning reservation")
    AFTERNOON = "afternoon", _("Afternoon reservation")
    WHOLE_DAY = "whole_day", _("Whole day reservation")


class ActivityTypeChoices(models.TextChoices):
    NONE = "none", _("None of the two")
    BLOC4 = "bloc4", _("Activity for Bloc4BCN services")
    ATENEU = ("ateneu", _("Activity for the Ateneu Cooperatiu de Barcelona"))


class Bloc4TypeChoices(models.TextChoices):
    TRAINING = "training", _("ESS continuous training")
    ACCOMPANIMENT = "accompaniment", _("Accompaniment")
    FINANCING = "financing", _("Access to financing")
    TECHBLOC4 = "techbloc4", _("TechBloc4-Digitalization")
    ACTS = "acts", _("Acts and events")
    INTERNATIONALIZATION = "internationalization", _("Internationalization")
    ATTENTION_POINT = "attention_point", _("ESS attention point")
    CHALLENGES = "challenges", _("Challenges")
    COMMUNICATION = "communication", _("Communication and disclosure")
    INTERCOOP = "intercooperation", _("Local intercooperation")
    JOVESS = "jovess", _("JovEES")
    GOVERNANCE = "governance", _("Governance Spaces")
    DIAGNOSIS = "diagnosis", _("Diagnosis of ESS")
