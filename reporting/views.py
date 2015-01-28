import json
import csv
import calendar
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from common import date_
from datetime import date

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.views.generic import FormView, TemplateView
from django.views.generic.base import ContextMixin
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from braces.views import LoginRequiredMixin

from reporting import filtering
from reporting.forms import FilteringForm, MonthRangeSelectForm
from reporting import lib as reportcsvlib
from reporting import queries as reports_queries
from reporting.exports import CSVView
from reporting import dashboard

from loans.models import Tag, Loan, FundingSource

from timetracking import reports as ta_reports
from timetracking import queries as ta_queries

from accounts.models import Account
from accounts.mixins import (
    MinimumRoleRequiredMixin,
)
from loans.queries import county_report as loan_county_report


def reports_dashboard(request):
    if (not request.user.is_authenticated()) or (request.user.role <= Account.EMPLOYEE):
        raise PermissionDenied

    return render(request, 'reports/dashboard.html', {
        'growth_rates': dashboard.growth_rates,
        'default_rates': dashboard.default_rates,
        'delinquency_rates': dashboard.delinquency_rates,
        'pre_loan_hours': dashboard.pre_loan_hours,
        'days_from_initial_contact': dashboard.days_from_initial_contact
    })


def getlist_to_querystring(getlist):
    variables = []
    for name, values in getlist.iteritems():
        for value in values:
            variables.append('%s=%s' % (name, str(value)))
    return '?' + '&'.join(variables)


def update_getlist(getlist, updates):
    # Repopulate fields that are not related to models (and don't have a pk)
    for field_name in [
        'cu_start_date', 'cu_end_date',
        'ta_start_date', 'ta_end_date',
        'ta_pre_loan_or_post_loan',
        'loan_start_date', 'loan_end_date', 'loan_county',
    ]:
        if updates[field_name]:
            getlist[field_name] = [updates[field_name]]
        else:
            if field_name in getlist:
                del getlist[field_name]

    # Repopulate fields that are related to models (and have a pk)
    for field_name in [
        'cu_client',
        'ta_staff_member', 'ta_client', 'ta_funding_source',
        'loan_client', 'loan_funding_source',
    ]:
        if updates[field_name]:
            getlist[field_name] = [updates[field_name].pk]
        else:
            if field_name in getlist:
                del getlist[field_name]

    if updates['loan_tag']:
        getlist['loan_tag'].append(updates['loan_tag'].pk)

    if updates['remove_loan_tag']:
        getlist['loan_tag'] = [
            tag_id for tag_id in getlist['loan_tag'] if str(tag_id) != str(updates['remove_loan_tag'])
        ]
    if len(getlist['loan_tag']) == 0:
        del getlist['loan_tag']

    for kind in ['loan', 'ta', 'cu']:
        if (updates[kind + '_property'] and
                updates[kind + '_operator'] and
                updates[kind + '_propvalue']):
            getlist[kind + '_attribute'].append(','.join([
                updates[kind + '_property'],
                updates[kind + '_operator'],
                updates[kind + '_propvalue'],
            ]))
        else:
            if kind + '_property' in getlist:
                del getlist[kind + '_property']
            if kind + '_operator' in getlist:
                del getlist[kind + '_operator']
            if kind + '_propvalue' in getlist:
                del getlist[kind + '_propvalue']

        if updates['remove_' + kind + '_attribute']:
            getlist[kind + '_attribute'] = [
                attr for attr in getlist[kind + '_attribute'] if attr != updates['remove_' + kind + '_attribute']
            ]
        if len(getlist[kind + '_attribute']) == 0:
            del getlist[kind + '_attribute']


