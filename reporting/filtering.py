from loans.models import *
from timetracking.models import *
from django.db.models import Sum
from clientupdates.models import ClientUpdate
import dateutil.parser
from decimal import Decimal
from datetime import date
import calendar
zero = Decimal('0.00')


# All filtering objects must implement the interface of having a filter function
# that takes a queryset and does something to that queryset and returns it.

# For filtering by tag, the only thing different between the different kinds is
# the double-underscore filtering statement, so factor that out
class FilterByTag(object):
    def __init__(self, tags):
        self.tags = tags

    def filter(self, queryset):
        for tag in self.tags:
            queryset = self.filtering_method(queryset, tag)
        return queryset
class FilterLoansByTag(FilterByTag):
    def filtering_method(self, queryset, tag):
        return queryset.filter(tags=tag)
class FilterTimeEntriesByLoanTag(FilterByTag):
    def filtering_method(self, queryset, tag):
        return queryset.filter(client__loans__tags=tag)
class FilterClientUpdatesByLoanTag(FilterByTag):
    def filtering_method(self, queryset, tag):
        return queryset.filter(client__loans__tags=tag)


class FilterByDateRange(object):
    def __init__(self, start_date, end_date):
        self.start_date = dateutil.parser.parse(start_date)
        self.end_date = dateutil.parser.parse(end_date)
class FilterLoansByDateRange(FilterByDateRange):
    def filter(self, queryset):
        return queryset.filter(
            start_date__gte=self.start_date,
            start_date__lte=self.end_date)
class FilterClientUpdatesByLoanDateRange(FilterByDateRange):
    def filter(self, queryset):
        return queryset.filter(
            client__loans__start_date__gte=self.start_date,
            client__loans__start_date__lte=self.end_date)
class FilterTimeEntriesByLoanDateRange(FilterByDateRange):
    def filter(self, queryset):
        return queryset.filter(
            client__loans__start_date__gte=self.start_date,
            client__loans__start_date__lte=self.end_date)


class FilterTimeEntriesByDateRange(FilterByDateRange):
    def __init__(self, start_date, end_date):
        start_year, start_month, start_day = start_date.split('-')
        end_year, end_month, end_day = end_date.split('-')
        self.start_date = date(int(start_year), int(start_month), int(start_day))
        self.end_date = date(int(end_year), int(end_month), int(end_day))
    def filter(self, queryset):
        return queryset.filter(
            date__gte=self.start_date,
            date__lte=self.end_date)
class FilterClientUpdatesByDateRange(FilterByDateRange):
    def __init__(self, start_date, end_date):
        start_month, start_year = start_date.split('-')
        end_month, end_year = end_date.split('-')
        self.start_date = date(int(start_year), int(start_month), 1)
        self.end_date = date(int(end_year), int(end_month), calendar.monthrange(int(end_year), int(end_month))[1])
    def filter(self, queryset):
        return queryset.filter(month__gte=self.start_date, month__lte=self.end_date)

class FilterByCounty(object):
    def __init__(self, county):
        self.county = county
class FilterLoansByCounty(FilterByCounty):
    def filter(self, queryset):
        return queryset.filter(county=self.county)
class FilterTimeEntriesByLoanCounty(FilterByCounty):
    def filter(self, queryset):
        return queryset.filter(client__loans__county=self.county)
class FilterClientUpdatesByLoanCounty(FilterByCounty):
    def filter(self, queryset):
        return queryset.filter(client__loans__county=self.county)

class FilterByFundingSource(object):
    def __init__(self, funding_source):
        self.funding_source = funding_source
class FilterLoansByFundingSource(FilterByFundingSource):
    def filter(self, queryset):
        return queryset.filter(funding_source=self.funding_source)
class FilterTimeEntriesByLoanFundingSource(FilterByFundingSource):
    def filter(self, queryset):
        return queryset.filter(client__loans__funding_source=self.funding_source)
class FilterClientUpdatesByLoanFundingSource(FilterByFundingSource):
    def filter(self, queryset):
        return queryset.filter(client__loans__funding_source=self.funding_source)
class FilterTimeEntriesByFundingSource(FilterByFundingSource):
    def filter(self, queryset):
        return queryset.filter(funding_source=self.funding_source)

class FilterByClient(object):
    def __init__(self, client):
        self.client = client
class FilterLoansByClient(FilterByClient):
    def filter(self, queryset):
        return queryset.filter(client=self.client)
class FilterTimeEntriesByLoanClient(FilterByClient):
    def filter(self, queryset):
        return queryset.filter(client__loans__client=self.client)
