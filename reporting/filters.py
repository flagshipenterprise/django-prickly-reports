from datetime import datetime, date
import dateutil
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.db.models.fields import BLANK_CHOICE_DASH
from django.http import QueryDict
from reporting.base import Filter
from reporting.fields import SelectNumericComparisonField


class ChoiceFilter(Filter):
    form_field_class = forms.ChoiceField
    blank_choice = BLANK_CHOICE_DASH

    def __init__(self, choices=[], **kwargs):
        super(ChoiceFilter, self).__init__(**kwargs)
        self.set_choices(choices)

    def set_choices(self, choices=[]):

        # Set the choices
        self.choices = choices

        # If this isn't a required field, add a blank choice
        if self.blank_choice and not self.required:
            self.choices = self.blank_choice + list(self.choices)

    def get_form_field(self):
        return self.form_field_class(
            required=(self.required and not self.filter_set),
            choices=self.choices,
            label=self.label)


class MultipleChoiceFilter(ChoiceFilter):
    form_field_class = forms.MultipleChoiceField
    blank_choice = None

    @staticmethod
    def get_data(name, filter_states, index=None):
        return filter_states.getlist(name, None)


class CharFilter(Filter):
    form_field_class = forms.CharField


class DateFilter(Filter):
    form_field_class = forms.DateField


class NumericComparisonFilter(Filter):
    form_field_class = SelectNumericComparisonField
    filter_state_names = ['%s_0', '%s_1', '%s_2', ]

    def __init__(self, attrnames, operators=None, **kwargs):
        super(NumericComparisonFilter, self).__init__(**kwargs)
        self.attrnames = attrnames

    def get_form_field(self):
        return self.form_field_class(
            required=(self.required and not self.filter_set),
            attrnames=self.attrnames,
            label=self.label)
