
import pytest
import datetime
import pathlib

from pony.orm import DatabaseSessionIsOver
from simplefinance.app.system import System, IllegalOperation, VoucherEntry


class TestSystem:

    @pytest.fixture(scope='function', autouse=True)
    def new_book(self, tmpdir_factory):
        System.new(pathlib.Path(tmpdir_factory.mktemp('db').join('test.sqlite')), datetime.date(1999, 12, 1))

    def test_account_A1_1S1(self):
        # A1.1/2
        System.createAccount('1002.01',
                             '1002.01.01',
                             'xxx')

        with pytest.raises(IllegalOperation, match='A1.1/2'):
            System.createAccount('1002.01',
                                 '1002.01.01',
                                 'yyy')

    def test_account_A1_1S5(self):
        # A1.1/5
        with pytest.raises(IllegalOperation, match='A1.1/5'):
            System.deleteAccount('1002.01')

    def test_account_A1_2_1S1(self):
        # A1.2.1/1
        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')
        System.createAccount('1002',
                             '1002.05',
                             'yyy')

    def test_account_A1_2_1S2(self):
        # A1.2.1/2
        with pytest.raises(IllegalOperation, match='A1.2.1.2/1'):
            System.createAccount('',
                                 '1002.02.05',
                                 'xxx')

    def test_account_A1_2_1S3(self):
        # A1.2.1/3
        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')
        System.setAccountCurrency('1002.01.05', '人民币')

        with pytest.raises(IllegalOperation):
            System.setAccountCurrency('1002.01', '人民币')

    def test_account_A1_2_1S4(self):
        # A1.2.1/4
        with pytest.raises(IllegalOperation, match='A1.2.1/4'):
            System.setAccountCurrency('1002.01', '人民币')
            System.createAccount(
                '1002.01',
                '1002.01.05',
                'xxx'
            )

    def test_account_A1_2_1S5(self):
        # A1.2.1/5
        with pytest.raises(IllegalOperation, match='A1.2.1/5'):
            System.createAccount(
                '1002.01',
                '1002.01.05',
                'xxx'
            )
            System.setAccountCurrency('1002.01.05', '人民币')
            System.deleteAccount('1002.01.05')

    def test_account_A1_2_1S8(self):
        System.createAccount('1002.01',
                             '1002.01.01',
                             'xxx')

        with pytest.raises(IllegalOperation, match='A1.2.1/8'):
            System.createAccount('1002.01',
                                 '1002.01.01',
                                 'xxx')

    def test_account_A1_2_1S10(self):
        System.createAccount('1002.01',
                             '1002.01.01',
                             'xxx')

        assert System.account('1002.01.01').direction == System.account('1002.01').direction

    def test_account_A1_2_1S11(self):
        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')
        account = System.account('1002.01.05')
        assert account.name == 'xxx'
        account.name = 'xxxyyy'
        assert System.account('1002.01.05').name == 'xxx'

        assert account.direction == '借'
        account.direction = '贷'
        assert System.account('1002.01.05').direction == '借'


    def test_account_A1_2_1_1S2(self):
        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')
        account = System.account('1002.01.05')
        assert account.qualname == '银行存款/基本存款账户/xxx'
        assert account.parent.qualname == '银行存款/基本存款账户'

    def test_account_A1_2_1_2S1(self):
        with pytest.raises(IllegalOperation):
            System.createAccount('1002.01',
                                 '1002.02.05',
                                 'xxx')

        with pytest.raises(IllegalOperation):
            System.createAccount('1002.01',
                                 '1002.03',
                                 'xxx')

        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')

        account = System.account('1002.01.05')
        assert account.name == 'xxx'

    def test_account_A2_1S1(self):
        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')
        System.createCurrency('美元')
        System.setAccountCurrency('1002.01.05', '人民币')

        with pytest.raises(IllegalOperation, match='A2.1/1'):
            System.setAccountCurrency('1002.01.05', '美元')

    def test_account_A2_1S2(self):
        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')
        System.createCurrency('美元')
        System.setAccountCurrency('1002.01.05', '美元')

        with pytest.raises(IllegalOperation, match='A2.1/2'):
            System.deleteCurrency('美元')

    def test_account_A2_1S3(self):
        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')
        System.createCurrency('美元')
        System.createExchangeRate('美元', 8.0, datetime.date(2000, 1, 1))
        System.setAccountCurrency('1002.01.05', '美元')
        System.setAccountCurrency('1002.02', '人民币')
        System.createVoucher('test/001', datetime.date(2000, 1, 1))
        System.updateDebitCreditEntries(
            'test/001',
            [VoucherEntry(account_code='1002.01.05', amount=100.0)],
            [VoucherEntry(account_code='1002.02', amount=800.0)]
        )

        with pytest.raises(IllegalOperation, match='A2.1/3'):
            System.deleteExchangeRate('美元', datetime.date(2000, 1, 1))

    def test_account_A2_1S4(self):
        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')
        with pytest.raises(IllegalOperation, match='A2.1/4'):
            System.setAccountCurrency('1002.01', '人民币')

    def test_account_A2_2S1(self):
        assert System.exchangeRate('人民币', datetime.date.today()).rate == 1.0

        with pytest.raises(IllegalOperation, match='A2.2/1'):
            System.createExchangeRate('人民币', 8.0, datetime.date(2000, 1, 1))

    def test_account_A2_2S2(self):
        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')
        System.createCurrency('美元')
        System.createExchangeRate('美元', 8.0, datetime.date(2000, 1, 1))
        System.setAccountCurrency('1002.01.05', '美元')
        System.setAccountCurrency('1002.02', '人民币')
        System.createVoucher('test/001', datetime.date(2000, 1, 1))
        System.updateDebitCreditEntries(
            'test/001',
            [VoucherEntry(account_code='1002.01.05', amount=100.0)],
            [VoucherEntry(account_code='1002.02', amount=800.0)]
        )

    def test_account_A2_2S3(self):
        System.createCurrency('美元')
        System.createExchangeRate('美元', 8.0, datetime.date(2000, 1, 1))
        System.createExchangeRate('美元', 7.0, datetime.date(2024, 1, 1))
        assert System.exchangeRate('美元', datetime.date(2000, 12, 31)).rate == 8.0
        assert System.exchangeRate('美元', datetime.date(2024, 2, 1)).rate == 7.0

    def test_account_A2_2S4(self):
        System.createCurrency('美元')
        System.createExchangeRate('美元', 8.0, datetime.date(2000, 1, 1))
        System.createExchangeRate('美元', 7.0, datetime.date(2024, 1, 15))
        assert System.exchangeRate('美元', datetime.date(2000, 12, 31)).rate == 8.0
        assert System.exchangeRate('美元', datetime.date(2024, 1, 1)).rate == 7.0

    def test_account_A3_2S1(self):
        with pytest.raises(IllegalOperation, match='A2.2/1'):
            System.createExchangeRate('人民币', 8.0, datetime.date(2000, 1, 1))

    def test_account_A3_2S2(self):
        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')
        System.createCurrency('美元')
        System.createExchangeRate('美元', 8.0, datetime.date(2000, 1, 1))
        System.setAccountCurrency('1002.01.05', '美元')
        System.setAccountCurrency('1002.02', '人民币')
        System.createVoucher('test/001', datetime.date(2000, 1, 1))

        with pytest.raises(IllegalOperation, match='A3.2/2'):
            System.updateDebitCreditEntries(
                'test/001',
                [VoucherEntry(account_code='1002.01.05', amount=100.0)],
                [VoucherEntry(account_code='1002.02', amount=700.0)]
            )

    def test_account_A3_2S3(self):
        System.createAccount('1002.01',
                             '1002.01.05',
                             'xxx')
        System.createCurrency('美元')
        System.createExchangeRate('美元', 8.0, datetime.date(2000, 1, 1))
        System.createExchangeRate('美元', 7.0, datetime.date(2000, 2, 1))
        System.setAccountCurrency('1002.01.05', '美元')
        System.setAccountCurrency('1002.02', '人民币')
        System.createVoucher('test/001', datetime.date(2000, 1, 1))
        System.updateDebitCreditEntries(
            'test/001',
            [VoucherEntry(account_code='1002.01.05', amount=100.0)],
            [VoucherEntry(account_code='1002.02', amount=800.0)]
        )

        System.createVoucher('test/002', datetime.date(2000, 2, 15))
        System.updateDebitCreditEntries(
            'test/002',
            [VoucherEntry(account_code='1002.01.05', amount=100.0)],
            [VoucherEntry(account_code='1002.02', amount=700.0)]
        )
