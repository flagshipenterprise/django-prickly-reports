from django_webtest import WebTest
from django.core.urlresolvers import reverse
from reporting.views import ReportView
from reporting.tests.test_reports import ConcreteReportClass


class ConcreteReportView(ReportView):
    report_class = ConcreteReportClass
    template_name = "test_report_view.html"


class TestReportView(WebTest):
    urls = 'reporting.tests.urls'

    def test_form(self):
        response = self.app.get(reverse('concrete-report'))
        self.assertIn('report', response.context)
