from django.forms.widgets import TextInput


class CustomNumericInput(TextInput):
    template_name = "reservations/widgets/custom_numeric.html"
