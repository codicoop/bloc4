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
                "class": "form-control",
                "required": True,
                "help_text": _("Date"),
            }
        )
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                "class": "form-control",
                "required": True,
                "help_text": _("Start time"),
                "placeholder": "00:00",
            }
        )
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                "class": "form-control",
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
                "class": "form-control",
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
