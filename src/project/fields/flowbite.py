from django import forms
from django.db import models

from project.fields.base import BaseFlowBiteBoundField


class FlowBiteBoundCharField(BaseFlowBiteBoundField):
    base_classes = "text-sm border rounded-lg block w-full p-2.5"
    no_error_classes = """
        bg-gray-50 border-gray-300 text-gray-900
        focus:ring-primary-600 focus:border-primary-600
        dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white
        dark:focus:ring-primary-500 dark:focus:border-primary-500
        """
    error_classes = """
        bg-red-50 border-red-500 text-red-900 placeholder-red-700
        focus:ring-red-500 focus:border-red-500
        dark:bg-gray-700 dark:text-red-500 dark:placeholder-red-500 dark:border-red-500
        """


class FormCharField(forms.CharField):
    def get_bound_field(self, form, field_name):
        return FlowBiteBoundCharField(form, self, field_name)


class ModelCharField(models.CharField):
    def formfield(self, **kwargs):
        defaults = {"form_class": FormCharField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class FormPasswordField(forms.CharField):
    def get_bound_field(self, form, field_name):
        return FlowBiteBoundCharField(form, self, field_name)


class ModelPasswordField(models.CharField):
    def formfield(self, **kwargs):
        defaults = {"form_class": FormPasswordField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class FormIntegerField(forms.IntegerField):
    def get_bound_field(self, form, field_name):
        return FlowBiteBoundCharField(form, self, field_name)


class ModelIntegerField(models.IntegerField):
    def formfield(self, **kwargs):
        defaults = {"form_class": FormIntegerField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class FormRadioField(forms.ChoiceField):
    def get_bound_field(self, form, field_name):
        return FlowBiteBoundCharField(form, self, field_name)


class ModelRadioField(models.CharField):
    def formfield(self, **kwargs):
        defaults = {"form_class": FormRadioField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class FormSelectDropdownField(forms.ChoiceField):
    def get_bound_field(self, form, field_name):
        return FlowBiteBoundCharField(form, self, field_name)


class ModelSelectDropdownField(models.CharField):
    def formfield(self, **kwargs):
        defaults = {"form_class": FormSelectDropdownField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class FormSelectCheckboxField(forms.MultipleChoiceField):
    def get_bound_field(self, form, field_name):
        return FlowBiteBoundCharField(form, self, field_name)


class ModelSelectCheckboxField(models.CharField):
    def formfield(self, **kwargs):
        defaults = {"form_class": FormSelectCheckboxField}
        defaults.update(kwargs)
        return super(models.CharField, self).formfield(**defaults)


class FormEmailField(forms.EmailField):
    def get_bound_field(self, form, field_name):
        # Using FlowBiteBoundCharField instead of creating an
        # FlowBiteBoundEmailField as, for now, email fields use the same classes
        # as CharFields.
        return FlowBiteBoundCharField(form, self, field_name)


class ModelEmailField(models.EmailField):
    def formfield(self, **kwargs):
        defaults = {"form_class": FormEmailField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class FlowBiteBoundBooleanField(BaseFlowBiteBoundField):
    base_classes = "w-4 h-4 border rounded text-primary-500"
    no_error_classes = (
        "border-gray-300 bg-gray-50 focus:ring-3 focus:ring-primary-300 "
        "dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-primary-600 "
        "dark:ring-offset-gray-800"
    )
    error_classes = (
        "bg-red-50 border-red-500 text-red-700 placeholder-red-700 focus:ring-red-500"
        " focus:border-red-500 dark:bg-gray-700 dark:text-red-500 "
        "dark:placeholder-red-500 dark:border-red-500"
    )


class FormBooleanField(forms.BooleanField):
    def get_bound_field(self, form, field_name):
        return FlowBiteBoundBooleanField(form, self, field_name)


class ModelBooleanField(models.BooleanField):
    def formfield(self, **kwargs):
        defaults = {"form_class": FormBooleanField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
