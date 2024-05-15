from django import forms

from apps.entities.models import Entity


class EntityForm(forms.ModelForm):
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