@login_required
def custom_reports(request, kind):
    getlist = defaultdict(list)
    getlist.update(request.GET.iterlists())

    if not request.user.role >= Account.EMPLOYEE:
        raise PermissionDenied()

    # If this is a POST we are adding another filter, so take care of that and redirect to a GET
    if request.method == 'POST':
        form = FilteringForm(data=request.POST, getlist=getlist, account=request.user)
        if form.is_valid():
            form.cleaned_data['remove_loan_tag'] = None
            form.cleaned_data['remove_cu_attribute'] = None
            form.cleaned_data['remove_ta_attribute'] = None
            form.cleaned_data['remove_loan_attribute'] = None

            if 'filter' not in request.POST:
                if 'remove_loan_tag' in request.POST:
                    form.cleaned_data['remove_loan_tag'] = request.POST.get('remove_loan_tag')
                if 'remove_cu_attribute' in request.POST:
                    form.cleaned_data['remove_cu_attribute'] = request.POST.get('remove_cu_attribute')
                if 'remove_ta_attribute' in request.POST:
                    form.cleaned_data['remove_ta_attribute'] = request.POST.get('remove_ta_attribute')
                if 'remove_loan_attribute' in request.POST:
                    form.cleaned_data['remove_loan_attribute'] = request.POST.get('remove_loan_attribute')

            update_getlist(getlist, form.cleaned_data)
        return HttpResponseRedirect(
            reverse('custom_reports', args=(kind,)) + getlist_to_querystring(getlist))
    else:
        form = FilteringForm(getlist=getlist, account=request.user)

    loan_tags = Tag.objects.filter(pk__in=getlist.get('loan_tag', []))

    filtered = filtering.run_custom_filter(kind, getlist)

    need_filters_set = len(getlist) == 0

    if kind == 'loans':
        loans = filtered
        if loans:
            loans.last_month = (date_.today_() + relativedelta(months=-1)).strftime('%b')
            for loan in loans:
                loan.last_months_payments = loan.get_last_months_payments(date_.today_())
        total_results = len(loans)

    elif kind == 'technical-assistance':
        time_budget_entries, time_entries = filtered
        ta_report = filtering.generate_ta_report(time_budget_entries, time_entries)
        total_results = len(time_entries)

    elif kind == 'client-updates':
        client_updates = filtered
        cu_report = filtering.generate_cu_report(client_updates)
        total_results = len(client_updates)

    loan_attributes = [{
        'loan_property': filtering.get_formatted_loan_property(prop),
        'loan_operator': filtering.get_formatted_operator(op),
        'loan_propvalue': val,
        'raw': ','.join([prop, op, val]),
    } for prop, op, val in [attr.split(',') for attr in getlist['loan_attribute']]]
    ta_attributes = [{
        'ta_property': filtering.get_formatted_ta_property(prop),
        'ta_operator': filtering.get_formatted_operator(op),
        'ta_propvalue': val,
        'raw': ','.join([prop, op, val]),
    } for prop, op, val in [attr.split(',') for attr in getlist['ta_attribute']]]
    cu_attributes = [{
        'cu_property': filtering.get_formatted_cu_property(prop),
        'cu_operator': filtering.get_formatted_operator(op),
        'cu_propvalue': val,
        'raw': ','.join([prop, op, val]),
    } for prop, op, val in [attr.split(',') for attr in getlist['cu_attribute']]]

    csv_export_url = reverse('custom_reports', args=(kind,)) + getlist_to_querystring(getlist) + '&csv=1'

    if 'csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        filename = '%s-custom-report-%s.csv' % (kind, date_.today_().isoformat())
        response['Content-Disposition'] = 'attachment; filename=' + filename
        writer = csv.writer(response)
        if kind == 'loans':
            last_month = (date_.today_() + relativedelta(months=-1)).strftime('%b')
            rows = reportcsvlib.get_filtered_loans_csv_data(loans, last_month, date_.today_())
        if kind == 'technical-assistance':
            rows = reportcsvlib.get_filtered_ta_csv_data(ta_report)
            rows.append([])
            rows.append(['Staff Member', 'Client', 'Hours', 'Prep Hours', 'Travel Hours', 'Miles', 'Expenses', 'Date', 'Hour Type', 'Activity Summary'])
            rows.extend([
                entry.staff_member,
                entry.client,
                entry.hours,
                entry.preparation_hours,
                entry.travel_hours,
                entry.miles,
                entry.expenses,
                entry.date,
                entry.hour_type,
                entry.activity_summary,
            ] for entry in time_entries)
        if kind == 'client-updates':
            rows = reportcsvlib.get_filtered_cu_csv_data(cu_report)
        for row in rows:
            writer.writerow(row)
        return response
    else:
        return render(request, 'reports/custom_reports.html', locals())


