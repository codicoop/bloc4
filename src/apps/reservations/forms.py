from django import forms
from django.utils.translation import gettext_lazy as _

from apps.entities.models import Entity
from apps.reservations.models import Reservation
from apps.rooms.choices import RoomTypeChoices
from apps.rooms.models import Room
from project.fields import flowbite


class ReservationForm(forms.ModelForm):
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        widget=forms.HiddenInput(),
    )
    entity = forms.ModelChoiceField(
        queryset=Entity.objects.all(), widget=forms.HiddenInput(), required=False
    )
    title = flowbite.FormCharField(
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
                "autofocus": True,
                "autocomplete": "on",
            }
        ),
    )
    date = flowbite.FormDateField(
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
                "disabled:bg-gray-200 "
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
                "disabled:bg-gray-200 "
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
    assistants = flowbite.FormIntegerField(
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
    catering = flowbite.FormBooleanField(
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
    catering = flowbite.FormBooleanField(
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
    notes = flowbite.FormCharField(
        label=_("Notes"),
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
    bloc4_reservation = flowbite.FormBooleanField(
        label=_("Reservation for Bloc4 services"),
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
                "autocomplete": True,
                "help_text": _(
                    "If the training is public, it will appear in the bloc4 agenda"
                ),
                "_": "on change "
                "if my.value is 'public' "
                "remove .hidden from #id_description "
                "then remone .hidden from #id_url "
                "then remone .hidden from #id_poster "
                "else "
                "add .hidden to #id_description "
                "then add .hidden to #id_url "
                "then add .hidden to #id_poster ",
            }
        ),
    )
    description = flowbite.FormCharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control text-sm border rounded-lg block hidden "
                "w-full p-2.5 "
                "bg-gray-50 border-gray-300 text-gray-900 "
                "focus:ring-primary-600 focus:border-primary-600 "
                "dark:bg-gray-700 dark:border-gray-600 "
                "dark:placeholder-gray-400 dark:text-white"
                "dark:focus:ring-primary-500 dark:focus:border-primary-500",
                "autofocus": True,
                "autocomplete": True,
                "cols": "40",
                "rows": "10",
                "help_text": _(
                    "This field will be used for the public add of the event."
                ),
            }
        ),
    )
    url = flowbite.FormUrlField(
        label=_("URL of the activity"),
        required=False,
        widget=forms.URLInput(
            attrs={
                "class": "text-sm border rounded-lg block hidden w-full p-2.5 bg-gray-50 "
                "border-gray-300 text-gray-900 focus:ring-primary-600 "
                "focus:border-primary-60 dark:bg-gray-700 "
                "dark:border-gray-600 dark:placeholder-gray-400 "
                "dark:text-white dark:focus:ring-primary-500 "
                "dark:focus:border-primary-500",
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
                "class": "form-control hidden",
                "autofocus": True,
                "autocomplete": True,
                "help_text": _(
                    "This field will be used for the public add of the event."
                ),
            }
        ),
    )

    class Meta:
        model = Reservation
        fields = [
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
        ]

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super(ReservationForm, self).__init__(*args, **kwargs)
        id = request.GET.get("id")
        room = Room.objects.get(id=id)
        if room.room_type == RoomTypeChoices.MEETING_ROOM:
            self.fields.pop("privacy", None)
            self.fields.pop("description", None)
            self.fields.pop("url", None)
            self.fields.pop("poster", None)

    # fieldsets = [
    #     (
    #         None,
    #         {
    #             "fields": (
    #                 "room",
    #                 "entity",
    #                 "title",
    #                 "date",
    #                 "start_time",
    #                 "end_time",
    #                 "assistants",
    #                 "catering",
    #                 "notes",
    #                 "bloc4_reservation",
    #                 "privacy",
    #             )
    #         },
    #     ),
    #     (
    #         None,
    #         {
    #             "fields": (
    #                 "description",
    #                 "url",
    #                 "poster",
    #             )
    #         },
    #     ),
    # ]

    # def as_fieldsets(self):
    #     output = []
    #     for name, fieldset in self.fieldsets:
    #         output.append("<fieldset>")
    #         if name:
    #             output.append(f"<legend>{name}</legend>")
    #         for field_name in fieldset["fields"]:
    #             field = self[field_name]
    #             if isinstance(field.field.widget, forms.HiddenInput):
    #                 output.append(f"{field}")
    #             else:
    #                 output.append(f"<p>{field.label_tag()}{field}</p>")
    #             if field.errors:
    #                 for error in field.errors:
    #                     output.append(f'<p class="error">{error}</p>')
    #             if field.help_text:
    #                 output.append(f'<p class="help">{field.help_text}</p>')
    #         output.append("</fieldset>")
    #     return "".join(output)
