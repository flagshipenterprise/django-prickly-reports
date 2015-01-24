from loans.models import Loan, LoanApplication, PaymentTable, MissedPayment
from django.db.models import Sum
from common.date_ import today_
from timetracking.models import TimeEntry
from decimal import Decimal
from datetime import date


def _get_year_loan_amounts(year):
    return Loan.objects.filter(start_date__year=year).aggregate(total=Sum('amount'))['total'] or 0


def _get_year_loan_written_off_amount(year):
    return Loan.objects.filter(date_written_off__year=year).aggregate(total=Sum('amount'))['total'] or 0


def _get_month_pre_loan_hours(year, month):
    return TimeEntry.objects.filter(
        date__year=year,
        date__month=month,
        pre_loan_or_post_loan=TimeEntry.PRE_LOAN
    ).aggregate(total=Sum('hours'))['total'] or Decimal(0)


def _get_month_loans_approved(year, month):
    return LoanApplication.objects.filter(
        decision_date__year=year,
        decision_date__month=month
    ).count()


def _get_month_avg_days_from_initial_contact(year, month):
    total = 0

    applications = LoanApplication.objects.filter(
        decision_date__year=year,
        decision_date__month=month
    )

    if applications.count() == 0:
        return 0

    for application in applications:
        total += (application.decision_date - application.first_contact_date).days

    return total / applications.count()


def growth_rates():
    for year in range(2011, today_().year + 1):
        cur_amount = _get_year_loan_amounts(year)
        prev_amount = _get_year_loan_amounts(year - 1)
        if prev_amount != 0:
            yield (year, 100.0 * (cur_amount - prev_amount) / prev_amount)


def default_rates():
    for year in range(2011, today_().year + 1):
        write_off_amount = _get_year_loan_written_off_amount(year)
        total_amount = _get_year_loan_amounts(year)
        if total_amount != 0:
            yield (year, 100.0 * write_off_amount / total_amount)


def delinquency_rates():
    for year in range(2011, today_().year + 1):

        # Find # of missed payments for any loan in this year
        count_missed = MissedPayment.objects.filter(due_date__year=year).count()

        # Find # of payments for all loans in this year
        count_total = 0

        loans = Loan.objects.filter(date_written_off=None).select_related('missed_payments', 'extra_payments')
        for loan in loans:
            table = PaymentTable(loan).generate_payment_table()

            # Total # of payments for this loan
            for row in table:
                if row['date'].year == year and (row['type'] == 'on-time' or row['type'] == 'missed'):
                    count_total += 1

        if count_total == 0:
            yield (year, 0)
        else:
            yield (year, 100.0 * count_missed / count_total)


def pre_loan_hours():
    month = today_().month
    year = today_().year

    for i in range(1, 7):
        month -= 1
        if month == 0:
            month = 12
            year -= 1

        hours = _get_month_pre_loan_hours(year, month)
        loans = _get_month_loans_approved(year, month)

        value = Decimal(1.0) * hours / loans if loans > 0 else 0

        yield (date(year, month, 1), value)


def days_from_initial_contact():
    month = today_().month
    year = today_().year

    for i in range(1, 7):
        month -= 1
        if month == 0:
            month = 12
            year -= 1

        days = _get_month_avg_days_from_initial_contact(year, month)

        yield (date(year, month, 1), days)
