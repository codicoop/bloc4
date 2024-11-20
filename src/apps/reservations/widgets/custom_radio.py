from django.forms.widgets import RadioSelect


class CustomRadioSelect(RadioSelect):
    def __init__(self, attrs=None):
        default_attrs = {
            "class": "flex items-stretch "
            "justify-between w-full h-full p-5 text-gray-900 bg-white "
            "border border-gray-200 rounded-lg cursor-pointer shadow "
            "dark:hover:text-gray-300 pointer dark:border-gray-700 "
            "dark:peer-checked:text-primary-500 "
            "peer-checked:border-primary-600 "
            "peer-checked:text-primary-600 hover:bg-gray-50 "
            "dark:text-gray-400 dark:bg-gray-800 "
            "dark:hover:bg-gray-700"
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
