from django import forms


class BaseFlowBiteBoundField(forms.BoundField):
    base_classes = ""
    no_error_classes = ""
    error_classes = ""

    def css_classes(self, extra_classes=None):
        """
        Just for documentation.
        This method is called when rendering the "div.html" template, in this line:
        <div{% with classes=field.css_classes %}{% if classes %}
        class="{{ classes }}"{% endif %}{% endwith %}>
        I previously tried to use it to alter the classes contained in the widget's
        attrs, but it's not the place for that.
        """
        return super().css_classes(extra_classes)

    def get_context(self):
        ctxt = super().get_context()
        widget = ctxt["field"].field.widget
        classes = widget.attrs.get("class", "").split()
        classes.append(self.base_classes)
        if self.errors:
            classes.append(self.error_classes)
        else:
            classes.append(self.no_error_classes)
        widget.attrs["class"] = " ".join(classes)
        return ctxt
