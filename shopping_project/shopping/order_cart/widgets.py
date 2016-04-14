from django import forms
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class AdvancedSelect(forms.Select):
    """
    Customised Select widget that allows a list of disabled values to be passed
    to the constructor.  Django's default Select widget doesn't allow this so
    we have to override the render_option method and add a section that checks
    for whether the widget is disabled.
    """

    def __init__(self, attrs=None, choices=(), disabled_values=()):
        self.disabled_values = set(force_text(v) for v in disabled_values)
        super(AdvancedSelect, self).__init__(attrs, choices)

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_text(option_value)
        if option_value in self.disabled_values:
            selected_html = mark_safe(' disabled="disabled"')
        elif option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html(u'<option value="{0}"{1}>{2}</option>',
                           option_value,
                           selected_html,
                           force_text(option_label))