class FilterClientUpdatesByLoanClient(FilterByClient):
    def filter(self, queryset):
        return queryset.filter(client__loans__client=self.client)
class FilterTimeEntriesByClient(FilterByClient):
    def filter(self, queryset):
        return queryset.filter(client=self.client)
class FilterClientUpdatesByClient(FilterByClient):
    def filter(self, queryset):
        return queryset.filter(client=self.client)

class FilterByProperty(object):
    def __init__(self, property_, operator, propvalue):
        self.property = property_
        self.operator = operator
        self.propvalue = propvalue

    def build_params(self, kind, base):
        filter_params = {}
        filter_expression = self.property

        if base == 'client-updates':
            filter_expression = 'response__' + filter_expression

        if (kind == 'technical-assistance' or kind == 'client-updates') and base == 'loan':
            filter_expression = 'client__loans__' + filter_expression

        if self.operator == 'lte':
            filter_expression += '__lte'
        if self.operator == 'lt':
            filter_expression += '__lt'
        if self.operator == 'eq':
            pass
        if self.operator == 'gt':
            filter_expression += '__gt'
        if self.operator == 'gte':
            filter_expression += '__gte'

        filter_params[filter_expression] = self.propvalue
        return filter_params


class FilterLoansByLoanProperty(FilterByProperty):
    def filter(self, queryset):
        return queryset.filter(**self.build_params('loan', 'loan'))
class FilterTimeEntriesByLoanProperty(FilterByProperty):
    def filter(self, queryset):
        return queryset.filter(**self.build_params('technical-assistance', 'loan'))
class FilterClientUpdatesByLoanProperty(FilterByProperty):
    def filter(self, queryset):
        return queryset.filter(**self.build_params('client-updates', 'loan'))
class FilterTimeEntriesByProperty(FilterByProperty):
    def filter(self, queryset):
        return queryset.filter(**self.build_params('technical-assistance', 'technical-assistance'))
class FilterClientUpdatesByProperty(FilterByProperty):
    def filter(self, queryset):
        return queryset.filter(**self.build_params('client-updates', 'client-updates'))


class FilterTimeEntriesByStaffMember(object):
    def __init__(self, staff_member):
        self.staff_member = staff_member
    def filter(self, queryset):
        return queryset.filter(staff_member=self.staff_member)

class FilterTimeEntriesByPreOrPostLoan(object):
    def __init__(self, pre_loan_or_post_loan):
        self.pre_loan_or_post_loan = pre_loan_or_post_loan
    def filter(self, queryset):
        return queryset.filter(pre_loan_or_post_loan=self.pre_loan_or_post_loan)

    
def run_filters(queryset, filters):
    if len(filters) > 0:
        for filter_ in filters:
            queryset = filter_.filter(queryset)
        return queryset.distinct()
    else:
        return queryset.none()


def generate_ta_report(time_budget_entries, time_entries):
    pre_times = time_entries.filter(pre_loan_or_post_loan=TimeEntry.PRE_LOAN)
    post_times = time_entries.filter(pre_loan_or_post_loan=TimeEntry.POST_LOAN)
    admin_times = time_entries.filter(pre_loan_or_post_loan=TimeEntry.ADMIN)

    report = {
        'pre': {
            'actual': (
                (pre_times.aggregate(total=Sum('hours'))['total'] or zero) +
                (pre_times.aggregate(total=Sum('preparation_hours'))['total'] or zero) +
                (pre_times.aggregate(total=Sum('travel_hours'))['total'] or zero)
            ),
            'budgeted': time_budget_entries.aggregate(total=Sum('pre_loan_amount'))['total']
        },
        'post': {
            'actual': (
                (post_times.aggregate(total=Sum('hours'))['total'] or zero) +
                (post_times.aggregate(total=Sum('preparation_hours'))['total'] or zero) +
                (post_times.aggregate(total=Sum('travel_hours'))['total'] or zero)
            ),
            'budgeted': time_budget_entries.aggregate(total=Sum('post_loan_amount'))['total']
        },
        'admin': {
            'actual': (
                (admin_times.aggregate(total=Sum('hours'))['total'] or zero) +
                (admin_times.aggregate(total=Sum('preparation_hours'))['total'] or zero) +
                (admin_times.aggregate(total=Sum('travel_hours'))['total'] or zero)
            ),
            'budgeted': time_budget_entries.aggregate(total=Sum('admin_amount'))['total']
        },
        'total': {
            'actual': (
                (time_entries.aggregate(total=Sum('hours'))['total'] or zero) +
                (time_entries.aggregate(total=Sum('preparation_hours'))['total'] or zero) +
                (time_entries.aggregate(total=Sum('travel_hours'))['total'] or zero)
            ),
            'budgeted': (
                (time_budget_entries.aggregate(total=Sum('pre_loan_amount'))['total'] or zero) +
                (time_budget_entries.aggregate(total=Sum('post_loan_amount'))['total'] or zero) +
                (time_budget_entries.aggregate(total=Sum('admin_amount'))['total'] or zero)
            )
        },
    }
    return report


