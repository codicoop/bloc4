from django.db import models
from django.utils.translation import gettext_lazy as _

from project.fields import flowbite


class Data(models.Model):
    class RadioChoices(models.TextChoices):
        OPTION_1 = "OP1", _("Option 1")
        OPTION_2 = "OP2", _("Option 2")
        OPTION_3 = "OP3", _("Option 3")

    class SelectChoices(models.TextChoices):
        OPTION_1 = "OP1", _("Option 1")
        OPTION_2 = "OP2", _("Option 2")
        OPTION_3 = "OP3", _("Option 3")

    class SelectCheckboxChoices(models.TextChoices):
        OPTION_1 = "OP1", _("Option 1")
        OPTION_2 = "OP2", _("Option 2")
        OPTION_3 = "OP3", _("Option 3")

    field_text_1 = flowbite.ModelCharField(
        max_length=50,
        blank=False,
        null=False,
        help_text="Help field_text_1",
    )
    field_text_2 = flowbite.ModelCharField(
        max_length=100,
        blank=False,
        null=False,
        help_text="Help field_text_2",
    )
    field_email = flowbite.ModelEmailField(
        max_length=100,
        blank=False,
        null=False,
        unique=True,
        help_text="Help field_email",
    )
    field_radio = flowbite.ModelRadioField(
        max_length=4,
        choices=RadioChoices.choices,
        blank=False,
        null=False,
        help_text="Help field_radio",
    )
    field_boolean_checkbox = flowbite.ModelBooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="Help field_boolean_checkbox",
    )
    field_select_dropdown = flowbite.ModelSelectDropdownField(
        max_length=4,
        choices=SelectChoices.choices,
        default=SelectChoices.OPTION_1,
        blank=False,
        null=False,
        help_text="Help field_select_dropdown",
    )
    field_password = flowbite.ModelPasswordField(
        max_length=50,
        blank=False,
        null=False,
        help_text="Help field_password",
    )
    field_password_confirm = flowbite.ModelPasswordField(
        max_length=50,
        blank=False,
        null=False,
        help_text="Help field_password_confirm",
    )
    field_number = flowbite.ModelIntegerField(
        blank=True,
        null=True,
        help_text="Help field_number",
    )
    field_select_checkbox = flowbite.ModelSelectCheckboxField(
        max_length=250,
        default=SelectCheckboxChoices.OPTION_1,
        blank=True,
        null=True,
        help_text="Help field_select_checkbox",
    )

    def __str__(self):
        return f"{self.field_text_1}"
