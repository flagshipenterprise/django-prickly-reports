from datetime import date

from django.db.models import Sum

from loans.models import Loan
from common import date_


# For the charts on the aggregate report page
def get_aggregate_report_graph_points():
    my_loans = Loan.objects.all()
    oldest_loan = my_loans.order_by('start_date')[0]
    today = date_.today_()

    points = {}
    points['cumulative_loan_count_points'] = []
    for year in range(oldest_loan.start_date.year, today.year+1):
        points['cumulative_loan_count_points'].append(
            [year, my_loans.filter(start_date__lte=date(year, 12, 31)).count()])

    points['cumulative_loan_amount_points'] = []
    for year in range(oldest_loan.start_date.year, today.year+1):
        points['cumulative_loan_amount_points'].append([
            year,
            my_loans.filter(start_date__lte=date(year, 12, 31)).aggregate(Sum('amount'))['amount__sum'] or 0
        ])
    return points


"""
def get_cumulative_interest_points(self):
    oldest_loan = self.loans.order_by('start_date')[0]
    today = date_.today_()

    points = []
    for year in range(oldest_loan.start_date.year, today.year+1):
        points.append([
            year,
            self.loans.filter(start_date__lte=date(year, 12, 31)).aggregate(Sum('amount'))['amount__sum'] or 0
        ])
    return points


def get_cumulative_principal_points(self):
    oldest_loan = self.loans.order_by('start_date')[0]
    today = date_.today_()

    points = []
    for year in range(oldest_loan.start_date.year, today.year+1):
        points.append([
            year,
            self.loans.filter(start_date__lte=date(year, 12, 31)).aggregate(Sum('amount'))['amount__sum'] or 0
        ])
    return points
"""
