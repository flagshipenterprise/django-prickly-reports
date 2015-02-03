# Copyright 2015 Steven Barnett
# This program is distributed under the terms of the Lesser GNU Public License

"""
Extra form widgets which are particularly useful for filters
"""
from __future__ import unicode_literals

import datetime
import re

from django.forms.widgets import Widget, MultiWidget, Select, NumberInput
from django.utils import datetime_safe
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.utils.formats import get_format
from django.utils import six
from django.conf import settings

__all__ = ('SelectNumericComparisonWidget',)


class FilterSetWidget(MultiWidget):
    pass
    # WOO DYNAMIC MULTIWIDGET WHAT THE FUCK!?


class SelectNumericComparisonWidget(MultiWidget):

    def __init__(self, attrnames, operators, attrs=None):
        widgets = (
            Select(attrs=attrs, choices=attrnames),
            Select(attrs=attrs, choices=operators),
            NumberInput(attrs=attrs)
        )
        super(SelectNumericComparisonWidget, self).__init__(widgets=widgets, attrs=attrs)

    def decompress(self, value):
        return value or (None, None, None)
