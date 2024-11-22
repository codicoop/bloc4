from django.forms.widgets import RadioSelect

from apps.reservations.choices import ReservationTypeChoices


class CustomRadioSelect(RadioSelect):
    template_name = "reservations/widgets/custom_radio.html"

    def __init__(self, prices=None):
        self.prices = prices if prices else {}
        super().__init__()

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["choices"] = ReservationTypeChoices
        context["prices"] = self.prices
        return context
