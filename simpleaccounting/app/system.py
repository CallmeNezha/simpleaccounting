"""
    Copyright 2024- ZiJian Jiang @ https://github.com/CallmeNezha

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import pathlib
import datetime
import typing

from typing import Optional

from pydantic import BaseModel, PositiveFloat
from collections import defaultdict, deque


from simpleaccounting.ffdb import FFDB
from simpleaccounting.tools.mymath import FloatWithPrecision
from simpleaccounting.standards import (ACCOUNTS_GENERAL_STANDARD_2018, ACCOUNTS_SMALL_STANDARD_2013,
                                        BALANCE_SHEET_SMALL_STANDARD_2013, BALANCE_SHEET_GENERAL_STANDARD_2018)
from simpleaccounting.tools.dateutil import last_day_of_previous_month, first_day_of_month, last_day_of_month, \
    month_of_date, first_day_of_year, last_day_of_year, first_day_of_next_month, last_day_of_previous_year


def parse_expression(expression):
    """
    Parses and evaluates a mathematical expression containing only + and - operators.

    Args:
        expression (str): The mathematical expression to evaluate, e.g., "AD+BD-CE".

    Returns:
        list: A list of terms with their respective signs, e.g., ['+AD', '+BD', '-CE']
    """
    import re

    # Add a leading '+' if the expression starts without a sign
    if expression[0] not in ('+', '-'):
        expression = '+' + expression

    # Use regex to match terms with their signs
    terms = re.findall(r'[+-][\w\u4E00-\u9FFF]+', expression)

    return terms

# exceptions
class IllegalOperation(Exception):
    pass


class EntryNotFound(IllegalOperation):
    pass


# models
class Meta:
    """"""
    def __init__(self, meta: 'FFDB.db.Meta'):
        self.version: str = meta.version
        self.company: str = meta.company
        self.month_from: datetime.date = meta.month_from
        self.month_until: datetime.date = meta.month_until
        self.standard: str = meta.standard


class ExchangeRate:

    def __init__(self, exchange_rate: 'FFDB.db.ExchangeRate'):
        self.rate: FloatWithPrecision = FloatWithPrecision(exchange_rate.rate)
        self.effective_date: datetime.date = exchange_rate.effective_date


class Currency:
    """"""
    def __init__(self, currency: 'FFDB.db.Currency'):
        self.name: str = currency.name
        self.is_local: bool = currency.is_local

    @property
    def exchange_rates(self) -> list[ExchangeRate]:
        with FFDB.db_session:
            return [ExchangeRate(er) for er in FFDB.db.Currency.get(name=self.name).exchange_rates]


class Account:
    """"""

    def __init__(self, account: 'FFDB.db.Account'):
        self.code: str = account.code
        self.name: str = account.name
        self.qualname: str = account.qualname
        self.major_category: str = account.major_category
        self.direction: str = account.direction
        self.is_custom: bool = account.is_custom
        self.need_exchange_gains_losses: bool = account.need_exchange_gains_losses

    @property
    def parent(self) -> typing.Optional['Account']:
        with FFDB.db_session:
            parent = FFDB.db.Account.get(code=self.code).parent
            if parent is None:
                return None
            else:
                return Account(parent)

    @property
    def children(self) -> list['Account']:
        with FFDB.db_session:
            return [Account(a) for a in FFDB.db.Account.get(code=self.code).children]

    @property
    def currency(self) -> typing.Optional['Currency']:
        with FFDB.db_session:
            currency = FFDB.db.Account.get(code=self.code).currency
            if currency is None:
                return None
            else:
                return Currency(currency)

    def debitEntries(self, filter=None):
        with FFDB.db_session:
            if filter:
                return list(FFDB.db.Account.get(code=self.code).debit_entries.select(filter))
            else:
                return list(FFDB.db.Account.get(code=self.code).debit_entries.select())

    def creditEntries(self, filter=None):
        with FFDB.db_session:
            if filter:
                return list(FFDB.db.Account.get(code=self.code).credit_entries.select(filter))
            else:
                return list(FFDB.db.Account.get(code=self.code).credit_entries.select())


class DebitEntry:
    """"""
    def __init__(self, debit: 'FFDB.db.DebitEntry'):
        self.account: Account = Account(debit.account)
        self.currency: str = debit.currency
        self.amount: FloatWithPrecision = FloatWithPrecision(debit.amount)
        self.exchange_rate: FloatWithPrecision = FloatWithPrecision(debit.exchange_rate)
        self.brief: Optional[str] = debit.brief


class CreditEntry:
    """"""
    def __init__(self, credit: 'FFDB.db.CreditEntry'):
        self.account: Account = Account(credit.account)
        self.currency: str = credit.currency
        self.amount: FloatWithPrecision = FloatWithPrecision(credit.amount)
        self.exchange_rate: FloatWithPrecision = FloatWithPrecision(credit.exchange_rate)
        self.brief: Optional[str] = credit.brief


class VoucherEntry(BaseModel):
    account_code: str
    amount: PositiveFloat
    currency: str
    exchange_rate: PositiveFloat
    brief: str = ""


class Voucher:

    def __init__(self, voucher: 'FFDB.db.Voucher'):
        self.number: str = voucher.number
        self.category: str = voucher.category
        self.date = voucher.date
        self.debit_entries = []
        self.credit_entries = []

        with FFDB.db_session:
            debit_entries = FFDB.db.Voucher.get(number=self.number).debit_entries
            credit_entries = FFDB.db.Voucher.get(number=self.number).credit_entries

            for debit_entry in debit_entries:
                self.debit_entries.append(DebitEntry(debit_entry))
            for credit_entry in credit_entries:
                self.credit_entries.append(CreditEntry(credit_entry))


class BalanceSheetEntry:
    """"""
    def __init__(self, balance_sheet_entry: 'FFDB.db.BalanceSheetEntry'):
        self.category: str = balance_sheet_entry.category
        self.item: str = balance_sheet_entry.item
        self.line_number: Optional[int] = balance_sheet_entry.line_number
        self.formula: str = balance_sheet_entry.formula


class BalanceSheetTemplate:
    """"""
    def __init__(self, balance_sheet_template: 'FFDB.db.BalanceSheetTemplate'):
        self.name: str = balance_sheet_template.name
        with FFDB.db_session:
            self.entries = [BalanceSheetEntry(bste) for bste in FFDB.db.BalanceSheetTemplate.get(name=self.name).asset_liability_entries.sort_by(FFDB.db.BalanceSheetEntry.id)]

# system
class System:
    """"""
    @staticmethod
    def __account_qualname(account):
        qualname = account.name
        pp = account
        while pp.parent:
            pp = pp.parent
            qualname = pp.name + '/' + qualname
        return qualname

    @staticmethod
    def __is_account_code_parent(code_parent: str, code: str):
        code_code_parent = '.'.join(code.split('.')[:-1])
        return code_parent == code_code_parent

    @staticmethod
    def __is_account_code_format(text: str) -> bool:
        if not text.strip():
            return False
        if text.startswith('.') or text.endswith('.'):
            return False
        try:
            map(int, text.strip().split('.'))
            return True
        except Exception as e:
            return False

    @staticmethod
    def new(filename: pathlib.Path, standard: typing.Literal['一般企业会计准则（2018）', '小企业会计准则（2013）'], month: datetime.date):
        if standard == '一般企业会计准则（2018）':
            standard_accounts = ACCOUNTS_GENERAL_STANDARD_2018
            balance_entries = BALANCE_SHEET_GENERAL_STANDARD_2018
        elif standard == '小企业会计准则（2013）':
            standard_accounts = ACCOUNTS_SMALL_STANDARD_2013
            balance_entries = BALANCE_SHEET_SMALL_STANDARD_2013

        # hard transfer
        month = month_of_date(month)
        #
        FFDB.bindDatabase(filename)

        with FFDB.db_session:
            FFDB.db.Meta(
                version='2024.11.07',
                standard=standard,
                company=filename.stem,
                month_from=month,
                month_until=month
            )

            rmb = FFDB.db.Currency(
                name='人民币',
                is_local=True
            )

            FFDB.db.ExchangeRate(
                currency=rmb,
                rate=1.0,
                effective_date=datetime.date(1970, 1, 1)
            )

            for major_category, accounts in standard_accounts.items():
                for account in accounts:
                    code_parent = '.'.join(account['科目代码'].split('.')[:-1])
                    parent = FFDB.db.Account.get(code=code_parent) if code_parent else None
                    FFDB.db.Account(
                        name=account['科目名称'],
                        qualname=System.__account_qualname(parent) + '/' + account['科目名称'] if parent else account['科目名称'] ,
                        code=account['科目代码'],
                        major_category=major_category,
                        direction=account['余额方向'],
                        parent=parent,
                        is_custom=False
                    )

            # 月末结转，年末结转，汇兑损益
            if standard == '一般企业会计准则（2018）':
                annual_profit = FFDB.db.Account.get(name='本年利润')
                annual_profit.currency = rmb
                undistributed_profit = FFDB.db.Account.get(name='未分配利润')
                undistributed_profit.currency = rmb
                exchange_difference = FFDB.db.Account.get(name='汇兑差额')
                exchange_difference.currency = rmb
            elif standard == '小企业会计准则（2013）':
                annual_profit = FFDB.db.Account.get(name='本年利润')
                annual_profit.currency = rmb
                undistributed_profit = FFDB.db.Account.get(name='未分配利润')
                undistributed_profit.currency = rmb
                exchange_difference = FFDB.db.Account.get(name='汇兑损益')
                exchange_difference.currency = rmb
                prior_year_profit_loss_adjustments = FFDB.db.Account.get(name='以前年度损益调整')
                prior_year_profit_loss_adjustments.currency = rmb

            #
            template = FFDB.db.BalanceSheetTemplate(name='默认')
            for category, entries in balance_entries.items():
                for entry in entries:
                    item, lineno, formula = entry
                    se = FFDB.db.BalanceSheetEntry(
                        template=template,
                        category=category,
                        item=item,
                        line_number = lineno,
                        formula=formula or ''
                    )

    @staticmethod
    def bindDatabase(filename: pathlib.Path):
        FFDB.bindDatabase(filename)

    @staticmethod
    def meta() -> Meta:
        with FFDB.db_session:
            return Meta(FFDB.db.Meta.get())

    @staticmethod
    def forwardToNextMonth():
        with FFDB.db_session:
            meta = FFDB.db.Meta.select().first()
            meta.month_until = month_of_date(first_day_of_next_month(meta.month_until))

    @staticmethod
    def createAccount(parent_code: str,
                      code: str,
                      name: str,
                      ) -> Account:
        """"""
        if not System.__is_account_code_format(code):
            raise IllegalOperation("A1.2.1.2/1")
        elif not System.__is_account_code_format(parent_code):
            raise IllegalOperation("A1.2.1.2/1")

        if not System.__is_account_code_parent(parent_code, code):
            raise IllegalOperation("A1.2.1.2/1")

        with FFDB.db_session:
            parent = FFDB.db.Account.get(code=parent_code)
            if not parent:
                raise IllegalOperation("A1.2.1/2")

            if parent.currency is not None:
                raise IllegalOperation('A1.2.1/4')

            if FFDB.db.Account.get(name=name):
                raise IllegalOperation('A1.2.1/8')

            if FFDB.db.Account.get(code=code):
                raise IllegalOperation('A1.1/2')

            account = FFDB.db.Account(
                name=name,
                qualname=parent.qualname + '/' + name,
                code=code,
                major_category=parent.major_category,
                direction=parent.direction,
                parent=parent,
                is_custom=True
            )
        # !with
        return Account(account)

    @staticmethod
    def deleteAccount(code: str):
        with FFDB.db_session:
            account = FFDB.db.Account.get(code=code)
            if account is None:
                raise EntryNotFound(code)
            if account.currency:
                raise IllegalOperation("A1.2.1/5")
            elif not account.is_custom:
                raise IllegalOperation("A1.1/5")
            elif account.children:
                raise IllegalOperation("A1.2.1/6")
            elif account.debit_entries:
                raise IllegalOperation("A1.2.1/5")
            elif account.credit_entries:
                raise IllegalOperation("A1.2.1/5")
            else:
                account.delete()

    @staticmethod
    def account(code: str) -> Optional[Account]:
        with FFDB.db_session:
            account = FFDB.db.Account.get(code=code)
            if account is None:
                return None
            return Account(account)

    @staticmethod
    def accountByQualname(qualname: str):
        with FFDB.db_session:
            account = FFDB.db.Account.get(qualname=qualname)
            if account is None:
                return None
            return Account(account)

    @staticmethod
    def accounts() -> list[Account]:
        with FFDB.db_session:
            return list((Account(a) for a in FFDB.db.Account.select().order_by(FFDB.db.Account.code)))

    @staticmethod
    def setAccountCurrency(account_code: str, currency_name: str, need_exchange_gains_losses: bool=False):
        with FFDB.db_session:
            account = FFDB.db.Account.get(code=account_code)
            if account is None:
                raise EntryNotFound(account_code)
            if account.currency:
                raise IllegalOperation('A2.1/1')
            elif account.children:
                raise IllegalOperation('A2.1/4')
            elif need_exchange_gains_losses:
                if currency_name == '人民币':
                    raise IllegalOperation('A5.1/1')
                elif account.children:
                    raise IllegalOperation('A5.1/2')

            currency = FFDB.db.Currency.get(name=currency_name)
            if currency is None:
                raise EntryNotFound(currency_name)
            account.currency = currency
            account.need_exchange_gains_losses = need_exchange_gains_losses

    @staticmethod
    def createCurrency(name: str) -> Currency:
        with FFDB.db_session:
            if FFDB.db.Currency.get(name=name):
                raise IllegalOperation('A2.2/2')
            currency = FFDB.db.Currency(name=name)
            FFDB.db.ExchangeRate(currency=currency,
                                 rate=1.0,
                                 effective_date=datetime.date(1970, 1, 1))
            return Currency(currency)

    @staticmethod
    def currencies() -> list[Currency]:
        with FFDB.db_session:
            return list((Currency(c) for c in FFDB.db.Currency.select()))

    @staticmethod
    def currency(name: str) -> Optional[Currency]:
        with FFDB.db_session:
            currency = FFDB.db.Currency.get(name=name)
            if currency is None:
                return None
            return Currency(currency)

    @staticmethod
    def deleteCurrency(name: str):
        if name == '人民币':
            raise IllegalOperation('A2.2/1')

        with FFDB.db_session:
            currency = FFDB.db.Currency.get(name=name)
            if currency is None:
                raise EntryNotFound(name)

            if currency.accounts:
                raise IllegalOperation('A2.1/2')
            currency.delete()

    @staticmethod
    def createExchangeRate(currency_name: str, rate: float, effective_date: datetime.date):
        if currency_name == '人民币':
            raise IllegalOperation('A2.2/1')

        with FFDB.db_session:
            currency = FFDB.db.Currency.get(name=currency_name)
            if currency is None:
                raise EntryNotFound(currency_name)

            if FFDB.db.ExchangeRate.get(currency=currency,
                                        effective_date=effective_date):
                raise IllegalOperation('A2.2/6')
            exchange_rate = FFDB.db.ExchangeRate(currency=currency,
                                                 rate=rate,
                                                 effective_date=effective_date)
            return ExchangeRate(exchange_rate)

    @staticmethod
    def deleteExchangeRate(currency_name: str, effective_date: datetime.date):
        if currency_name == '人民币':
            raise IllegalOperation('A2.2/1')

        with FFDB.db_session:
            currency = FFDB.db.Currency.get(name=currency_name)
            if currency is None:
                raise EntryNotFound(currency_name)

            er = FFDB.db.ExchangeRate.get(currency=currency,
                                          effective_date=effective_date)

            if er is None:
                raise EntryNotFound(currency_name, effective_date)

            er.delete()

    @staticmethod
    def exchangeRates(currency_name: str) -> list[ExchangeRate]:
        with FFDB.db_session:
            currency = FFDB.db.Currency.get(name=currency_name)
            if currency is None:
                raise EntryNotFound(currency_name)

            exchange_rates = currency.exchange_rates.select().order_by(
                FFDB.db.ExchangeRate.effective_date.desc()
            )
            return list((ExchangeRate(er) for er in exchange_rates))

    @staticmethod
    def exchangeRate(currency_name: str, date: datetime.date) -> Optional[ExchangeRate]:
        with FFDB.db_session:
            currency = FFDB.db.Currency.get(name=currency_name)
            if currency is None:
                raise EntryNotFound(currency_name)

            er = currency.exchange_rates.select(lambda er: er.effective_date <= date).order_by(
                FFDB.db.ExchangeRate.effective_date.desc()
            ).first()
            if er is None:
                return None
            return ExchangeRate(er)

    @staticmethod
    def voucher(number: str):
        with FFDB.db_session:
            if not FFDB.db.Voucher.get(number=number):
                raise EntryNotFound(number)
            return Voucher(FFDB.db.Voucher.get(number=number))

    @staticmethod
    def vouchers(filter):
        with FFDB.db_session:
            return [Voucher(v) for v in FFDB.db.Voucher.select(filter)]

    @staticmethod
    def createVoucher(number: str, date: datetime.date, category='记账') -> 'FFDB.db.Voucher':
        with FFDB.db_session:
            if FFDB.db.Voucher.get(number=number):
                raise IllegalOperation('A3.2/4')

            voucher = FFDB.db.Voucher(number=number, date=date, category=category)
            return Voucher(voucher)

    @staticmethod
    def setVoucherDate(voucher_number: str, date: datetime.date):
        with FFDB.db_session:
            voucher = FFDB.db.Voucher.get(number=voucher_number)
            if voucher is None:
                raise EntryNotFound(voucher_number)

            if (first_day_of_month(voucher.date) > date or
                last_day_of_month(voucher.date) < date):
                raise IllegalOperation("Can't set date outside voucher's month")
            #
            voucher.date = date

    @staticmethod
    def changeVoucherNumber(old_voucher_number: str, new_voucher_number: str):
        with FFDB.db_session:
            voucher = FFDB.db.Voucher.get(number=old_voucher_number)
            if voucher is None:
                raise EntryNotFound(old_voucher_number)
            voucher.number = new_voucher_number

    @staticmethod
    def deleteVoucher(number: str):
        with FFDB.db_session:
            voucher = FFDB.db.Voucher.get(number=number)
            if voucher is None:
                raise EntryNotFound(number)
            voucher.delete()

    @staticmethod
    def updateDebitCreditEntries(voucher_number: str,
                                 debitEntries: list[VoucherEntry],
                                 creditEntries: list[VoucherEntry]):

        with FFDB.db_session:
            voucher = FFDB.db.Voucher.get(number=voucher_number)
            if voucher is None:
                raise EntryNotFound(voucher_number)

            voucher.debit_entries.clear()
            voucher.credit_entries.clear()

            sum_debit = FloatWithPrecision(0.0)
            sum_credit = FloatWithPrecision(0.0)

            for entry in debitEntries:
                account = FFDB.db.Account.get(code=entry.account_code)
                assert account is not None
                if account.currency is None:
                    raise IllegalOperation('A2.1/1')

                currency = FFDB.db.Currency.get(name=entry.currency)
                assert currency is not None
                if currency is None:
                    raise IllegalOperation('A2.1/1')

                FFDB.db.DebitEntry(voucher=voucher,
                                   account=account,
                                   currency=entry.currency,
                                   amount=entry.amount,
                                   exchange_rate=entry.exchange_rate,
                                   brief=entry.brief)
                sum_debit += entry.amount * entry.exchange_rate

            for entry in creditEntries:
                account = FFDB.db.Account.get(code=entry.account_code)
                assert account is not None
                if account.currency is None:
                    raise IllegalOperation('A2.1/1')

                currency = FFDB.db.Currency.get(name=entry.currency)
                assert currency is not None
                if currency is None:
                    raise IllegalOperation('A2.1/1')

                FFDB.db.CreditEntry(voucher=voucher,
                                    account=account,
                                    currency=entry.currency,
                                    amount=entry.amount,
                                    exchange_rate=entry.exchange_rate,
                                    brief=entry.brief)
                sum_credit += entry.amount * entry.exchange_rate

            if sum_debit != sum_credit:
                raise IllegalOperation('A3.2/2')

    @staticmethod
    def increaseMRUAccount(account_code: str):
        with FFDB.db_session:
            mru = FFDB.db.MRU_Account.get(account_code=account_code)
            if mru is None:
                mru = FFDB.db.MRU_Account(
                    account_code=account_code
                )
            mru.hits += 1

    @staticmethod
    def topMRUAccounts(N: int):
        with FFDB.db_session:
            return [
                Account(FFDB.db.Account.get(code=mru_account.account_code)) for mru_account in FFDB.db.MRU_Account.select().sort_by(
                FFDB.db.MRU_Account.hits.desc()).limit(N)
            ]

    @staticmethod
    def previewMonthEndCarryForwardVoucherEntries(month: datetime.date):

        if System.meta().standard == '一般企业会计准则（2018）':
            annual_profit_code = System.accountByQualname('本年利润').code
            number_cost_category = '5'
            number_income_and_expense_category = '6'

        elif System.meta().standard == '小企业会计准则（2013）':
            annual_profit_code = System.accountByQualname('本年利润').code
            number_cost_category = '4'
            number_income_and_expense_category = '5'

        with FFDB.db_session:

            # 获取所有成本及损益大类细分科目
            cost_categories = [
                acc.code for acc in FFDB.db.Account.select(
                    lambda a: not a.children and a.code.startswith(number_cost_category))]

            income_and_expense_categories = [
                acc.code for acc in FFDB.db.Account.select(
                    lambda a: not a.children and a.code.startswith(number_income_and_expense_category))]

            # 获取本月度成本及损益大类细分科目的记账凭证条目
            debit_entries = []
            credit_entries = []

            query = FFDB.db.Voucher.select(
                lambda v: first_day_of_month(month) <= v.date and
                          v.date <= last_day_of_month(month) and
                          v.category in ('记账', '汇兑损益结转')
            )

            for v in query:
                for entry in v.debit_entries:
                    if entry.account.code in cost_categories + income_and_expense_categories:
                        debit_entries.append(entry)
                for entry in v.credit_entries:
                    if entry.account.code in cost_categories + income_and_expense_categories:
                        credit_entries.append(entry)

            # 借方本期发生额
            debit_credit_amounts = defaultdict(lambda: FloatWithPrecision(0.0))

            for entry in debit_entries:
                debit_credit_amounts[entry.account.code] += entry.amount

            for entry in credit_entries:
                debit_credit_amounts[entry.account.code] -= entry.amount

            # 借方和贷方本期发生额
            credit_entries = []
            debit_entries = []
            profit_remains = FloatWithPrecision(0.0)
            for code, amount in debit_credit_amounts.items():
                if amount > FloatWithPrecision(0.0):
                    credit_entries.append(VoucherEntry(account_code=code, amount=amount.value, currency='人民币', exchange_rate=1.0))
                elif amount < FloatWithPrecision(0.0):
                    debit_entries.append(VoucherEntry(account_code=code, amount=abs(amount.value), currency='人民币', exchange_rate=1.0))
                # !else
                profit_remains += amount
            # !for

            if profit_remains > 0.0:
                debit_entries.append(VoucherEntry(account_code=annual_profit_code, amount=profit_remains.value, currency='人民币', exchange_rate=1.0))
            elif profit_remains < 0.0:
                credit_entries.append(VoucherEntry(account_code=annual_profit_code, amount=abs(profit_remains.value), currency='人民币', exchange_rate=1.0))
            # !if
            return debit_entries, credit_entries

    @staticmethod
    def previewYearEndCarryForwardVoucherEntries(year: datetime.date):

        if System.meta().standard == '一般企业会计准则（2018）':
            annual_profit_code = System.accountByQualname('本年利润').code
            undistributed_profit_code = System.accountByQualname('利润分配/未分配利润').code

        elif System.meta().standard == '小企业会计准则（2013）':
            annual_profit_code = System.accountByQualname('本年利润').code
            undistributed_profit_code = System.accountByQualname('利润分配/未分配利润').code

        with FFDB.db_session:
            debit_entries = []
            credit_entries = []

            profit_remains = FloatWithPrecision(0.0)
            for v in FFDB.db.Voucher.select(
                    lambda v: v.date >= first_day_of_year(year) and
                              v.date <= last_day_of_year(year) and
                              v.category == '月末结转'):
                for entry in v.debit_entries:
                    if entry.account.code == annual_profit_code:
                        profit_remains += entry.amount
                for entry in v.credit_entries:
                    if entry.account.code == annual_profit_code:
                        profit_remains -= entry.amount
            # 1for

            if profit_remains > 0.0:
                credit_entries.append(
                    VoucherEntry(account_code=annual_profit_code, amount=abs(profit_remains.value), currency="人民币",
                                 exchange_rate=1.0))
                debit_entries.append(
                    VoucherEntry(account_code=undistributed_profit_code, amount=abs(profit_remains.value), currency="人民币",
                                 exchange_rate=1.0))
            elif profit_remains < 0.0:
                debit_entries.append(VoucherEntry(account_code=annual_profit_code, amount=abs(profit_remains.value), currency="人民币",
                                                  exchange_rate=1.0))
                credit_entries.append(
                    VoucherEntry(account_code=undistributed_profit_code, amount=abs(profit_remains.value), currency="人民币",
                                 exchange_rate=1.0))

            # !if
            return debit_entries, credit_entries

    @staticmethod
    def incurredBalances(account_code: str, date_from: datetime.date, date_until: datetime.date) -> tuple[
        FloatWithPrecision|None, FloatWithPrecision|None,
        FloatWithPrecision|None, FloatWithPrecision|None,
        FloatWithPrecision|None, FloatWithPrecision|None,
        FloatWithPrecision|None, FloatWithPrecision|None]:
        with (((FFDB.db_session))):
            account = FFDB.db.Account.get(code=account_code)
            if not account.children:
                if account.currency is None:
                    return None, FloatWithPrecision(0.0), \
                    None, FloatWithPrecision(0.0), \
                    None, FloatWithPrecision(0.0), \
                    None, FloatWithPrecision(0.0)
                #
                account_currency: str = account.currency.name
                debit_entries = account.debit_entries.select(lambda e: e.voucher.date <= date_until)
                credit_entries = account.credit_entries.select(lambda e: e.voucher.date <= date_until)

                begin_amount = FloatWithPrecision(0.0)
                begin_local_amount = FloatWithPrecision(0.0)
                incurred_debit_amount = FloatWithPrecision(0.0)
                incurred_debit_local_amount = FloatWithPrecision(0.0)
                incurred_credit_amount = FloatWithPrecision(0.0)
                incurred_credit_local_amount = FloatWithPrecision(0.0)
                currency_amount = FloatWithPrecision(0.0)
                currency_local_amount = FloatWithPrecision(0.0)
                for entry in debit_entries:
                    # there are exchange gains and losses vouchers that use local currency
                    if account_currency == entry.currency:
                        currency_amount += entry.amount
                        if entry.voucher.date < date_from:
                            begin_amount += entry.amount
                        else:
                            incurred_debit_amount += entry.amount
                    # 1if
                    local_amount = entry.amount * entry.exchange_rate
                    currency_local_amount += local_amount
                    if entry.voucher.date < date_from:
                        begin_local_amount += local_amount
                    else:
                        incurred_debit_local_amount += local_amount
                    #
                for entry in credit_entries:
                    # there are exchange gains and losses vouchers that use local currency
                    if account_currency == entry.currency:
                        currency_amount -= entry.amount
                        if entry.voucher.date < date_from:
                            begin_amount -= entry.amount
                        else:
                            incurred_credit_amount += entry.amount
                    # 1if
                    local_amount = entry.amount * entry.exchange_rate
                    currency_local_amount -= local_amount
                    if entry.voucher.date < date_from:
                        begin_local_amount -= local_amount
                    else:
                        incurred_credit_local_amount += local_amount
                #
                return (begin_amount, begin_local_amount,
                        incurred_debit_amount, incurred_debit_local_amount,
                        incurred_credit_amount, incurred_credit_local_amount,
                        currency_amount, currency_local_amount)
            else:
                stack = deque()
                stack.append(account)
                leafs = []
                while stack:
                    account = stack.pop()
                    if account.children:
                        for a in account.children:
                            stack.append(a)
                        # 1for
                    else:
                        leafs.append(account)
                    # 1if
                # 1while
                begin_sum_local = FloatWithPrecision(0.0)
                end_sum_local = FloatWithPrecision(0.0)
                incurred_debit_sum_local = FloatWithPrecision(0.0)
                incurred_credit_sum_local = FloatWithPrecision(0.0)
                for account in leafs:
                    (_, beginning_balance,
                     _, incurred_debit,
                     _, incurred_credit,
                     _, ending_balance) = System.incurredBalances(account.code, date_from, date_until)
                    begin_sum_local += beginning_balance
                    end_sum_local += ending_balance
                    incurred_debit_sum_local += incurred_debit
                    incurred_credit_sum_local += incurred_credit
                return None, begin_sum_local, None, incurred_debit_sum_local, None, incurred_credit_sum_local, None, end_sum_local

    @staticmethod
    def endingBalance(account_code: str, date_until: datetime.date) -> tuple[FloatWithPrecision|None, FloatWithPrecision]:
        with FFDB.db_session:
            account = FFDB.db.Account.get(code=account_code)
            if not account.children:
                if account.currency is None:
                    return FloatWithPrecision(0.0), FloatWithPrecision(0.0)
                #
                account_currency: str = account.currency.name
                debit_entries = account.debit_entries.select(lambda e: e.voucher.date <= date_until)
                credit_entries = account.credit_entries.select(lambda e: e.voucher.date <= date_until)

                currency_amount = FloatWithPrecision(0.0)
                currency_local_amount = FloatWithPrecision(0.0)
                for entry in debit_entries:
                    # there are exchange gains and losses vouchers that use local currency
                    if account_currency == entry.currency:
                        currency_amount += entry.amount
                    # 1if
                    currency_local_amount += entry.amount * entry.exchange_rate
                for entry in credit_entries:
                    # there are exchange gains and losses vouchers that use local currency
                    if account_currency == entry.currency:
                        currency_amount -= entry.amount
                    # 1if
                    currency_local_amount -= entry.amount * entry.exchange_rate
                #
                return currency_amount, currency_local_amount
            else:
                stack = deque()
                stack.append(account)
                leafs = []
                while stack:
                    account = stack.pop()
                    if account.children:
                        for a in account.children:
                            stack.append(a)
                        # 1for
                    else:
                        leafs.append(account)
                    # 1if
                # 1while
                local_amount = FloatWithPrecision(0.0)
                for account in leafs:
                    _, ending_balance = System.endingBalance(account.code, date_until)
                    local_amount += ending_balance
                return None, local_amount

    @staticmethod
    def previewExchangeGainsAndLosses(month: datetime.date):

        if System.meta().standard == '一般企业会计准则（2018）':
            exchange_diff_code = System.accountByQualname('财务费用/汇兑差额').code

        elif System.meta().standard == '小企业会计准则（2013）':
            exchange_diff_code = System.accountByQualname('财务费用/汇兑损益').code

        def pair_entries(gains_losses: FloatWithPrecision, account_code: str, brief: str):

            debit_entry = None
            credit_entry = None

            if gains_losses > 0.0:
                debit_entry = VoucherEntry(
                    account_code=account_code,
                    amount=gains_losses.value,
                    currency='人民币',
                    exchange_rate=1.0,
                    brief=brief
                )
                credit_entry = VoucherEntry(
                    account_code=exchange_diff_code,
                    amount=gains_losses.value,
                    currency='人民币',
                    exchange_rate=1.0,
                    brief=brief
                )
            elif gains_losses < 0.0:
                debit_entry = VoucherEntry(
                    account_code=exchange_diff_code,
                    amount=abs(gains_losses.value),
                    currency='人民币',
                    exchange_rate=1.0,
                    brief=brief
                )
                credit_entry = VoucherEntry(
                    account_code=account_code,
                    amount=abs(gains_losses.value),
                    currency='人民币',
                    exchange_rate=1.0,
                    brief=brief
                )
            return (debit_entry, credit_entry) if debit_entry else None

        #
        debit_entries = []
        credit_entries = []

        with FFDB.db_session:
            for account in FFDB.db.Account.select():
                if not account.need_exchange_gains_losses:
                    continue
                # 1for

                account_currency = account.currency.name
                current_exchange_rate = System.exchangeRate(account.currency.name, last_day_of_month(month)).rate

                remains_currency, remains_local_currency = System.endingBalance(account.code, last_day_of_previous_month(month))
                beginning_balance_gains_losses = remains_currency * current_exchange_rate - remains_local_currency
                if pair := pair_entries(beginning_balance_gains_losses, account.code, '期初余额'):
                    debit_entries.append(pair[0])
                    credit_entries.append(pair[1])

                for entry in account.debit_entries.select(
                    lambda e: e.voucher.date >= first_day_of_month(month) and # noqa
                              e.voucher.date <= last_day_of_month(month)):
                    if entry.currency == account_currency:
                        gains_losses = (current_exchange_rate - entry.exchange_rate) * entry.amount
                        if pair := pair_entries(gains_losses, account.code, entry.voucher.number):
                            debit_entries.append(pair[0])
                            credit_entries.append(pair[1])

                for entry in account.credit_entries.select(
                    lambda e: e.voucher.date >= first_day_of_month(month) and # noqa
                              e.voucher.date <= last_day_of_month(month)):
                    if entry.currency == account_currency:
                        gains_losses = - (current_exchange_rate - entry.exchange_rate) * entry.amount
                        if pair := pair_entries(gains_losses, account.code, entry.voucher.number):
                            debit_entries.append(pair[0])
                            credit_entries.append(pair[1])

        return debit_entries, credit_entries

    @staticmethod
    def balanceSheetTemplates():
        with FFDB.db_session:
            return [BalanceSheetTemplate(bste) for bste in FFDB.db.BalanceSheetTemplate.select()]

    @staticmethod
    def balanceSheet(template: BalanceSheetTemplate, date_until: datetime.date):

        date_from = first_day_of_year(date_until)

        beginnings = defaultdict(lambda: FloatWithPrecision(0.0))
        endings = defaultdict(lambda: FloatWithPrecision(0.0))

        for entry in template.entries:
            if entry.line_number and entry.formula:
                terms = parse_expression(entry.formula.replace(' ', ''))
                for term in terms:
                    sign = term[0]
                    try:
                        lineno = int(term[1:])
                        if sign == '+':
                            beginnings[entry.line_number] += beginnings[lineno]
                            endings[entry.line_number] += endings[lineno]
                        elif sign == '-':
                            beginnings[entry.line_number] -= beginnings[lineno]
                            endings[entry.line_number] -= endings[lineno]
                    except:
                        account = System.accountByQualname(term[1:])
                        if account:
                            _, begin, _, _, _, _, _, end = System.incurredBalances(account.code, date_from, date_until)
                            if sign == '+':
                                beginnings[entry.line_number] += begin
                                endings[entry.line_number] += end
                            elif sign == '-':
                                beginnings[entry.line_number] -= begin
                                endings[entry.line_number] -= end
        #
        return beginnings, endings

    @staticmethod
    def updateBalanceSheetTemplate(name: str, asset_entries, liability_entries):
        with FFDB.db_session:
            bste = FFDB.db.BalanceSheetTemplate.get(name=name)
            if not bste:
                return

            bste.asset_liability_entries.clear()

            for entry in asset_entries:
                item, lineno, formula = entry
                FFDB.db.BalanceSheetEntry(
                    template = bste,
                    category = '资产',  # 资产 / 负债和所有者权益（或股东权益）
                    item = item,
                    line_number = lineno,
                    formula = formula or ''
                )

            for entry in liability_entries:
                item, lineno, formula = entry
                FFDB.db.BalanceSheetEntry(
                    template = bste,
                    category = '负债和所有者权益（或股东权益）',  # 资产 /
                    item = item,
                    line_number = lineno,
                    formula = formula or ''
                )
