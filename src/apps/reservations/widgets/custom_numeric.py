from django.forms.widgets import TextInput


class CustomNumericInput(TextInput):
    template_name = "reservations/widgets/custom_numeric.html"

    def __init__(self, attrs=None):
        attrs = attrs or {}
        if attrs is None:
            attrs = {}
        attrs.update({"data-input-counter": "",})
        super().__init__(attrs)
