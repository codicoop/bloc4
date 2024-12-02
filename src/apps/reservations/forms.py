from django import forms
from django.conf import settings
from django.core.validators import ValidationError
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from extra_settings.models import Setting

from apps.reservations.models import Reservation
from apps.reservations.services import calculate_discount_price
from apps.rooms.choices import RoomTypeChoices
from apps.rooms.models import Room

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
            "date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": "text-sm border rounded-lg block w-full "
                    "p-2.5 bg-gray-50 "
                    "border-gray-300 text-gray-900 focus:ring-primary-600 "
                    "focus:border-primary-60 dark:bg-gray-700 "
                    "dark:border-gray-600 dark:placeholder-gray-400 "
                    "dark:text-white dark:focus:ring-primary-500 "
                    "dark:focus:border-primary-500",
                },
            ),
            "start_time": forms.TimeInput(
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
                    "hx-target": "#total_price",
                    "hx-trigger": "change",
                }
            ),
            "end_time": forms.TimeInput(
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
                }
            ),
            "description": forms.Textarea(),
            "poster": forms.FileInput(
                attrs={
                    "class": "text-sm border rounded-lg "
                    "block w-full px-2.5 bg-gray-50 border-gray-300 "
                    "text-gray-900 focus:ring-primary-600 "
                    "focus:border-primary-600 dark:bg-gray-700 "
                    "dark:border-gray-600 dark:placeholder-gray-400 "
                    "dark:text-white dark:focus:ring-primary-500"
                    "dark:focus:border-primary-500",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        prices = kwargs.pop("prices", {})
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
                        'I agree the <a href="{url}" target="_blank" style="color: '
                        '#be3bc7; font-weight: bold;">Terms of Use</a>'
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
