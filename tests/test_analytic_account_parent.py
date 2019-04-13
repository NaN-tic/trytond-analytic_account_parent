# This file is part analytic_account_parent module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import doctest
from decimal import Decimal
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction


class AnalyticAccountParentTestCase(ModuleTestCase):
    'Test Analytic Account Parent module'
    module = 'analytic_account_parent'

    def setUp(self):
        super(AnalyticAccountParentTestCase, self).setUp()
        self.fiscalyear = POOL.get('account.fiscalyear')
        self.journal = POOL.get('account.journal')
        self.move = POOL.get('account.move')
        self.account = POOL.get('account.account')
        self.analytic_account = POOL.get('analytic_account.account')
        self.party = POOL.get('party.party')

    def test0010account_debit_credit(self):
        'Test account debit/credit'
        with Transaction().start(DB_NAME, USER,
                context=CONTEXT) as transaction:
            party = self.party(name='Party')
            party.save()

            # Root - root
            # - Analytic Account 1 - view
            #   - Analytic Account 1A - view
            #     - Analytic Account 1A1 - normal
            #     - Analytic Account 1A2 - normal
            #   - Analytic Account 1B - normal
            # - Analytic Account 2 - view
            #   - Analytic Account 2A - normal

            root, = self.analytic_account.create([{
                        'type': 'root',
                        'name': 'Root',
                        }])
            analytic_account1, analytic_account2 = self.analytic_account.create([{
                        'type': 'view',
                        'name': 'Analytic Account 1',
                        'parent': root.id,
                        'root': root.id,
                        }, {
                        'type': 'view',
                        'name': 'Analytic Account 2',
                        'parent': root.id,
                        'root': root.id,
                        }])
            analytic_account1a, analytic_account1b = self.analytic_account.create([{
                        'type': 'view',
                        'name': 'Analytic Account 1A',
                        'parent': analytic_account1.id,
                        'root': root.id,
                        }, {
                        'type': 'normal',
                        'name': 'Analytic Account 1B',
                        'parent': analytic_account1.id,
                        'root': root.id,
                        }])
            analytic_account1a1, analytic_account1a2 = self.analytic_account.create([{
                        'type': 'normal',
                        'name': 'Analytic Account 1A1',
                        'parent': analytic_account1a.id,
                        'root': root.id,
                        }, {
                        'type': 'normal',
                        'name': 'Analytic Account 1A2',
                        'parent': analytic_account1a.id,
                        'root': root.id,
                        }])
            analytic_account2a, = self.analytic_account.create([{
                        'type': 'normal',
                        'name': 'Analytic Account 2A',
                        'parent': analytic_account2.id,
                        'root': root.id,
                        }])

            fiscalyear, = self.fiscalyear.search([])
            period = fiscalyear.periods[0]
            journal_revenue, = self.journal.search([
                    ('code', '=', 'REV'),
                    ])
            journal_expense, = self.journal.search([
                    ('code', '=', 'EXP'),
                    ])
            revenue, = self.account.search([
                    ('type.revenue', '=', True),
                    ])
            receivable, = self.account.search([
                    ('type.receivable', '=', True),
                    ])
            expense, = self.account.search([
                    ('type.expense', '=', True),
                    ])
            payable, = self.account.search([
                    ('type.payable', '=', True),
                    ])

            # analytic lines
            account_line1b = {
                'account': revenue.id,
                'credit': Decimal(100),
                'analytic_lines': [
                    ('create', [{
                                'account': analytic_account1b.id,
                                'name': 'Analytic Line 1B',
                                'credit': Decimal(100),
                                'debit': Decimal(0),
                                'journal': journal_revenue.id,
                                'date': period.start_date,
                                }])
                    ]}
            account_line1a1 = {
                'account': expense.id,
                'debit': Decimal(30),
                'analytic_lines': [
                    ('create', [{
                                'account': analytic_account1a1.id,
                                'name': 'Analytic Line 1A1',
                                'debit': Decimal(30),
                                'credit': Decimal(0),
                                'journal': journal_expense.id,
                                'date': period.start_date,
                                }])
                    ]}
            account_line1a2 = {
                'account': revenue.id,
                'debit': Decimal(40),
                'analytic_lines': [
                    ('create', [{
                                'account': analytic_account1a2.id,
                                'name': 'Analytic Line 1A2',
                                'debit': Decimal(0),
                                'credit': Decimal(40),
                                'journal': journal_revenue.id,
                                'date': period.start_date,
                                }])
                    ]}
            account_line2a = {
                'account': revenue.id,
                'credit': Decimal(90),
                'analytic_lines': [
                    ('create', [{
                                'account': analytic_account2a.id,
                                'name': 'Analytic Line 2A',
                                'credit': Decimal(90),
                                'debit': Decimal(0),
                                'journal': journal_revenue.id,
                                'date': period.start_date,
                                }])
                    ]}

            # Create some moves
            vlist = [{
                    'period': period.id,
                    'journal': journal_revenue.id,
                    'date': period.start_date,
                    'lines': [
                        ('create', [account_line1b, {
                                    'account': receivable.id,
                                    'debit': Decimal(100),
                                    'party': party.id,
                                    }]),
                        ],
                    }, {
                    'period': period.id,
                    'journal': journal_expense.id,
                    'date': period.start_date,
                    'lines': [
                        ('create', [account_line1a1, {
                                    'account': payable.id,
                                    'credit': Decimal(30),
                                    'party': party.id,
                                    }]),
                        ],
                    }, {
                    'period': period.id,
                    'journal': journal_revenue.id,
                    'date': period.start_date,
                    'lines': [
                        ('create', [account_line1a2, {
                                    'account': receivable.id,
                                    'debit': Decimal(40),
                                    'party': party.id,
                                    }]),
                        ],
                    }, {
                    'period': period.id,
                    'journal': journal_revenue.id,
                    'date': period.start_date,
                    'lines': [
                        ('create', [account_line2a, {
                                    'account': receivable.id,
                                    'debit': Decimal(90),
                                    'party': party.id,
                                    }]),
                        ],
                    },
                ]
            self.move.create(vlist)

            with transaction.set_context(start_date=period.end_date):
                analytic_account = self.analytic_account(analytic_account1.id)
                self.assertEqual(analytic_account.credit, Decimal(140))
                self.assertEqual(analytic_account.debit, Decimal(30))

                analytic_account = self.analytic_account(analytic_account1a.id)
                self.assertEqual(analytic_account.credit, Decimal(40))
                self.assertEqual(analytic_account.debit, Decimal(30))

                analytic_account = self.analytic_account(analytic_account2.id)
                self.assertEqual(analytic_account.credit, Decimal(90))
                self.assertEqual(analytic_account.debit, Decimal(0))

def suite():
    suite = trytond.tests.test_tryton.suite()
    from trytond.modules.account.tests import test_account
    for test in test_account.suite():
        if test not in suite and not isinstance(test, doctest.DocTestCase):
            suite.addTest(test)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            AnalyticAccountParentTestCase))
    return suite
