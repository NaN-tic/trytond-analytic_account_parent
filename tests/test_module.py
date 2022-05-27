
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from decimal import Decimal
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.modules.company.tests import (CompanyTestMixin, create_company,
    set_company)
from trytond.modules.account.tests import get_fiscalyear, create_chart


class AnalyticAccountParentTestCase(CompanyTestMixin, ModuleTestCase):
    'Test AnalyticAccountParent module'
    module = 'analytic_account_parent'

    @with_transaction()
    def test0010account_debit_credit(self):
        pool = Pool()
        FiscalYear = pool.get('account.fiscalyear')
        Journal = pool.get('account.journal')
        Move = pool.get('account.move')
        Account = pool.get('account.account')
        AnalyticAccount = pool.get('analytic_account.account')
        Party = pool.get('party.party')
        party = Party(name='Party')
        party.save()

        # Root - root
        # - Analytic Account 1 - view
        #   - Analytic Account 1A - view
        #     - Analytic Account 1A1 - normal
        #     - Analytic Account 1A2 - normal
        #   - Analytic Account 1B - normal
        # - Analytic Account 2 - view
        #   - Analytic Account 2A - normal

        company = create_company()
        with set_company(company):
            root, = AnalyticAccount.create([{
                        'type': 'root',
                        'name': 'Root',
                        }])
            analytic_account1, analytic_account2 = AnalyticAccount.create([{
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
            analytic_account1a, analytic_account1b = AnalyticAccount.create([{
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
            analytic_account1a1, analytic_account1a2 = AnalyticAccount.create([{
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
            analytic_account2a, = AnalyticAccount.create([{
                        'type': 'normal',
                        'name': 'Analytic Account 2A',
                        'parent': analytic_account2.id,
                        'root': root.id,
                        }])

            fiscalyear = get_fiscalyear(company)
            fiscalyear.save()
            FiscalYear.create_period([fiscalyear])
            period = fiscalyear.periods[0]


            create_chart(company)

            journal_revenue, = Journal.search([
                    ('code', '=', 'REV'),
                    ])
            journal_expense, = Journal.search([
                    ('code', '=', 'EXP'),
                    ])
            revenue, = Account.search([
                    ('type.revenue', '=', True),
                    ])
            receivable, = Account.search([
                    ('type.receivable', '=', True),
                    ])
            expense, = Account.search([
                    ('type.expense', '=', True),
                    ])
            payable, = Account.search([
                    ('type.payable', '=', True),
                    ])

            # analytic lines
            account_line1b = {
                'account': revenue.id,
                'credit': Decimal(100),
                'analytic_lines': [
                    ('create', [{
                                'account': analytic_account1b.id,
                                'debit': Decimal(0),
                                'credit': Decimal(100),
                                'date': period.start_date,
                                }])
                    ]}
            account_line1a1 = {
                'account': expense.id,
                'debit': Decimal(30),
                'analytic_lines': [
                    ('create', [{
                                'account': analytic_account1a1.id,
                                'debit': Decimal(30),
                                'credit': Decimal(0),
                                'date': period.start_date,
                                }])
                    ]}
            account_line1a2 = {
                'account': revenue.id,
                'credit': Decimal(40),
                'analytic_lines': [
                    ('create', [{
                                'account': analytic_account1a2.id,
                                'debit': Decimal(0),
                                'credit': Decimal(40),
                                'date': period.start_date,
                                }])
                    ]}
            account_line2a = {
                'account': revenue.id,
                'credit': Decimal(90),
                'analytic_lines': [
                    ('create', [{
                                'account': analytic_account2a.id,
                                'debit': Decimal(0),
                                'credit': Decimal(90),
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
            Move.create(vlist)

            with Transaction().set_context(start_date=period.start_date):
                analytic_account = AnalyticAccount(analytic_account1.id)
                self.assertEqual(analytic_account.debit, Decimal(30))
                self.assertEqual(analytic_account.credit, Decimal(140))

                analytic_account = AnalyticAccount(analytic_account1a.id)
                self.assertEqual(analytic_account.credit, Decimal(40))
                self.assertEqual(analytic_account.debit, Decimal(30))

                analytic_account = AnalyticAccount(analytic_account2.id)
                self.assertEqual(analytic_account.credit, Decimal(90))
                self.assertEqual(analytic_account.debit, Decimal(0))


del ModuleTestCase