@login_required
def aggregate_reports(request):

    if request.user.role == Account.CLIENT:
        raise PermissionDenied()

    today = date_.today_()

    funding_sources = FundingSource.objects.all().prefetch_related('loans')
    for source in funding_sources:
        source.aggregate_report = source.get_aggregate_report(today)

    loan_aggregate_report = Loan.objects.get_aggregate_report(today)

    total_loan_count = Loan.objects.count()

    all_tags = Tag.objects.all()
    loan_tags = []
    loans_by_tag_points = []

    tag_counts = []
    for tag in all_tags:
        tag_count = tag.loans.count()
        tag_counts.append({
            'name': tag.name,
            'count': tag_count,
            'percent': tag_count * 1.0 / total_loan_count * 100
        })

    for i, tag in enumerate(all_tags):
        loan_tags.append([i, tag.name])
        loans_by_tag_points.append(
            [[i, tag.loans.count() * 1.0 / total_loan_count * 100]]
        )

    nxt = len(loan_tags)
    loan_tags.append([nxt, 'Having One or More'])
    count = 0
    for loan in Loan.objects.all().select_related('tags').all():
        if loan.tags.count() > 0:
            count += 1
    tag_counts.append({
        'name': 'Having One or More',
        'count': count,
        'percent': count * 1.0 / total_loan_count * 100
    })

    loans_by_tag_points.append([[nxt, count * 1.0 / total_loan_count * 100]])
    loan_tags_json = json.dumps(loan_tags)
    points = reports_queries.get_aggregate_report_graph_points()

    county_report = loan_county_report()

    return render(request, 'reports/aggregate_reports.html', locals())


def get_ordered_months_header(first_month):
    months_header = ['']

    unordered_months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]

    months_header.extend(unordered_months[first_month - 1:])
    months_header.extend(unordered_months[:first_month - 1])

    months_header.append('Year Total')
    return months_header


@login_required
def ta_year_detail_report(request, budget_year=None):
    if request.user.role == Account.CLIENT:
        raise PermissionDenied()
    if budget_year is None:
        now = timezone.now()
        budget_year = ta_queries.get_dates_budget_year(now, request.settings)
        return redirect('ta_year_detail_report', budget_year=budget_year)
    else:
        budget_year = int(budget_year)
    prev_year = budget_year - 1
    next_year = budget_year + 1

    months_header = get_ordered_months_header(request.settings.first_month_of_budgeting_year)

    report = ta_reports.TAYearOrganizationReport(budget_year, request.settings).generate()
    return render(request, 'reports/ta_year_detail_report.html', locals())


@login_required
def export_year_detail_report_csv(request, budget_year):
    if request.user.role == Account.CLIENT:
        raise PermissionDenied()
    budget_year = int(budget_year)

    report = ta_reports.TAYearOrganizationReport(budget_year, request.settings).generate()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=year-detailed-report-%s.csv' % budget_year
    writer = csv.writer(response)

    months_header = get_ordered_months_header(request.settings.first_month_of_budgeting_year)

    writer.writerow(['Year Detailed Report'])
    writer.writerow([])

    def make_subsection(writer, title, total_data, data):
        writer.writerow([title] + total_data)
        for account, cols in data.iteritems():
            writer.writerow(['        ' + account.get_full_name()] + cols)

    for subsection in report:
        writer.writerow([subsection['title']])
        writer.writerow(months_header)

        make_subsection(writer, 'Total Direct TA', subsection['total_direct'], subsection['direct'])
        make_subsection(writer, 'Total Travel', subsection['total_travel'], subsection['travel'])
        make_subsection(writer, 'Total Preparation', subsection['total_prep'], subsection['prep'])
        make_subsection(writer, 'Total ' + subsection['title'], subsection['grand_total'], subsection['total'])
        writer.writerow([])
    return response



# #################### IT'S THE [Um] NEW [...stuff] !!!! ################## #

from django.views.generic.base import TemplateResponseMixin, ContextMixin
from django.views.generic.edit import ProcessFormView


class ReportMixin(object):
    report_class = None

    """
    def __init__(self, report_class=None, *args, **kwargs):
        if report_class:
            self.report_class = report_class
        return super(ReportMixin, self).__init__(*args, **kwargs)
    """

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
