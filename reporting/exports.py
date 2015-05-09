from django.http import HttpResponse
from django.views.generic.base import View
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
import csv

from lxml import etree
from z3c.rml import document
from StringIO import StringIO


class CSVView(View):

    headers = None
    filename = "report.csv"

    def __init__(self):
        self.writer = None
        self.data = None

    def get_data(self, *args, **kwargs):
        return []

    def get_filename(self, *args, **kwargs):
        return self.filename

    def get_headers(self, *args, **kwargs):
        return self.headers

    def get_row(self, row_data, i):
        return row_data

    def write_headers(self):
        if self.headers and len(self.headers) > 0:
            if isinstance(self.headers[0], list):
                for row in self.headers:
                    self.write_row(row)
            else:
                self.write_row(self.headers)

    def write_rows(self):
        i = 0
        for row_data in self.data:
            row = self.get_row(row_data, i)
            if row:
                self.write_row(row)
            i += 1

    def write_row(self, row):
        row = [item for item in row]
        self.writer.writerow(row)

    def dispatch(self, request, *args, **kwargs):
        self.data = self.get_data(*args, **kwargs)
        self.filename = self.get_filename(*args, **kwargs)
        self.headers = self.get_headers(*args, **kwargs)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = "attachment; filename=%s" % self.filename
        self.writer = csv.writer(response)
        self.write_headers()
        self.write_rows()
        return response


class PDFView(View):

    filename = 'report.pdf'
    template_name = ''

    def get_filename(self):
        return self.filename

    def get_context_data(self):
        return {}

    def dispatch(self, request, *args, **kwargs):
        if self.template_name == '':
            raise ImproperlyConfigured(
                "A template_name must be specified for the rml template.")

        context = self.get_context_data()

        # Use StringIO and not cStringIO because cStringIO can't accept unicode characters
        buf = StringIO()
        rml = render_to_string(self.template_name, context)


        buf.write(rml)
        buf.seek(0)
        root = etree.parse(buf).getroot()
        # Make the rml available in the context for testing purposes
        context['rml'] = root
        doc = document.Document(root)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = \
            "filename=%s" % self.get_filename()
        doc.process(response)

        return response
