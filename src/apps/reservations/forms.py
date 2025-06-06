from django import forms
from django.conf import settings
from django.core.validators import ValidationError
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from extra_settings.models import Setting
from flowbite_classes.widgets import (
    FlowBiteDateInput,
    FlowBiteNumericIncrementalInput,
    FlowBiteTimeInput,
)

from apps.reservations.models import Reservation
from apps.reservations.services import calculate_discount_price
from apps.rooms.choices import RoomTypeChoices

from . import constants
from .constants import END_TIME, END_TIME_MINUS_ONE, START_TIME, START_TIME_PLUS_ONE
from .widgets.custom_radio import CustomRadioSelect


class ReservationForm(forms.ModelForm):
    data_policy = forms.BooleanField(
        label=_("I agree to Privacy Policy"),
        required=True,
        widget=forms.CheckboxInput,
    )
    terms_use = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = Reservation
        fields = (
            "room",
            "entity",
            "reservation_type",
            "title",
            "date",
            "start_time",
            "end_time",
            "assistants",
            "catering",
            "notes",
            "activity_type",
            "bloc4_type",
            "privacy",
            "description",
            "url",
            "poster",
            "data_policy",
            "terms_use",
        )
        widgets = {
            "room": forms.HiddenInput(),
            "entity": forms.HiddenInput(),
            "date": FlowBiteDateInput,
            "start_time": FlowBiteTimeInput(
                attrs={
                    "type": "time",
                    "step": 900,
                    "hx-target": "#total_price",
                    "hx-swap": "outerHTML",
                    "hx-trigger": "change",
                }
            ),
            "end_time": FlowBiteTimeInput(
                attrs={
                    "type": "time",
                    "step": 900,
                    "hx-target": "#total_price",
                    "hx-swap": "outerHTML",
                    "hx-trigger": "change",
                }
            ),
            "assistants": FlowBiteNumericIncrementalInput(
                attrs={
                    "data-input-counter-min": 1,
                    "data-input-counter-max": 9999,
                },
            ),
            "catering": forms.CheckboxInput,
            "notes": forms.Textarea(),
            "activity_type": forms.Select(
                attrs={
                    "_": "init if my.value is 'bloc4'"
                    "remove .hidden from #id_bloc4_type.parentElement "
                    "else "
                    "add .hidden to #id_bloc4_type.parentElement "
                    "end "
                    "on change "
                    "if my.value is 'bloc4' "
                    "remove .hidden from #id_bloc4_type.parentElement "
                    "else "
                    "add .hidden to #id_bloc4_type.parentElement ",
                }
            ),
            "privacy": forms.Select(
                attrs={
                    "_": "init if my.value is 'public'"
                    "remove .hidden from #id_description.parentElement "
                    "then remove .hidden from #id_url.parentElement "
                    "then remove .hidden from #id_poster.parentElement "
                    "else "
                    "add .hidden to #id_description.parentElement "
                    "then add .hidden to #id_url.parentElement "
                    "then add .hidden to #id_poster.parentElement "
                    "end "
                    "on change "
                    "if my.value is 'public' "
                    "remove .hidden from #id_description.parentElement "
                    "then remove .hidden from #id_url.parentElement "
                    "then remove .hidden from #id_poster.parentElement "
                    "else "
                    "add .hidden to #id_description.parentElement "
                    "then add .hidden to #id_url.parentElement "
                    "then add .hidden to #id_poster.parentElement ",
                },
            ),
            "description": forms.Textarea(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.room = kwargs.pop("room", None)
        super(ReservationForm, self).__init__(*args, **kwargs)
        calculate_price_url = reverse("reservations:calculate_total_price")
        self.fields["start_time"].widget.attrs.update({"hx-post": calculate_price_url})
        self.fields["end_time"].widget.attrs.update({"hx-post": calculate_price_url})
        if not self.request.user.is_administrator():
            self.fields["start_time"].widget.attrs.update(
                {
                    "min": constants.START_TIME.strftime("%H:%M"),
                    "max": constants.END_TIME_MINUS_ONE.strftime("%H:%M"),
                },
            )
            self.fields["end_time"].widget.attrs.update(
                {
                    "min": constants.START_TIME_PLUS_ONE.strftime("%H:%M"),
                    "max": constants.END_TIME.strftime("%H:%M"),
                },
            )
        if self.room.room_type == RoomTypeChoices.MEETING_ROOM:
            self.fields.pop("privacy", None)
            self.fields.pop("description", None)
            self.fields.pop("url", None)
            self.fields.pop("poster", None)
        self.fields["assistants"].widget.attrs.update(
            {
                "min": "1",
                "max": str(self.room.capacity),
                "data-input-counter-max": str(self.room.capacity),
            }
        )
        if self.room.pk == Setting.get("CATERING_ROOM"):
            self.fields.pop("catering", None)
        if Setting.get("TERMS_USE"):
            self.fields["terms_use"].label = mark_safe(
                _(
                    'I have read and agree with <a href="{url}" '
                    'target="_blank" style="color: '
                    '#be3bc7; font-weight: bold;">the rules of use of the space</a>'
                ).format(
                    url=(
                        f"{settings.AWS_S3_ENDPOINT_URL}/"
                        f"{settings.AWS_STORAGE_BUCKET_NAME}/"
                        f"{settings.AWS_PUBLIC_MEDIA_LOCATION}/"
                        f"{Setting.get('TERMS_USE')}"
                    )
                )
            )
        prices = {
            "price": calculate_discount_price(
                self.request.user.entity.entity_type, self.room.price
            ),
            "price_half_day": calculate_discount_price(
                self.request.user.entity.entity_type,
                self.room.price_half_day,
            ),
            "price_all_day": calculate_discount_price(
                self.request.user.entity.entity_type,
                self.room.price_all_day,
            ),
        }
        self.fields["reservation_type"].widget = CustomRadioSelect(
            prices=prices,
        )
        self.fields["data_policy"].help_text = Setting.get("DATA_POLICY")

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        errors = {}
        if date and date < date.today():
            errors.update(
                {
                    "date": ValidationError(
                        _("The date must be greater than the current date.")
                    )
                },
            )
        # April 2025, now admins should be able to make reservations outside
        # the time span.
        if not self.request.user.is_administrator() and not (
            START_TIME <= cleaned_data.get("start_time") <= END_TIME_MINUS_ONE
        ):
            errors.update(
                {
                    "start_time": ValidationError(
                        _(
                            "The start time must be between "
                            "{start_time} and {end_time}."
                        ).format(
                            start_time=START_TIME.strftime("%H:%M"),
                            end_time=END_TIME_MINUS_ONE.strftime("%H:%M"),
                        )
                    )
                },
            )
        if not self.request.user.is_administrator() and not (
            START_TIME_PLUS_ONE <= cleaned_data.get("end_time") <= END_TIME
        ):
            errors.update(
                {
                    "end_time": ValidationError(
                        _(
                            "The end time must be between "
                            "{start_time} and {end_time}."
                        ).format(
                            start_time=START_TIME_PLUS_ONE.strftime("%H:%M"),
                            end_time=END_TIME.strftime("%H:%M"),
                        )
                    )
                },
            )
        if errors:
            raise ValidationError(errors)
