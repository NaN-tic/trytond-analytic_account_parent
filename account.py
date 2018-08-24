# This file is part analytic_account_parent module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.tools import reduce_ids, grouped_slice
from sql.aggregate import Sum
from sql.conditionals import Coalesce

__all__ = ['Account']


class Account(metaclass=PoolMeta):
    __name__ = 'analytic_account.account'
    left = fields.Integer('Left', required=True, select=True)
    right = fields.Integer('Right', required=True, select=True)

    @classmethod
    def __setup__(cls):
        super(Account, cls).__setup__()
        if not cls.parent.left:
            cls.parent.left = 'left'
        if not cls.parent.right:
            cls.parent.right = 'right'

    @staticmethod
    def default_left():
        return 0

    @staticmethod
    def default_right():
        return 0

    @classmethod
    def get_credit_debit(cls, accounts, names):
        pool = Pool()

        result = super(Account, cls).get_credit_debit(accounts, names)

        Line = pool.get('analytic_account.line')

        table_a = cls.__table__()
        table_c = cls.__table__()
        line = Line.__table__()

        line_query = Line.query_get(line)

        ids = [a.id for a in accounts]
        childs = cls.search([('parent', 'child_of', ids)])
        all_ids = list({}.fromkeys(ids + [c.id for c in childs]).keys())

        cursor = Transaction().connection.cursor()

        for sub_ids in grouped_slice(all_ids):
            red_sql = reduce_ids(table_a.id, sub_ids)
            cursor.execute(*table_a.join(table_c,
                    condition=(table_c.left >= table_a.left)
                    & (table_c.right <= table_a.right)
                    ).join(line, condition=line.account == table_c.id
                    ).select(
                    table_a.id,
                    Sum(Coalesce(line.credit, 0)),
                    Sum(Coalesce(line.debit, 0)),
                    where=red_sql & table_c.active & line_query,
                    group_by=table_a.id))

        for row in cursor.fetchall():
            if 'credit' in names:
                result['credit'][row[0]] = row[1]
            if 'debit' in names:
                result['debit'][row[0]] = row[2]
        return result
