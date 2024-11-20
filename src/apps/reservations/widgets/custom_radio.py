from django.forms.widgets import RadioSelect


class CustomRadioSelect(RadioSelect):
    template_name = "reservations/widgets/custom_radio.html"

    def __init__(self, attrs=None):
        default_attrs = {"label": "Custom Radio", "help_text": "Choose an option."}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