def generate_cu_report(client_updates):
    months = {}
    for client_update in client_updates:
        if not hasattr(client_update, 'response'):
            continue
        month = date(client_update.month.year, client_update.month.month, 1)
        if not month in months:
            months[month] = {
                'month': month, 'total_sales': 0, 'total_profit': 0,
                'total_ftes': 0
            }
        months[month]['total_sales'] += client_update.response.sales_last_month
        months[month]['total_profit'] += client_update.response.profit_last_month
        months[month]['total_ftes'] += client_update.response.ftes

    # This doesn't feel overly awesome, but it does work
    report = [m[1] for m in sorted(months.iteritems(), key=lambda kv: kv[1])]
    report.append({
        'month': 'Total',
        'total_sales': sum([month['total_sales'] for month in report]),
        'total_profit': sum([month['total_profit'] for month in report]),
        'total_ftes': sum([month['total_ftes'] for month in report])
    })
    return report




LOAN_FILTERABLE_FIELD_CHOICES = [
    ('term', 'Term'),
    ('amount', 'Amount'),
    ('interest_rate', 'Interest Rate'),
    ('credit_score', 'Credit Score'),
    ('annual_income', 'Annual Income'),
]
TECHNICAL_ASSISTANCE_FILTERABLE_FIELD_CHOICES = [
    ('hours', 'Hours'),
    ('travel_hours', 'Travel Hours'),
    ('preparation_hours', 'Preparation Hours'),
    ('miles', 'Miles'),
    ('expenses', 'Expenses'),
]
CLIENT_UPDATES_FILTERABLE_FIELD_CHOICES = [
    ('sales_last_month', 'Sales Last Month'),
    ('profit_last_month', 'Profit Last Month'),
    ('ftes', 'Full Time Equivalent Employees'),
]
OPERATOR_CHOICES = [
    ('lte','<='),
    ('lt', '<'),
    ('eq', '='),
    ('gt', '>'),
    ('gte','>='),
]
LOAN_FILTERABLE_FIELDS = [choice[0] for choice in LOAN_FILTERABLE_FIELD_CHOICES]
OPERATORS = [choice[0] for choice in OPERATOR_CHOICES]
def get_formatted_property(prop, collection):
    for value, formatted in collection:
        if prop == value:
            return formatted
    return ''

def get_formatted_loan_property(prop):
    return get_formatted_property(prop, LOAN_FILTERABLE_FIELD_CHOICES)
def get_formatted_ta_property(prop):
    return get_formatted_property(prop, TECHNICAL_ASSISTANCE_FILTERABLE_FIELD_CHOICES)
def get_formatted_cu_property(prop):
    return get_formatted_property(prop, CLIENT_UPDATES_FILTERABLE_FIELD_CHOICES)
def get_formatted_operator(prop):
    return get_formatted_property(prop, OPERATOR_CHOICES)


