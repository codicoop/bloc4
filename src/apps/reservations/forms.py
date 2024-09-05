from django import forms
from django.utils.translation import gettext_lazy as _

from apps.reservations.models import Reservation
from apps.rooms.models import Room
from project.fields import flowbite


class ReservationForm(forms.ModelForm):
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        widget=forms.HiddenInput(),
    )
    total_price = flowbite.FormFloatField(
        widget=forms.HiddenInput(),
        required=False,
    )
    title = flowbite.FormCharField(
        label=_("Title"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autofocus": True,
                "autocomplete": True,
                "help_text": _("Title"),
            }
        ),
    )
    date = flowbite.FormDateField(
        label=_("Date"),
        widget=forms.DateInput(
            format="%Y-%m-%d",
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
            },
        ),
        input_formats=["%Y-%m-%d"],
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
        ),
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
        ),
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
        ),
    )
    notes = flowbite.FormCharField(
        label=_("Notes"),
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "autofocus": True,
                "autocomplete": True,
                "help_text": _("Notes"),
            }
        ),
    )
    privacy = forms.ChoiceField(
        label=_("Privacy"),
        choices=Reservation.PrivacyChoices,
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
                "help_text": _(
                    "If the training is public, it will appear in the bloc4 agenda"
                ),
            }
        ),
    )
    description = flowbite.FormCharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "autofocus": True,
                "autocomplete": True,
                "help_text": _("Description"),
            }
        ),
    )
    poster = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "autofocus": True,
                "autocomplete": True,
                "help_text": _("Description"),
            }
        ),
    )

    class Meta:
        model = Reservation
        fields = [
            "room",
            "total_price",
            "title",
            "date",
            "start_time",
            "end_time",
            "assistants",
            "catering",
            "notes",
            "bloc4_reservation",
            "privacy",
            "description",
            "poster",
            "url",
        ]
