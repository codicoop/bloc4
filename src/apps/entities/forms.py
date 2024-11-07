from django import forms

from apps.entities.choices import EntityTypesChoices
from apps.entities.models import Entity


class EntitySignUpForm(forms.ModelForm):
    class Meta:
        model = Entity
        fields = (
            "fiscal_name",
            "nif",
            "email",
            "town",
            "postal_code",
            "address",
            "country",
            "entity_type",
            "logo",
        )

    def __init__(self, *args, **kwargs):
        super(EntitySignUpForm, self).__init__(*args, **kwargs)
        self.fields["entity_type"].choices = [
            choice
            for choice in EntityTypesChoices.choices
            if choice[0] in ["general", "outside"]
        ]
