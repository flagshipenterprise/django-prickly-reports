from loans.models import Loan, MissedPayment


class PaidOffLoansSummaryReport(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.loans = Loan.objects.filter(
            date_paid_off__gte=self.start_date,
            date_paid_off__lte=self.end_date,
        ).order_by('-date_paid_off')

    def generate(self):
        return self.loans


class MissedPaymentsSummaryReport(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.missed_payments = MissedPayment.objects.filter(
            due_date__gte=self.start_date,
            due_date__lte=self.end_date,
        ).order_by('-due_date')

    def generate(self):
        return self.missed_payments
