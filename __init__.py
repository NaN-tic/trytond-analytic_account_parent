# This file is part analytic_account_parent module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import account


def register():
    Pool.register(
        account.Account,
        module='analytic_account_parent', type_='model')
