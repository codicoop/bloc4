from django import forms
from django.utils.translation import gettext_lazy as _

from apps.reservations.models import Reservation
from apps.rooms.models import Room
from project.fields import flowbite


class ReservationForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
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
        )
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                "type": "time",
                "class": "text-sm border rounded-lg block w-full p-2.5 bg-gray-50 "
                        "border-gray-300 text-gray-900 focus:ring-primary-600 "
                        "focus:border-primary-60 dark:bg-gray-700 "
                        "dark:border-gray-600 dark:placeholder-gray-400 "
                        "dark:text-white dark:focus:ring-primary-500 "
                        "dark:focus:border-primary-500",
                "required": True,
                "help_text": _("Start time"),
                "placeholder": "00:00",
            }
        )
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                "type": "time",
                "class": "text-sm border rounded-lg block w-full p-2.5 bg-gray-50 "
                        "border-gray-300 text-gray-900 focus:ring-primary-600 "
                        "focus:border-primary-60 dark:bg-gray-700 "
                        "dark:border-gray-600 dark:placeholder-gray-400 "
                        "dark:text-white dark:focus:ring-primary-500 "
                        "dark:focus:border-primary-500",
                "required": True,
                "help_text": _("End time"),
                "placeholder": "00:00",
            }
        )
    )
    motivation = flowbite.FormCharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "autofocus": True,
                "autocomplete": True,
                "help_text": _("Motivation"),
                "placeholder": _("Motivation"),
            }
        )
    )
    assistants = flowbite.FormCharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "autofocus": True,
                "autocomplete": True,
                "help_text": _("Assistants"),
                "placeholder": _("Assistants"),
            }
        )
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "text-sm border rounded-lg block w-full p-2.5 bg-gray-50 "
                         "border-gray-300 text-gray-900 focus:ring-primary-500 "
                         "focus:border-primary-500 dark:bg-gray-700 "
                         "dark:border-gray-600 dark:placeholder-gray-400 "
                         "dark:text-white dark:focus:ring-primary-500 "
                         "dark:focus:border-primary-500",
                "autofocus": True,
                "autocomplete": True,
                "help_text": _("Room"),
                "placeholder": _("Room"),
                "required": True,
            }
        ),
    )

    class Meta:
        model = Reservation
        fields = [
            "room",
            "date",
            "start_time",
            "end_time",
            "motivation",
            "assistants",
        ]
