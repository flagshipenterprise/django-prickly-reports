from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin, ContextMixin
from django.views.generic.edit import ProcessFormView
from django.template.defaultfilters import slugify
from reporting.exports import CSVView


class ReportMixin(object):
    report_class = None

    def get_report(self):
        return self.get_report_class()(
            filter_states=self.get_filter_states())

    def get_filter_states(self):
        report_class = self.get_report_class()
        return report_class.decode_filter_states(self.request.GET)

    def get_report_class(self):
        return self.report_class


class ReportView(ReportMixin, TemplateView):
    template_name = 'reporting/generic/report_template.html'
    filters_template_name = 'reporting/generic/report_filters_template.html'
    table_template_name = 'reporting/generic/report_table_template.html'
    report_context_name = "report"
    filters_template_context_name = "form_template"
    table_template_context_name = "table_template"
    csv_url_context_name = "csv_url"

    def get(self, request, *args, **kwargs):

        # If we have a "csv" mark, generate a csv and return the file response
        if request.GET.get('csv') is not None:
            csv_view = ReportCSVView(self.get_report())
            return csv_view.dispatch(request, *args, **kwargs)

        # Otherwise, do a normal get
        return super(ReportView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)

        # Add the report instance to the context
        if self.report_context_name:
            context[self.report_context_name] = self.get_report()

        # Add the report form and table sub-templates to the context
        context[self.filters_template_context_name] = self.filters_template_name
        context[self.table_template_context_name] = self.table_template_name

        # Add the url for the csv export to the context
        context[self.csv_url_context_name] = "%s?%s&csv" % (self.request.path_info, self.request.GET.urlencode())

        # Contextualize dat shit
        return context


class ReportCSVView(CSVView):
    def __init__(self, report, *args, **kwargs):
        super(ReportCSVView, self).__init__(*args, **kwargs)
        self.report = report

    def get_data(self):
        return self.report.get_rows()

    def get_headers(self):
        return self.report.get_headers()

    def get_filename(self):
        return '%s.csv' % slugify(self.report.get_title())
