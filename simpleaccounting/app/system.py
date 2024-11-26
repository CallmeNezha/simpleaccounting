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

from typing import Optional
from pydantic import BaseModel, PositiveFloat, ValidationError
from collections import defaultdict

from simpleaccounting.tools.mymath import FloatWithPrecision
from simpleaccounting.ffdb import FFDB
from simpleaccounting.defaults import DEFAULT_ACCOUNTS_2023
from simpleaccounting.tools.dateutil import last_day_of_previous_month, first_day_of_month, last_day_of_month, \
    month_of_date, first_day_of_year, last_day_of_year, first_day_of_next_month


# exceptions
class IllegalOperation(Exception):
    pass


class EntryNotFound(IllegalOperation):
    pass


# models
class Meta:
    """"""
    def __init__(self, meta):
        self.version = meta.version
        self.company = meta.company
        self.month_from = meta.month_from
        self.month_until = meta.month_until


class ExchangeRate:

    def __init__(self, exchange_rate):
        self.rate = exchange_rate.rate
        self.effective_date = exchange_rate.effective_date


class Currency:
    """"""
    def __init__(self, currency):
        self.name = currency.name

    @property
    def exchange_rates(self):
        with FFDB.db_session:
            return [ExchangeRate(er) for er in FFDB.db.Currency.get(name=self.name).exchange_rates]


class Account:
    """"""
    def __init__(self, account):
        self.code = account.code
        self.name = account.name
        self.qualname = account.qualname
        self.major_category = account.major_category
        self.sub_category = account.sub_category
        self.direction = account.direction
        self.custom = account.custom
        self.exchange_gains_and_losses = account.exchange_gains_and_losses

    @property
    def parent(self):
        with FFDB.db_session:
            parent = FFDB.db.Account.get(code=self.code).parent
            if parent is None:
                return None
            else:
                return Account(parent)

    @property
    def children(self):
        with FFDB.db_session:
            return [Account(a) for a in FFDB.db.Account.get(code=self.code).children]

    @property
    def currency(self):
        with FFDB.db_session:
            currency = FFDB.db.Account.get(code=self.code).currency
            if currency is None:
                return None
            else:
                return Currency(currency)


class DebitEntry:
    """"""
    def __init__(self, debitEntry):
        self.account = Account(debitEntry.account)
        self.amount = debitEntry.amount
        self.exchange_rate = ExchangeRate(debitEntry.exchange_rate)
        self.brief = debitEntry.brief


class CreditEntry:
    """"""
    def __init__(self, creditEntry):
        self.account = Account(creditEntry.account)
        self.amount = creditEntry.amount
        self.exchange_rate = ExchangeRate(creditEntry.exchange_rate)
        self.brief = creditEntry.brief


class VoucherEntry(BaseModel):
    account_code: str
    amount: PositiveFloat
    currency_name: str
    brief: str = ""


