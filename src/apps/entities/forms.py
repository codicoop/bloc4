from django import forms

from apps.entities.choices import EntityTypesChoices
from apps.entities.models import Entity


class EntitySignUpForm(forms.ModelForm):
    class Meta:
        model = Entity
        fields = (
            "fiscal_name",
            "nif",
            "entity_email",
            "town",
            "postal_code",
            "address",
            "country",
            "entity_type",
            "logo",
        )
        widgets = {
            "logo": forms.FileInput(
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
        super(EntitySignUpForm, self).__init__(*args, **kwargs)
        self.fields["entity_type"].choices = [
            choice
            for choice in EntityTypesChoices.choices
            if choice[0] in ["general", "outside"]
        ]
