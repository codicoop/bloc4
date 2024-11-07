from django import forms

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
            # "entity_type"
        )
