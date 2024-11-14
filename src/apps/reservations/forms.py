from django import forms
from django.core.validators import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.entities.models import Entity
from apps.reservations.choices import ReservationTypeChoices
from apps.reservations.models import Reservation
from apps.rooms.choices import RoomTypeChoices
from apps.rooms.models import Room


class ReservationForm(forms.ModelForm):
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        widget=forms.HiddenInput(),
    )
    entity = forms.ModelChoiceField(
        queryset=Entity.objects.all(), widget=forms.HiddenInput(), required=False
    )
    reservation_type = forms.ChoiceField(
        label=_("Reservation Type"),
        choices=ReservationTypeChoices,
        required=True,
        widget=forms.RadioSelect(),
        initial=ReservationTypeChoices.HOURLY,
    )
    title = forms.CharField(
        label=_("Title"),
        widget=forms.TextInput(
            attrs={
                "class": "text-sm border rounded-lg "
                "block w-full p-2.5 bg-gray-50 border-gray-300 "
                "text-gray-900 focus:ring-primary-600 "
                "focus:border-primary-600 dark:bg-gray-700 "
                "dark:border-gray-600 dark:placeholder-gray-400 "
                "dark:text-white dark:focus:ring-primary-500"
                "dark:focus:border-primary-500",
                "autocomplete": "on",
            }
        ),
    )
    date = forms.DateField(
        label=_("Date"),
        widget=forms.DateInput(
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
                "required": True,
                "help_text": _("Date"),
            },
        ),
        input_formats=["%Y-%m-%d"],
    )
    start_time = forms.TimeField(
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
                "hx-target": "#total_price",
                "hx-trigger": "change",
            }
        ),
    )
    end_time = forms.TimeField(
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
                "hx-target": "#total_price",
                "hx-trigger": "change",
            }
        ),
    )
    assistants = forms.IntegerField(
        label=_("Assitants"),
        widget=forms.NumberInput(
            attrs={
                "data-input-counter": "",
                "aria-describedby": "helper-text-explanation",
                "class": "bg-gray-50 border-x-0 border-gray-300 rounded-none"
                "h-11 text-center text-gray-900 text-sm block w-full py-2.5 "
                "focus:ring-primary-500 focus:border-primary-500 "
                "dark:bg-gray-700 dark:border-gray-600 "
                "dark:placeholder-gray-400 dark:text-white "
                "dark:focus:ring-primary-500 dark:focus:border-primary-500",
                "autocomplete": True,
                "required": "",
            }
        ),
    )
    catering = forms.BooleanField(
        label=_("Do I need catering service?"),
        widget=forms.CheckboxInput(
            attrs={
                "class": "ms-2 text-sm font-medium text-gray-900 "
                "dark:text-gray-300 w-4 h-4 border rounded text-primary-500 "
                "border-gray-300 bg-gray-50 focus:ring-3 "
                "focus:ring-primary-300 "
                "dark:bg-gray-700 dark:border-gray-600 ",
                "help_text": _("Bloc4 reservation"),
            }
        ),
    )
    catering = forms.BooleanField(
        label=_("Do I need catering service?"),
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "ms-2 text-sm font-medium text-gray-900 "
                "dark:text-gray-300 w-4 h-4 border rounded text-primary-500 "
                "border-gray-300 bg-gray-50 focus:ring-3 "
                "focus:ring-primary-300 "
                "dark:bg-gray-700 dark:border-gray-600 ",
                "help_text": _("Bloc4 reservation"),
            }
        ),
    )
    notes = forms.CharField(
        label=_("Do you need to tell us something?"),
        widget=forms.Textarea(
            attrs={
                "class": "text-sm border rounded-lg block w-full p-2.5 bg-gray-50 "
                "border-gray-300 text-gray-900 focus:ring-primary-600 "
                "focus:border-primary-60 dark:bg-gray-700 "
                "dark:border-gray-600 dark:placeholder-gray-400 "
                "dark:text-white dark:focus:ring-primary-500 "
                "dark:focus:border-primary-500",
                "autocomplete": True,
                "help_text": _("Notes"),
            }
        ),
    )
    bloc4_reservation = forms.BooleanField(
        label=_("Reservation for Bloc4BCN services"),
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "ms-2 text-sm font-medium text-gray-900 "
                "dark:text-gray-300 w-4 h-4 border rounded text-primary-500 "
                "border-gray-300 bg-gray-50 focus:ring-3 "
                "focus:ring-primary-300 "
                "dark:bg-gray-700 dark:border-gray-600 ",
                "help_text": _("Bloc4BCN reservation"),
            }
        ),
    )
    privacy = forms.ChoiceField(
        label=_("Type of event"),
        choices=Reservation.PrivacyChoices,
        required=False,
        help_text=_(
            "Public events must be open to all citizens and will "
            "be published in the Bloc4BCN Agenda, subject to approval."
        ),
        widget=forms.Select(
            attrs={
                "class": "text-sm border rounded-lg block w-full p-2.5 bg-gray-50 "
                "border-gray-300 text-gray-900 focus:ring-primary-500 "
                "focus:border-primary-500 dark:bg-gray-700 "
                "dark:border-gray-600 dark:placeholder-gray-400 "
                "dark:text-white dark:focus:ring-primary-500 "
                "dark:focus:border-primary-500",
                "autocomplete": True,
                "help_text": _(
                    "If the training is public, it will appear in the Bloc4BCN agenda"
                ),
                "_": "init if my.value is 'public' "
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
    )
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control text-sm border rounded-lg block "
                "w-full p-2.5 "
                "bg-gray-50 border-gray-300 text-gray-900 "
                "focus:ring-primary-600 focus:border-primary-600 "
                "dark:bg-gray-700 dark:border-gray-600 "
                "dark:placeholder-gray-400 dark:text-white"
                "dark:focus:ring-primary-500 dark:focus:border-primary-500",
                "autocomplete": True,
                "cols": "40",
                "rows": "10",
                "help_text": _(
                    "This field will be used for the public add of the event."
                ),
            }
        ),
    )
    url = forms.URLField(
        label=_("URL of the activity"),
        required=False,
        widget=forms.URLInput(
            attrs={
                "help_text": _(
                    "This field will be used for the public add of the event."
                ),
            }
        ),
    )
    poster = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "text-sm border rounded-lg "
                "block w-full px-2.5 bg-gray-50 border-gray-300 "
                "text-gray-900 focus:ring-primary-600 "
                "focus:border-primary-600 dark:bg-gray-700 "
                "dark:border-gray-600 dark:placeholder-gray-400 "
                "dark:text-white dark:focus:ring-primary-500"
                "dark:focus:border-primary-500",
                "help_text": _(
                    "This field will be used for the public add of the event."
                ),
            }
        ),
    )

    class Meta:
        model = Reservation
        fields = (
            "reservation_type",
            "room",
            "entity",
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
            "url",
            "poster",
        )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super(ReservationForm, self).__init__(*args, **kwargs)
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
