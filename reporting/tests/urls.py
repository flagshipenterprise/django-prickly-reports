# Copyright 2015 Steven Barnett
# This program is distributed under the terms of the Lesser GNU Public License

from django.conf.urls import patterns, url
from reporting.tests.test_views import ConcreteReportView


urlpatterns = patterns('',
    url(r'^concrete-report/$', ConcreteReportView.as_view(), name='home'),
    url(r'^concrete-report/$', ConcreteReportView.as_view(), name='concrete-report'),
)
