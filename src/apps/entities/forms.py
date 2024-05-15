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
    email = FormEmailField(label=_("Email"))
    fiscal_name = FormCharField(label=_("Fiscal name"))
    nif = FormCharField(label=_("NIF"))
    town = FormCharField(label=_("Towm"))
    postal_code = FormIntegerField(label=_("Postal code"))
    address = FormCharField(label=_("Address"))
    country = FormCharField(label=_("Country"))
    person_responsible = FormCharField(label=_("Person responsible"))
    is_resident = FormBooleanField(label=_("Resident"))

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
