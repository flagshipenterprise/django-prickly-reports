from django.conf.urls import patterns, url
from loans.views import *
from reporting.views import *

urlpatterns = patterns('reporting.views',
    #url(r'^ta-year-detail-report/$', 'ta_year_detail_report', name='ta_year_detail_report'),
    #url(r'^ta-year-detail-report/(?P<budget_year>\d{4})/$', 'ta_year_detail_report', name='ta_year_detail_report'),
    url(r'^reports/export-csv/(?P<budget_year>\d{4})/$', 'export_year_detail_report_csv', name='export_year_detail_report_csv'),
)
