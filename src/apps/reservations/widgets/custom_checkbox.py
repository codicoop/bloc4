from django.forms.widgets import CheckboxInput


class CustomCheckboxInput(CheckboxInput):
    template_name = "reservations/widgets/custom_checkbox.html"
