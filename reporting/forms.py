from django import forms
from loans.models import Client, FundingSource, Loan, Tag
from accounts.models import Account
from reporting import filtering
from timetracking.models import TimeEntry


class MonthRangeSelectForm(forms.Form):
    start_date = forms.CharField(required=False)
    end_date = forms.CharField(required=False)


class FilteringForm(forms.Form):
    cu_start_date = forms.CharField(required=False)
    cu_end_date = forms.CharField(required=False)
    cu_client = forms.ModelChoiceField(queryset=Client.objects.all(), required=False)
    cu_property = forms.ChoiceField(choices=filtering.CLIENT_UPDATES_FILTERABLE_FIELD_CHOICES, required=False)
    cu_operator = forms.ChoiceField(choices=filtering.OPERATOR_CHOICES, required=False)
    cu_propvalue = forms.CharField(required=False)

    ta_start_date = forms.CharField(required=False)
    ta_end_date = forms.CharField(required=False)
    ta_staff_member = forms.ModelChoiceField(queryset=Account.objects.all(), required=False)
    ta_client = forms.ModelChoiceField(queryset=Client.objects.all(), required=False)

    ta_funding_source = forms.ModelChoiceField(queryset=FundingSource.objects.all(), required=False)
    ta_pre_loan_or_post_loan = forms.ChoiceField(choices=TimeEntry.PRE_OR_POST_CHOICES, required=False)
    ta_property = forms.ChoiceField(choices=filtering.TECHNICAL_ASSISTANCE_FILTERABLE_FIELD_CHOICES, required=False)
    ta_operator = forms.ChoiceField(choices=filtering.OPERATOR_CHOICES, required=False)
    ta_propvalue = forms.CharField(required=False)

    loan_start_date = forms.DateField(required=False)
    loan_end_date = forms.DateField(required=False)
    loan_client = forms.ModelChoiceField(queryset=Client.objects.all(), required=False)
    loan_funding_source = forms.ModelChoiceField(queryset=FundingSource.objects.all(), required=False)
    loan_county = forms.ChoiceField(choices=Loan.COUNTIES, required=False)
    loan_tag = forms.ModelChoiceField(queryset=Tag.objects.all(), required=False)
    loan_property = forms.ChoiceField(choices=filtering.LOAN_FILTERABLE_FIELD_CHOICES, required=False)
    loan_operator = forms.ChoiceField(choices=filtering.OPERATOR_CHOICES, required=False)
    loan_propvalue = forms.CharField(required=False)

    def __init__(self, getlist=[], *args, **kwargs):

        self.account = kwargs.pop('account', None)
        super(FilteringForm, self).__init__(*args, **kwargs)

        for field_name in [
                'cu_property', 'cu_operator',
                'ta_pre_loan_or_post_loan', 'ta_property', 'ta_operator',
                'loan_county', 'loan_property', 'loan_operator']:
            empty = [('', '---------')]
            empty.extend(self.fields[field_name].choices)
            self.fields[field_name].choices = empty

        excluded_tag_ids = []
        for name, values in getlist.iteritems():
            for value in values:
                if name == 'loan_tag':
                    excluded_tag_ids.append(value)
                for field_name in [
                    'cu_start_date', 'cu_end_date', 'cu_client',

                    'ta_start_date', 'ta_end_date', 'ta_staff_member',
                    'ta_client', 'ta_funding_source', 'ta_pre_loan_or_post_loan',

                    'loan_start_date', 'loan_end_date',
                    'loan_client', 'loan_county',
                    'loan_funding_source',
                ]:
                    if name == field_name:
                        self.fields[field_name].initial = value

        self.fields['loan_tag'].queryset = Tag.objects.exclude(pk__in=excluded_tag_ids)

        for field_name in [
                'cu_client',
                'ta_staff_member', 'ta_client', 'ta_funding_source',
                'loan_client', 'loan_funding_source',
                'loan_tag']:
            field = self.fields[field_name]
            field.queryset = field.queryset.all()
