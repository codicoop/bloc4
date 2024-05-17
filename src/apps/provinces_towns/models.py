from django.db import models
from django.utils.translation import gettext_lazy as _


class AutonomousCommunityChoices(models.IntegerChoices):
    ANDALUCIA = 1, _("Andalucia")
    ZARAGOZA = 2, _("Zaragoza")
    ASTURIAS = 3, _("Asturias")
    BALEARS = 4, _("Illes Balears")
    TENERIFE = 5, _("Santa Cruz de Tenerife")
    CANTABRIA = 6, _("Cantàbria")
    CASTILLA_LEON = 7, _("Castilla y León")
    CASTILLA_MANCHA = 8, _("Castilla - La Mancha")
    CATALUNYA = 9, _("Catalunya")
    VALENCIA = 10, _("País Valencià")
    EXTREMADURA = 11, _("Extremadura")
    GALICIA = 12, _("Galícia")
    MADRID = 13, _("Madrid")
    MURCIA = 14, _("Múrcia")
    NAVARRA = 15, _("Navarra")
    EUSKADI = 16, _("Euskal Herria")
    RIOJA = 17, _("La Rioja")
    CEUTA = 18, _("Ceuta")
    MELILLA = 19, _("Melilla")


class Province(models.Model):
    class Meta:
        verbose_name = "província"
        verbose_name_plural = "provincies"

    autonomous_community = models.SmallIntegerField(
        _("Autonomous Community"),
        choices=AutonomousCommunityChoices.choices,
    )
    name = models.CharField(
        _("Name"),
        blank=False,
        null=False,
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.name


class County(models.Model):
    class Meta:
        verbose_name = "comarca"
        verbose_name_plural = "comarques"

    province = models.ForeignKey(
        Province,
        verbose_name=_("Province"),
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name="counties",
    )
    name = models.CharField(
        _("Name"),
        blank=False,
        null=False,
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.name


class Town(models.Model):
    class Meta:
        verbose_name = "població"
        verbose_name_plural = "poblacions"
        ordering = [
            "name",
        ]

    county = models.ForeignKey(
        County,
        verbose_name=_("County"),
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        related_name="counties",
    )
    name = models.CharField(
        _("Name"),
        blank=False,
        null=False,
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.name
