# Copyright 2015 Steven Barnett
# This program is distributed under the terms of the Lesser GNU Public License

from django.forms import Field, MultiValueField, ChoiceField, CharField, Widget
from reporting.widgets import SelectNumericComparisonWidget
from django.core.exceptions import ValidationError
from django.utils import html


class SelectNumericComparisonField(MultiValueField):

    OPERATORS = [
        ('lte', '<='),
        ('lt', '<'),
        ('eq', '='),
        ('gt', '>'),
        ('gte', '>='),
    ]

    def __init__(self, attrnames=[], operators=OPERATORS, *args, **kwargs):
        self.widget = SelectNumericComparisonWidget(attrnames=attrnames, operators=operators)
        fields = (
            ChoiceField(choices=attrnames),
            ChoiceField(choices=operators),
            CharField(max_length=32, initial=''),
        )
        super(SelectNumericComparisonField, self).__init__(fields=fields, require_all_fields=False, *args, **kwargs)

    def compress(self, data_list):
        return data_list


"""
SubmitButtonField & Widget
Snipped from:   https://djangosnippets.org/snippets/2312/
Usage:          SubmitButtonField(label="", initial=u"Your submit button text")
"""


class SubmitButtonWidget(Widget):
    def render(self, name, value, attrs=None):
        return '<input type="submit" name="%s" value="%s">' % (html.escape(name), html.escape(value))


class SubmitButtonField(Field):
    def __init__(self, *args, **kwargs):
        if not kwargs:
            kwargs = {}
        kwargs["widget"] = SubmitButtonWidget

        super(SubmitButtonField, self).__init__(*args, **kwargs)

    def clean(self, value):
        return value
