import pathlib
import datetime

from typing import Optional
from pydantic import BaseModel, PositiveFloat, ValidationError

from simplefinance.tools.mymath import FloatWithPrecision
from simplefinance.ffdb import FFDB
from simplefinance.defaults import DEFAULT_ACCOUNTS_2023
from simplefinance.tools.dateutil import last_day_of_previous_month, first_day_of_month, last_day_of_month


class IllegalOperation(Exception):
    pass


class Meta:
    """"""
    def __init__(self, meta):
        self.version = meta.version
        self.company = meta.company
        self.date_from = meta.date_from
        self.date_until = meta.date_until


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

    @property
    def parent(self):
        with FFDB.db_session:
            parent = FFDB.db.Account.get(code=self.code).parent
            if parent is None:
                return None
            else:
                return Account(parent)

    @property
    def currency(self):
        with FFDB.db_session:
            currency = FFDB.db.Account.get(code=self.code).currency
            if currency is None:
                return None
            else:
                return Currency(currency)


class VoucherEntry(BaseModel):
    account_code: str
    amount: PositiveFloat
    brief: str = ""


class System:

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
    def new(filename: pathlib.Path, date: datetime.date):
        FFDB.bindDatabase(filename)

        with FFDB.db_session:
            FFDB.db.MetaData(
                version='2024.11.07',
                company=filename.stem,
                date_from=first_day_of_month(date),
                date_until=last_day_of_month(date)
            )

            rmb = FFDB.db.Currency(
                name='人民币'
            )

            FFDB.db.ExchangeRate(
                currency=rmb,
                rate=1.0,
                effective_date=first_day_of_month(date)
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


            annual_profit = FFDB.db.Account.get(name='本年利润')
            annual_profit.activated = True
            annual_profit.currency = rmb

    @staticmethod
    def bindDatabase(filename: pathlib.Path):
        FFDB.bindDatabase(filename)

    @staticmethod
    def meta() -> Meta:
        with FFDB.db_session:
            return Meta(FFDB.db.MetaData.get())

    @staticmethod
    def createAccount(parent_code: str,
                      code: str,
                      name: str,
                      ) -> Account:
        """"""
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
    def accounts() -> list[Account]:
        with FFDB.db_session:
            return list((Account(a) for a in FFDB.db.Account.select()))

    @staticmethod
    def setAccountCurrency(account_code: str, currency_name: str):
        with FFDB.db_session:
            account = FFDB.db.Account.get(code=account_code)
            if account.currency:
                raise IllegalOperation('A2.1/1')
            elif account.children:
                raise IllegalOperation('A2.1/4')

            currency = FFDB.db.Currency.get(name=currency_name)
            account.currency = currency

    @staticmethod
    def createCurrency(name: str) -> Currency:
        with FFDB.db_session:
            return Currency(FFDB.db.Currency(name=name))

    @staticmethod
    def currency(name: str) -> Optional[Currency]:
        with FFDB.db_session:
            currency = FFDB.db.Currency.get(name=name)
            if currency is None:
                return None
            return Currency(currency)

    @staticmethod
    def deleteCurrency(name: str):
        with FFDB.db_session:
            currency = FFDB.db.Currency.get(name=name)
            if currency.accounts:
                raise IllegalOperation('A2.1/2')
            currency.delete()

    @staticmethod
    def createExchangeRate(currency_name: str, rate: float, effective_date: datetime.date):
        if currency_name == '人民币':
            raise IllegalOperation('A2.2/1')

        with FFDB.db_session:
            currency = FFDB.db.Currency.get(name=currency_name)
            exchange_rate = FFDB.db.ExchangeRate(currency=currency,
                                        rate=rate,
                                        effective_date=first_day_of_month(effective_date))
            return ExchangeRate(exchange_rate)

    @staticmethod
    def deleteExchangeRate(currency_name: str, effective_date: datetime.date):
        with FFDB.db_session:
            currency = FFDB.db.Currency.get(name=currency_name)
            er = FFDB.db.ExchangeRate.get(currency=currency,
                                          effective_date=first_day_of_month(effective_date))
            if er.debit_entries or er.credit_entries:
                raise IllegalOperation('A2.1/3')

            er.delete()

    @staticmethod
    def exchangeRate(currency_name: str, date: datetime.date) -> Optional[ExchangeRate]:
        with FFDB.db_session:
            currency = FFDB.db.Currency.get(name=currency_name)
            er = currency.exchange_rates.select(lambda er: er.effective_date <= date).order_by(
                FFDB.db.ExchangeRate.effective_date.desc()
            ).first()
            if er is None:
                return None
            return ExchangeRate(er)

    @staticmethod
    def createVoucher(number: str, date: datetime.date, note: str='') -> 'FFDB.db.Voucher':
        with FFDB.db_session:
            voucher = FFDB.db.Voucher(number=number, date=date, note=note)
            return voucher

    @staticmethod
    def setVoucherDate(voucher_number: str, date: datetime.date):
        with FFDB.db_session:
            voucher = FFDB.db.Voucher.get(number=voucher_number)
            voucher.date = date

    @staticmethod
    def setVoucherNote(voucher_number: str, note: str):
        with FFDB.db_session:
            voucher = FFDB.db.Voucher.get(number=voucher_number)
            voucher.note = note

    @staticmethod
    def deleteVoucher(number: str):
        with FFDB.db_session:
            return FFDB.db.Voucher.get(number=number).delete()


    @staticmethod
    def updateDebitCreditEntries(voucher_number: str,
                                 debitEntries: list[VoucherEntry],
                                 creditEntries: list[VoucherEntry]):

        with FFDB.db_session:
            voucher = FFDB.db.Voucher.get(number=voucher_number)
            voucher.debit_entries.clear()
            voucher.credit_entries.clear()

            sum_debit = FloatWithPrecision(0.0)
            sum_credit = FloatWithPrecision(0.0)

            for entry in debitEntries:
                account = FFDB.db.Account.get(code=entry.account_code)
                assert account is not None
                if account.currency is None:
                    raise IllegalOperation('A2.1/1')

                currency = FFDB.db.Currency.get(name=account.currency.name)
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

                currency = FFDB.db.Currency.get(name=account.currency.name)
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






