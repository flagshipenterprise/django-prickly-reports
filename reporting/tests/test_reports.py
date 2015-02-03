# Copyright 2015 Steven Barnett
# This program is distributed under the terms of the Lesser GNU Public License

from datetime import date
from django.test import TestCase
from django.forms import Form
from reporting.base import Filter, Report
from reporting.filters import CharFilter, DateFilter


class ConcreteReportClass(Report):
    """
    A sample report class, just for use within the tests module. It just
    filters a very simple set of hard-coded original data based on keywords and
    a date range.
    """
    keywords = CharFilter()
    start_date = DateFilter()
    end_date = DateFilter()

    test_value = None
    original_data = [
        {'date': date(year=2000, day=1, month=1), 'word': "hello"},
        {'date': date(year=2001, day=1, month=1), 'word': "test"},
        {'date': date(year=2002, day=1, month=1), 'word': "word"},
        {'date': date(year=2003, day=1, month=1), 'word': "test"},
        {'date': date(year=2004, day=1, month=1), 'word': "word"},
    ]

    def generate(self):
        processed_data = []
        for item in self.original_data:
            if self.start_date and item['date'] < self.start_date:
                continue
            if self.end_date and item['date'] > self.end_date:
                continue
            if self.keywords and item['word'] not in self.keywords:
                continue
            processed_data.append(item)
        return processed_data


class BadConcreteReportClass(Report):
    """
    Instantiation of this test class should fail since it does not
    implement the generate function. This is just used to ensure that
    the Report class was properly designed as an abstract base class.
    """
    pass


class TestReport(TestCase):

    def setUp(self):
        pass

    def test_get_attr(self):
        """
        Some tests that ensure that the overridden __getattribute__ method on
        the Report abstract base class workds the way we want it to... it
        should return only the "value" attribute of one of it's own attributes
        is of a type which was derived from Filter.
        """
        report = ConcreteReportClass({'keywords': "test"})
        self.assertEquals(report.keywords, "test")

    def test_set_attr(self):
        """
        Basically same test as above, but testing __setattr__ and
        __gettattribute__ together. Really test_get_attr, already tests for
        both of these since the initialization parameters internally call
        __setattr__, but this makes it explicit.
        """
        report = ConcreteReportClass()
        report.keywords = "test"
        self.assertEquals(report.keywords, "test")

    def test_get_filters(self):
        """
        Ensure that the get_filters function returns all/only the Filter based
        attributes on the Report object.
        """
        report = ConcreteReportClass({
            'keywords': "word",
            'start_date': date(year=2002, day=1, month=1)})
        filters = [filt for filt in report.get_filters() if type(filt[1]) is CharFilter or type(filt[1]) is DateFilter]
        self.assertEquals(len(filters), 3)

    def test_generate(self):
        """
        This essentially just tests the test report class... which isn't that
        usefull since it can only be used in the test. But this indirectly
        tests a use case.
        """
        report = ConcreteReportClass({'keywords': "test"})
        self.assertEquals(report.generate(), [
            report.original_data[1],
            report.original_data[3],
        ])

        report = ConcreteReportClass({
            'keywords': "word",
            'start_date': date(year=2002, day=1, month=1)})
        self.assertEquals(report.generate(), [
            report.original_data[2],
            report.original_data[4],
        ])

        report = ConcreteReportClass({
            'keywords': "word",
            'end_date': date(year=2003, day=1, month=1)})
        self.assertEquals(report.generate(), [
            report.original_data[2],
        ])

    def test_bad_report_class(self):
        """
        Attempt to instantiate a concrete report class which has not
        implemented the generate() function.
        """
        with self.assertRaises(Exception):
            report = self.BadConcreteReportClass()

    def test_get_form_class(self):
        """
        Ensure that the get_form_class() function returns a valid django form
        with fields corresponding to the report's filters.
        """
        form_class = ConcreteReportClass().get_form_class()
        self.assertTrue(issubclass(form_class, Form))
        form = form_class()
        self.assertIn('keywords', form.fields)
        self.assertIn('start_date', form.fields)
        self.assertIn('end_date', form.fields)

    def test_get_filter_forms(self):
        forms = ConcreteReportClass().get_filter_forms()
        for form in forms:
            self.assertIn(form.fields.items()[0][0], ['keywords', 'start_date', 'end_date'])

    def test_get_form_class(self):
        """
        Ensure that the get_form_class() function returns a valid django form
        with fields corresponding to the report's filters.
        """
        """
        form_class = ConcreteReportClass().get_form_class()
        self.assertTrue(issubclass(form_class, Form))
        form = form_class()
        self.assertIn('keywords', form.fields)
        self.assertIn('start_date', form.fields)
        self.assertIn('end_date', form.fields)
        """

    def test_get_form_class_filter_fields(self):
        pass  # THIS FEATURE NO LONGER EXISTS...
        #       ... but the test remains in case we want to implement it again
        """
        Same as above, but with the filter_fields argument present to limit the
        filters which are converted into form fields.
        """
        """
        form_class = ConcreteReportClass().get_form_class(
            form_filters=['keywords', 'start_date'])
        form = form_class()
        self.assertIn('keywords', form.fields)
        self.assertIn('start_date', form.fields)
        self.assertNotIn('end_date', form.fields)
        """