class Voucher:

    def __init__(self, voucher):
        self.number = voucher.number
        self.category = voucher.category
        self.date = voucher.date
        self.note = voucher.note

        self.debit_entries = []
        self.credit_entries = []

        with FFDB.db_session:
            debit_entries = FFDB.db.Voucher.get(number=self.number).debit_entries
            credit_entries = FFDB.db.Voucher.get(number=self.number).credit_entries

            for debit_entry in debit_entries:
                self.debit_entries.append(DebitEntry(debit_entry))
            for credit_entry in credit_entries:
                self.credit_entries.append(CreditEntry(credit_entry))


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
    def new(filename: pathlib.Path, month: datetime.date):
        # hard transfer
        month = month_of_date(month)
        #
        FFDB.bindDatabase(filename)

        with FFDB.db_session:
            FFDB.db.MetaData(
                version='2024.11.07',
                company=filename.stem,
                month_from=month,
                month_until=month
            )

            rmb = FFDB.db.Currency(
                name='人民币'
            )

            FFDB.db.ExchangeRate(
                currency=rmb,
                rate=1.0,
                effective_date=datetime.date(1970, 1, 1)
            )

            for major_category, accounts in DEFAULT_ACCOUNTS_2023.items():
                for account in accounts:
                    code_parent = '.'.join(account['科目代码'].split('.')[:-1])
                    parent = FFDB.db.Account.get(code=code_parent) if code_parent else None
                    if not FFDB.db.Account.get(name=account['科目名称']):
                        FFDB.db.Account(
                            name=account['科目名称'],
                            qualname=account['科目名称'],
                            code=account['科目代码'],
                            major_category=major_category,
                            sub_category=account['科目类别'],
                            direction=account['余额方向'],
                            parent=parent,
                            custom=False
                        )

            for account in FFDB.db.Account.select():
                account.qualname = System.__account_qualname(account)

            # 月末结转，年末结转
            annual_profit = FFDB.db.Account.get(name='本年利润')
            annual_profit.currency = rmb

            undistributed_profit = FFDB.db.Account.get(name='未分配利润')
            undistributed_profit.currency = rmb

    @staticmethod
    def bindDatabase(filename: pathlib.Path):
        FFDB.bindDatabase(filename)

    @staticmethod
    def meta() -> Meta:
        with FFDB.db_session:
            return Meta(FFDB.db.MetaData.get())

    @staticmethod
    def forwardToNextMonth():
        with FFDB.db_session:
            meta = FFDB.db.MetaData.select().first()
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
                sub_category=parent.sub_category,
                direction=parent.direction,
                parent=parent
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
            elif not account.custom:
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
    def accountByName(name: str):
        with FFDB.db_session:
            account = FFDB.db.Account.get(name=name)
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
            return list((Account(a) for a in FFDB.db.Account.select()))

    @staticmethod
    def setAccountCurrency(account_code: str, currency_name: str, exchange_gains_and_losses: bool=False):
        with FFDB.db_session:
            account = FFDB.db.Account.get(code=account_code)
            if account is None:
                raise EntryNotFound(account_code)
            if account.currency:
                raise IllegalOperation('A2.1/1')
            elif account.children:
                raise IllegalOperation('A2.1/4')
            elif exchange_gains_and_losses:
                if currency_name == '人民币':
                    raise IllegalOperation('A5.1/1')
                elif account.children:
                    raise IllegalOperation('A5.1/2')

            currency = FFDB.db.Currency.get(name=currency_name)
            if currency is None:
                raise EntryNotFound(currency_name)
            account.currency = currency
            account.exchange_gains_and_losses = exchange_gains_and_losses

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

            if er.debit_entries or er.credit_entries:
                raise IllegalOperation('A2.1/3')

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
    def createVoucher(number: str, date: datetime.date, category='记账', note: str='') -> 'FFDB.db.Voucher':
        with FFDB.db_session:
            if FFDB.db.Voucher.get(number=number):
                raise IllegalOperation('A3.2/4')

            voucher = FFDB.db.Voucher(number=number, date=date, category=category, note=note)
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
    def setVoucherNote(voucher_number: str, note: str):
        with FFDB.db_session:
            voucher = FFDB.db.Voucher.get(number=voucher_number)
            if voucher is None:
                raise EntryNotFound(voucher_number)
            voucher.note = note

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

                currency = FFDB.db.Currency.get(name=entry.currency_name)
                er = currency.exchange_rates.select(lambda er: er.effective_date <= voucher.date).order_by(
                    FFDB.db.ExchangeRate.effective_date.desc()
                ).first()
                FFDB.db.DebitEntry(voucher=voucher,
                                   account=account,
                                   amount=entry.amount,
                                   exchange_rate=er,
                                   brief=entry.brief)
                sum_debit += entry.amount * er.rate

            for entry in creditEntries:
                account = FFDB.db.Account.get(code=entry.account_code)
                assert account is not None
                if account.currency is None:
                    raise IllegalOperation('A2.1/1')

                currency = FFDB.db.Currency.get(name=entry.currency_name)
                er = currency.exchange_rates.select(lambda er: er.effective_date <= voucher.date).order_by(
                    FFDB.db.ExchangeRate.effective_date.desc()
                ).first()
                FFDB.db.CreditEntry(voucher=voucher,
                                    account=account,
                                    amount=entry.amount,
                                    exchange_rate=er,
                                    brief=entry.brief)
                sum_credit += entry.amount * er.rate

            if sum_debit != sum_credit:
                raise IllegalOperation('A3.2/2')

    @staticmethod
    def increaseMRUAccount(account_code: str):
        with FFDB.db_session:
            mru = FFDB.db.MRU_Account.get(account_code)
            if mru is None:
                mru = FFDB.db.MRU_Account(
                    account_code=account_code
                )
            mru.hits += 1

    @staticmethod
    def topMRUAccounts(N: int):
        with FFDB.db_session:
            return [
                Account(a) for a in FFDB.db.MRU_Account.select().sort_by(
                FFDB.db.MRU_Account.hits.desc()).limit(N)
            ]

    @staticmethod
    def previewMonthEndCarryForwardVoucherEntries(month: datetime.date):
        with FFDB.db_session:
            number_cost_category = '5'
            number_income_and_expense_category = '6'

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
                          v.category == '记账'
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
                    credit_entries.append(VoucherEntry(account_code=code, amount=amount.value, currency_name='人民币'))
                elif amount < FloatWithPrecision(0.0):
                    debit_entries.append(VoucherEntry(account_code=code, amount=abs(amount.value), currency_name='人民币'))
                # !else
                profit_remains += amount
            # !for

            if profit_remains > 0.0:
                debit_entries.append(VoucherEntry(account_code='4103', amount=profit_remains.value, currency_name='人民币'))
            elif profit_remains < 0.0:
                credit_entries.append(VoucherEntry(account_code='4103', amount=abs(profit_remains.value), currency_name='人民币'))
            # !if
            return debit_entries, credit_entries


    @staticmethod
    def previewYearEndCarryForwardVoucherEntries(year: datetime.date):
        with FFDB.db_session:
            debit_entries = []
            credit_entries = []

            profit_remains = FloatWithPrecision(0.0)
            for v in FFDB.db.Voucher.select(
                    lambda v: v.date >= first_day_of_year(year) and
                              v.date <= last_day_of_year(year) and
                              v.category == '月末结转'):
                for entry in v.debit_entries:
                    if entry.account.code == '4103':
                        profit_remains += entry.amount
                for entry in v.credit_entries:
                    if entry.account.code == '4103':
                        profit_remains -= entry.amount
            # 1for

            if profit_remains > 0.0:
                debit_entries.append(VoucherEntry(account_code='4103', amount=profit_remains.value, currency_name="人民币"))
                credit_entries.append(VoucherEntry(account_code='4104.06', amount=profit_remains.value, currency_name="人民币"))
            elif profit_remains < 0.0:
                credit_entries.append(VoucherEntry(account_code='4103', amount=abs(profit_remains.value), currency_name="人民币"))
                debit_entries.append(VoucherEntry(account_code='4104.06', amount=abs(profit_remains.value), currency_name="人民币"))
            # !if
            return debit_entries, credit_entries







