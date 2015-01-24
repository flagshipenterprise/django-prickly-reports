"""
from mock import Mock
from datetime import date

from django.test import TestCase, SimpleTestCase

from common.test import BaseLoantracTest
from accounts.tests.factories import *
from loans.tests.factories import *
from reporting.lib import *
from reporting.filtering import run_custom_filter


class CustomAssertions(object):
    def assertInstanceIn(self, klass, lst):
        for item in lst:
            if isinstance(item, klass):
                break
        else:
            raise AssertionError(
                'An instance of %s was not found in %s.' % (klass.__name__, str(lst)))


class ReportMachineryTest(SimpleTestCase):

    def test_get_remove_url_for_tag(self):
        tag = Mock(id=2, name='Test Tag')
        tag_ids = [1, 2, 3, 4]
        remove_url = get_remove_url_for_tag(tag, tag_ids)
        self.assertEqual(remove_url, '?tag=1&tag=3&tag=4')


class CustomLoanReportsTest(BaseLoantracTest):

    def test_can_filter_by_tags(self):
        tags = [
            TagFactory.create(name='Minority Owned'),
            TagFactory.create(name='Woman Owned'),
            TagFactory.create(name='Veteran Owned'),
        ]
        all_loans = [
            LoanFactory.create(),
            LoanFactory.create(),
            LoanFactory.create(),
        ]
        all_loans[0].tags.add(*tags[:1])
        all_loans[1].tags.add(*tags[:2])
        all_loans[2].tags.add(*tags[:3])

        getlist = {'tag': [unicode(tag.pk) for tag in tags[:3]]}
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 1)

        getlist = {'tag': [unicode(tag.pk) for tag in tags[:2]]}
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 2)

        getlist = {'tag': [unicode(tag.pk) for tag in tags[:1]]}
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 3)

    def test_can_filter_by_date_range(self):
        LoanFactory.create(start_date=date(2012, 1, 1)),
        LoanFactory.create(start_date=date(2012, 6, 20)),
        LoanFactory.create(start_date=date(2013, 1, 1)),
        LoanFactory.create(start_date=date(2013, 6, 20)),
        LoanFactory.create(start_date=date(2014, 1, 1)),
        LoanFactory.create(start_date=date(2014, 6, 20)),

        getlist = {'start_date': ['2012-03-15'], 'end_date': ['2014-03-15']}
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 4)

    def test_can_filter_by_property(self):
        all_loans = [
            LoanFactory.create(term=10),
            LoanFactory.create(term=20),
            LoanFactory.create(term=30),
            LoanFactory.create(term=40),
            LoanFactory.create(term=50),
            LoanFactory.create(term=60),
        ]
        getlist = { 'property': ['term'], 'operator': ['<'], 'propvalue': [40] }
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 3)
        for loan in loans:
            self.assertTrue(loan.term < 40)

        getlist = { 'property': ['term'], 'operator': ['='], 'propvalue': [40] }
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 1)
        self.assertEqual(loans[0].term, 40)

        getlist = { 'property': ['term'], 'operator': ['>'], 'propvalue': [40] }
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 2)
        for loan in loans:
            self.assertTrue(loan.term > 40)

        getlist = { 'property': ['term'], 'operator': ['>='], 'propvalue': [40] }
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 3)
        for loan in loans:
            self.assertTrue(loan.term >= 40)

        getlist = { 'property': ['term'], 'operator': ['<='], 'propvalue': [40] }
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 4)
        for loan in loans:
            self.assertTrue(loan.term <= 40)

    def test_can_filter_by_county(self):
        LoanFactory.create(county='Madison'),
        LoanFactory.create(county='Madison'),
        LoanFactory.create(county='Madison'),
        LoanFactory.create(county='Delaware'),
        LoanFactory.create(county='Delaware'),
        LoanFactory.create(county='Grant'),

        getlist = {'county': ['Madison']}
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 3)

        getlist = {'county': ['Delaware']}
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 2)

        getlist = {'county': ['Grant']}
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 1)

    def test_can_filter_by_county(self):
        LoanFactory.create(county='Madison'),
        LoanFactory.create(county='Madison'),
        LoanFactory.create(county='Madison'),
        LoanFactory.create(county='Delaware'),
        LoanFactory.create(county='Delaware'),
        LoanFactory.create(county='Grant'),

        getlist = {'county': ['Madison']}
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 3)

        getlist = {'county': ['Delaware']}
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 2)

        getlist = {'county': ['Grant']}
        loans = run_custom_filter('loans', getlist)
        self.assertEqual(len(loans), 1)


class CustomTechnicalAssistanceReportsTest(TestCase):

    def test_can_filter_by_date_range(self):
        TrackedTimeFactory.create(date=date(2014, 1, 1), staff_member=self.employee),
        TrackedTimeFactory.create(date=date(2014, 2, 1), staff_member=self.employee),
        TrackedTimeFactory.create(date=date(2014, 3, 1), staff_member=self.employee),
        TrackedTimeFactory.create(date=date(2014, 4, 1), staff_member=self.employee),
        TrackedTimeFactory.create(date=date(2014, 5, 1), staff_member=self.employee),
        TrackedTimeFactory.create(date=date(2014, 6, 1), staff_member=self.employee),

        getlist = {'start_date': ['2014-01-01'], 'end_date': ['2014-06-01']}
        tracked_times = run_custom_filter('technical-assistance', getlist)
        self.assertEqual(len(tracked_times), 6)

        getlist = {'start_date': ['2014-01-15'], 'end_date': ['2014-05-15']}
        tracked_times = run_custom_filter('technical-assistance', getlist)
        self.assertEqual(len(tracked_times), 4)

    def test_can_filter_by_tags(self):
        tags = [
            TagFactory.create(name='Minority Owned'),
            TagFactory.create(name='Woman Owned'),
            TagFactory.create(name='Veteran Owned'),
        ]
        all_loans = [
            LoanFactory.create(),
            LoanFactory.create(),
            LoanFactory.create(),
        ]
        all_loans[0].tags.add(*tags[:1])
        all_loans[1].tags.add(*tags[:2])
        all_loans[2].tags.add(*tags[:3])

        all_clients = [
            ClientFactory.create(),
            ClientFactory.create(),
        ]
        all_clients[0].loans.add(*all_loans[:1])
        all_clients[1].loans.add(*all_loans[1:3])

        staff = DavidAccountFactory.create()
        all_tracked_times = [
            TrackedTimeFactory.create(client=all_clients[0], staff_member=staff),
            TrackedTimeFactory.create(client=all_clients[1], staff_member=staff),
            TrackedTimeFactory.create(client=all_clients[0], staff_member=staff),
            TrackedTimeFactory.create(client=all_clients[1], staff_member=staff),
            TrackedTimeFactory.create(client=all_clients[0], staff_member=staff),
            TrackedTimeFactory.create(client=all_clients[1], staff_member=staff),
        ]

        getlist = { 'tag': [unicode(tag.pk) for tag in tags[2:]] }
        tracked_times = run_custom_filter('technical-assistance', getlist)
        self.assertEqual(len(tracked_times), 3)

        getlist = { 'tag': [unicode(tag.pk) for tag in tags[:1]] }
        tracked_times = run_custom_filter('technical-assistance', getlist)
        self.assertEqual(len(tracked_times), 6)

        getlist = { 'tag': [unicode(tag.pk) for tag in tags] }
        tracked_times = run_custom_filter('technical-assistance', getlist)
        self.assertEqual(len(tracked_times), 3)


class CustomClientUpdateReportsTest(BaseLoantracTest):

    def test_can_filter_by_date_range(self):
        ClientUpdateFactory.create(year=2013, month=10),
        ClientUpdateFactory.create(year=2013, month=11),
        ClientUpdateFactory.create(year=2013, month=12),
        ClientUpdateFactory.create(year=2014, month=1),
        ClientUpdateFactory.create(year=2014, month=2),
        ClientUpdateFactory.create(year=2014, month=3),

        getlist = {'start_date': ['2013-10-01'], 'end_date': ['2014-03-31']}
        client_updates = run_custom_filter('client-updates', getlist)
        self.assertEqual(len(client_updates), 6)

        #getlist = { 'start_date': ['2013-10-15'], 'end_date': ['2014-02-15'] }
        #client_updates = run_custom_filter('client-updates', getlist)
        #self.assertEqual(len(client_updates), 4)
"""