def run_custom_filter(kind, filter_data):
    filters = []
    try:
        if 'loan_tag' in filter_data:
            tags = Tag.objects.filter(pk__in=filter_data['loan_tag'])
            if kind == 'loans':
                filters.append(FilterLoansByTag(tags))
            elif kind == 'technical-assistance':
                filters.append(FilterTimeEntriesByLoanTag(tags))
            elif kind == 'client-updates':
                filters.append(FilterClientUpdatesByLoanTag(tags))

        if 'loan_start_date' in filter_data and 'loan_end_date' in filter_data:
            if kind == 'loans':
                filters.append(FilterLoansByDateRange(
                    filter_data['loan_start_date'][0],
                    filter_data['loan_end_date'][0],
                ))
            elif kind == 'technical-assistance':
                filters.append(FilterTimeEntriesByLoanDateRange(
                    filter_data['loan_start_date'][0],
                    filter_data['loan_end_date'][0],
                ))
            elif kind == 'client-updates':
                filters.append(FilterClientUpdatesByLoanDateRange(
                    filter_data['loan_start_date'][0],
                    filter_data['loan_end_date'][0],
                ))
        if 'ta_start_date' in filter_data and 'ta_end_date' in filter_data:
            filters.append(FilterTimeEntriesByDateRange(
                filter_data['ta_start_date'][0],
                filter_data['ta_end_date'][0],
            ))
        if 'cu_start_date' in filter_data and 'cu_end_date' in filter_data:
            filters.append(FilterClientUpdatesByDateRange(
                filter_data['cu_start_date'][0],
                filter_data['cu_end_date'][0],
            ))

        if 'loan_client' in filter_data:
            if kind == 'loans':
                filters.append(FilterLoansByClient(filter_data['loan_client'][0]))
            elif kind == 'technical-assistance':
                filters.append(FilterTimeEntriesByLoanClient(filter_data['loan_client'][0]))
            elif kind == 'client-updates':
                filters.append(FilterClientUpdatesByLoanClient(filter_data['loan_client'][0]))
        if 'ta_client' in filter_data:
            filters.append(FilterTimeEntriesByClient(filter_data['ta_client'][0]))
        if 'cu_client' in filter_data:
            filters.append(FilterClientUpdatesByClient(filter_data['cu_client'][0]))

        if 'loan_county' in filter_data:
            if kind == 'loans':
                filters.append(FilterLoansByCounty(filter_data['loan_county'][0]))
            elif kind == 'technical-assistance':
                filters.append(FilterTimeEntriesByLoanCounty(filter_data['loan_county'][0]))
            elif kind == 'client-updates':
                filters.append(FilterClientUpdatesByLoanCounty(filter_data['loan_county'][0]))

        if 'loan_funding_source' in filter_data:
            funding_source = get_object_or_None(FundingSource, pk=filter_data['loan_funding_source'][0])
            if kind == 'loans':
                filters.append(FilterLoansByFundingSource(funding_source))
            elif kind == 'technical-assistance':
                filters.append(FilterTimeEntriesByLoanFundingSource(funding_source))
            elif kind == 'client-updates':
                filters.append(FilterClientUpdatesByLoanFundingSource(funding_source))
        if 'ta_funding_source' in filter_data:
            ta_funding_source = get_object_or_None(FundingSource, pk=filter_data['ta_funding_source'][0])
            filters.append(FilterTimeEntriesByFundingSource(ta_funding_source))

        if 'loan_attribute' in filter_data:
            for attribute in filter_data['loan_attribute']:
                prop, op, val = attribute.split(',')
                if kind == 'loans':
                    filters.append(FilterLoansByLoanProperty(prop, op, val))
                elif kind == 'technical-assistance':
                    filters.append(FilterTimeEntriesByLoanProperty(prop, op, val))
                elif kind == 'client-updates':
                    filters.append(FilterClientUpdatesByLoanProperty(prop, op, val))

        if 'ta_attribute' in filter_data:
            for attribute in filter_data['ta_attribute']:
                prop, op, val = attribute.split(',')
                filters.append(FilterTimeEntriesByProperty(prop, op, val))
        if 'cu_attribute' in filter_data:
            for attribute in filter_data['cu_attribute']:
                prop, op, val = attribute.split(',')
                filters.append(FilterClientUpdatesByProperty(prop, op, val))

        if 'ta_staff_member' in filter_data:
            staff_member = get_object_or_None(Account, pk=filter_data['ta_staff_member'][0])
            filters.append(FilterTimeEntriesByStaffMember(staff_member))

        if 'ta_pre_loan_or_post_loan' in filter_data:
            filters.append(FilterTimeEntriesByPreOrPostLoan(filter_data['ta_pre_loan_or_post_loan'][0]))

    except Exception as e:
        # If it fails for any reason, just ignore it.
        print 'ERROR', str(e)

    if kind == 'loans':
        return run_filters(Loan.objects.all(), filters)
    if kind == 'technical-assistance':
        # TODO refactor this mess out of here
        time_budget_entries = TimeBudgetEntry.objects.all()
        try:
            if 'ta_start_date' in filter_data and 'ta_end_date' in filter_data:
                start_date = dateutil.parser.parse(filter_data['ta_start_date'][0])
                end_date = dateutil.parser.parse(filter_data['ta_end_date'][0])
                start_date = date(start_date.year, start_date.month, 1)
                end_date = date(end_date.year, end_date.month, calendar.monthrange(end_date.year, end_date.month)[1])
                time_budget_entries = time_budget_entries.filter(month__gte=start_date, month__lte=end_date)

            if 'ta_staff_member' in filter_data:
                staff_member = get_object_or_None(Account, pk=filter_data['ta_staff_member'][0])
                time_budget_entries = time_budget_entries.filter(account=staff_member)

        except Exception as e:
            # If it fails for any reason, just ignore it.
            print str(e)

        return time_budget_entries, run_filters(TimeEntry.objects.all(), filters)
    if kind == 'client-updates':
        return run_filters(ClientUpdate.objects.all(), filters)
