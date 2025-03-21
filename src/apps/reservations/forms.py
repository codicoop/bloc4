from django import forms
from django.conf import settings
from django.core.validators import ValidationError
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from extra_settings.models import Setting
from flowbite_classes.widgets import FlowBiteDateInput, FlowBiteTimeInput

from apps.reservations.models import Reservation
from apps.reservations.services import calculate_discount_price
from apps.rooms.choices import RoomTypeChoices
from apps.rooms.models import Room

from . import constants
from .widgets.custom_numeric import CustomNumericInput
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
                    "min": constants.START_TIME.strftime("%H:%M"),
                    "max": constants.END_TIME_MINUS_ONE.strftime("%H:%M"),
                    "hx-target": "#total_price",
                    "hx-trigger": "change",
                }
            ),
            "end_time": FlowBiteTimeInput(
                attrs={
                    "type": "time",
                    "step": 900,
                    "min": constants.START_TIME_PLUS_ONE.strftime("%H:%M"),
                    "max": constants.END_TIME.strftime("%H:%M"),
                    "hx-target": "#total_price",
                    "hx-trigger": "change",
                }
            ),
            "assistants": CustomNumericInput(),
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
        request = kwargs.pop("request", None)
        super(ReservationForm, self).__init__(*args, **kwargs)
        calculate_price_url = reverse("reservations:calculate_total_price")
        self.fields["start_time"].widget.attrs.update({"hx-post": calculate_price_url})
        self.fields["end_time"].widget.attrs.update({"hx-post": calculate_price_url})
        if request:
            id = request.GET.get("id")
            room = Room.objects.get(id=id)
            if room.room_type == RoomTypeChoices.MEETING_ROOM:
                self.fields.pop("privacy", None)
                self.fields.pop("description", None)
                self.fields.pop("url", None)
                self.fields.pop("poster", None)
            self.fields["assistants"].widget.attrs.update(
                {"min": "1", "max": str(room.capacity)}
            )
            if id == Setting.get("CATERING_ROOM"):
                self.fields.pop("catering", None)
            if Setting.get("TERMS_USE"):
                self.fields["terms_use"].label = mark_safe(
                    _(
                        'I have read and agree with the <a href="{url}" '
                        'target="_blank" style="color: '
                        '#be3bc7; font-weight: bold;">rules of use of the space</a>'
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
                    request.user.entity.entity_type, room.price
                ),
                "price_half_day": calculate_discount_price(
                    request.user.entity.entity_type,
                    room.price_half_day,
                ),
                "price_all_day": calculate_discount_price(
                    request.user.entity.entity_type,
                    room.price_all_day,
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
            raise ValidationError(errors)
