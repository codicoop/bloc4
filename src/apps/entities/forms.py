from django import forms
from django.utils.translation import gettext_lazy as _

from apps.entities.models import Entity
from project.fields.flowbite import (
    FormCharField,
    FormEmailField,
    FormIntegerField,
    FormBooleanField,
)


class EntityForm(forms.ModelForm):
    email = FormEmailField(label=_("Email"), disabled=True)
    fiscal_name = FormCharField(label=_("Fiscal name"), disabled=True)
    nif = FormCharField(label=_("NIF"), disabled=True)
    town = FormCharField(label=_("Towm"), disabled=True)
    postal_code = FormIntegerField(label=_("Postal code"), disabled=True)
    address = FormCharField(label=_("Address"), disabled=True)
    country = FormCharField(label=_("Country"), disabled=True)
    person_responsible = FormCharField(label=_("Person responsible"), disabled=True)
    is_resident = FormBooleanField(label=_("Resident"), disabled=True)

    class Meta:
        model = Entity
        fields = "__all__"
        exclude = ["created_by"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.initial.update({"town": self.instance.town.name})
            self.initial.update(
                {"person_responsible": self.instance.person_responsible.full_name}
            )
