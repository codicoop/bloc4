from django import forms
from django.utils.translation import gettext_lazy as _

from apps.reservations.models import Reservation
from apps.rooms.models import Room
from project.fields import flowbite


class ReservationForm(forms.ModelForm):
    date = flowbite.FormDateField(
        label=_("Date"),
        widget=forms.DateInput(format="%Y-%m-%d",
            attrs={
                "type": "date",
                "class": "text-sm border rounded-lg block w-full p-2.5 bg-gray-50 "
                "border-gray-300 text-gray-900 focus:ring-primary-600 "
                "focus:border-primary-60 dark:bg-gray-700 "
                "dark:border-gray-600 dark:placeholder-gray-400 "
                "dark:text-white dark:focus:ring-primary-500 "
                "dark:focus:border-primary-500",
                "required": True,
                "help_text": _("Date"),
            }
        ),
        input_formats=["%Y-%m-%d"]

    )
    start_time = flowbite.FormTimeField(
        label=_("Start Time"),
        widget=forms.TimeInput(
            attrs={
                "type": "time",
                "step": 900,
                "min": "08:00",
                "max": "17:00",
                "class": "text-sm border rounded-lg block w-full p-2.5 bg-gray-50 "
                "border-gray-300 text-gray-900 focus:ring-primary-600 "
                "focus:border-primary-60 dark:bg-gray-700 "
                "dark:border-gray-600 dark:placeholder-gray-400 "
                "dark:text-white dark:focus:ring-primary-500 "
                "dark:focus:border-primary-500",
                "required": True,
                "help_text": _("Start time"),
            }
        )
    )
    end_time = flowbite.FormTimeField(
        label=_("End Time"),
        widget=forms.TimeInput(
            attrs={
                "type": "time",
                "step": 900,
                "min": "09:00",
                "max": "18:00",
                "class": "text-sm border rounded-lg block w-full p-2.5 bg-gray-50 "
                "border-gray-300 text-gray-900 focus:ring-primary-600 "
                "focus:border-primary-60 dark:bg-gray-700 "
                "dark:border-gray-600 dark:placeholder-gray-400 "
                "dark:text-white dark:focus:ring-primary-500 "
                "dark:focus:border-primary-500",
                "required": True,
                "help_text": _("End time"),
            }
        )
    )
    motivation = flowbite.FormCharField(
        label=_("Motivation"),
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "autofocus": True,
                "autocomplete": True,
                "help_text": _("Motivation"),
            }
        )
    )
    assistants = flowbite.FormIntegerField(
        label=_("Assitants"),
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "autofocus": True,
                "autocomplete": True,
                "help_text": _("Assistants"),
            }
        )
    )

    class Meta:
        model = Reservation
        fields = [
            "date",
            "start_time",
            "end_time",
            "motivation",
            "assistants",
        ]
