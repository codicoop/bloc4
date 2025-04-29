import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SetBooleanDatetimeMixin:
    def set_boolean_datetime(self, field, auth):
        """
        For fields that we store as Datetime but are presented as checkboxes
        to the user. So they check it to (i.e.) authorize receiving the
        newsletter but instead of a boolean we store the date when the
        authorization was given.
        """
        if auth is True:
            setattr(self, field, timezone.now())
            self.save()


class BaseModel(SetBooleanDatetimeMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(
        _("created_at"),
        auto_now_add=True,
        null=False,
        editable=False,
    )
    created_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_related",
        on_delete=models.SET_NULL,
        verbose_name=_("created by"),
    )
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True,
        null=False,
        editable=False,
    )

    class Meta:
        abstract = True


# class Setting(BaseSetting):
#     """
#     This version catches the AppRegistryNotReady exception to make it possible
#     for the extra-settings to load the settings or default value when you
#     use it in a place that is loaded during the initialization, i.e., a
#     `help_text` argument of a model's field.
#     """

#     @staticmethod
#     def _get_from_database(name):
#         try:
#             setting_obj = Setting.objects.get(name=name)
#             value = setting_obj.value
#             set_cached_setting(name, value)
#             return value
#         except (AppRegistryNotReady, Setting.DoesNotExist):
#             return None
