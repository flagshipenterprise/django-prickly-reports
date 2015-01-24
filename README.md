=========
Reporting
=========

Reporting is a simple, filterable report generator.


Quick Start
-----------

1. Add "reporting" to your INSTALLED\_APPS.
    
    # settings.py

    INSTALLED_APPS = (
        ...
        "reporting",
    )

2. In one of your apps, import the reporting module and make a report in "yourapp/reports.py"

    # yourapp/reports.py

    from reporting.base import Report
    from reporting import filters

    class SomeKindaReport(Report):
        
        # Report class members which inherit from base.Filter, can be used to
        # filter the data retrieved in get_queryset, and will be rendered as
        # forms in a ReportView.

        start_date = filters.DateFilter()
        end_date = filters.DateFilter()

        # Since no headers member was provided, a logical default will be
        # generated. If a report is desired which has no headers, simply set
        # it to an empty list.
        # headers = ["Start Date", "End Date"]


        # Return the filtered queryset of objects (or just a list of things).
        # Since filters can become complex, and because the same filters may
        # be used by various reports in different ways, there is no simple
        # over-ridable default for this function... it must be specified.

        def get_queryset(self):
            qs = Object.objects.all()

            if self.start_date:
                qs = qs.filter(date__gt=self.start_date)

            if self.end_date:
                qs = qs.filter(date__lt=self.end_date)

            return qs


        # Get row is called on every object returned by get_queryset in order
        # to generate the final data table. It should (but doesn't need to)
        # return a list of the same length as headers, in general.

        def get_row(self, object):
            return [
                object.property1,
                object.property2,
                ...
            ]
