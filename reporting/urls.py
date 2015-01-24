from django.conf.urls import patterns, url
from loans.views import *
from reporting.views import *

urlpatterns = patterns('reporting.views',
    url(r'^dashboard/$', 'reports_dashboard', name='reports_dashboard'),
    url(r'^custom-reports/(?P<kind>loans|technical-assistance|client-updates)/$', 'custom_reports', name='custom_reports'),
    url(r'^aggregate-reports/$', 'aggregate_reports', name='aggregate_reports'),
    # url(r'^funding-source-summary-report/$', FundingSourceSummaryReportView.as_view(), name='fundingsource_summary_report'),
    # url(r'^paid-off-loans-summary-report/$', PaidOffLoansSummaryReportView.as_view(), name='paidoffloans_summary_report'),
    # url(r'^missed-payments-summary-report/$', MissedPaymentsSummaryReportView.as_view(), name='missedpayments_summary_report'),

    url(r'^ta-year-detail-report/$', 'ta_year_detail_report', name='ta_year_detail_report'),
    url(r'^ta-year-detail-report/(?P<budget_year>\d{4})/$', 'ta_year_detail_report', name='ta_year_detail_report'),

    url(r'^reports/export-csv/(?P<budget_year>\d{4})/$', 'export_year_detail_report_csv', name='export_year_detail_report_csv'),
)
