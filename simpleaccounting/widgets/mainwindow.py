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
import datetime
from qtpy import QtWidgets, QtGui, QtCore
from simpleaccounting.app.system import System
from simpleaccounting.widgets.account import AccountWidget
from simpleaccounting.widgets.currency import CurrencyWidget
from simpleaccounting.widgets.voucher import VoucherWidget
from simpleaccounting.tools.dateutil import last_day_of_year, month_of_date
from simpleaccounting.widgets.voucheredit import YearEndCarryForwardWidget
from simpleaccounting.widgets.subsidiaryledger import SubsidiaryLedgerWidget
from simpleaccounting.widgets.voucheredit import MonthEndCarryForwardWidget
from simpleaccounting.widgets.voucheredit import VoucherEditWidget


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.action_show_accounts_window = QtWidgets.QAction(QtGui.QIcon(":/icons/accounting.png"), "科目管理")
        self.action_show_accounts_window.triggered.connect(self.on_action_showAccountsWindowTriggered)
        self.action_show_currency_window = QtWidgets.QAction(QtGui.QIcon(":/icons/dollar-taiwan.png"), "币种管理")
        self.action_show_currency_window.triggered.connect(self.on_action_showCurrencyWindowTriggered)
        self.action_show_voucher_window = QtWidgets.QAction(QtGui.QIcon(":/icons/voucher.png"), "凭证管理")
        self.action_show_voucher_window.triggered.connect(self.on_action_showVoucherWindowTriggered)
        self.toolbar.addAction(self.action_show_accounts_window)
        self.toolbar.addAction(self.action_show_currency_window)
        self.toolbar.addAction(self.action_show_voucher_window)
        self.mdi_area = QtWidgets.QMdiArea()
        self.addToolBar(self.toolbar)
        self.setCentralWidget(self.mdi_area)
        self.account_widget = AccountWidget()
        self.account_sub_window = QtWidgets.QMdiSubWindow()
        self.account_sub_window.setWidget(self.account_widget)
        self.account_sub_window.setWindowIcon(QtGui.QIcon(":/icons/accounting.png"))
        self.currency_widget = CurrencyWidget()
        self.currency_sub_window = QtWidgets.QMdiSubWindow()
        self.currency_sub_window.setWidget(self.currency_widget)
        self.currency_sub_window.setWindowIcon(QtGui.QIcon(":/icons/dollar-taiwan.png"))
        self.voucher_widget = VoucherWidget()
        self.voucher_widget.signal_voucher_edit_requested.connect(self.on_voucherEditRequested)
        self.voucher_widget.signal_mecf_requested.connect(self.on_mecfRequested)
        self.voucher_widget.signal_yecf_requested.connect(self.on_yecfRequested)
        self.voucher_widget.signal_subsidiary_ledger_requested.connect(self.on_subsidiaryLedgerRequested)
        self.voucher_sub_window = QtWidgets.QMdiSubWindow()
        self.voucher_sub_window.setWidget(self.voucher_widget)
        self.voucher_sub_window.setWindowIcon(QtGui.QIcon(":/icons/voucher.png"))

        self.mdi_area.addSubWindow(self.account_sub_window)
        self.mdi_area.addSubWindow(self.currency_sub_window)
        self.mdi_area.addSubWindow(self.voucher_sub_window)
        self.voucher_viewer_sub_window: QtWidgets.QMdiSubWindow = None

    def enterVoucherEditMode(self):
        self.account_sub_window.setEnabled(False)
        self.currency_sub_window.setEnabled(False)
        self.voucher_sub_window.setEnabled(False)

    def quitVoucherEditMode(self):
        try:
            self.account_sub_window.setEnabled(True)
            self.currency_sub_window.setEnabled(True)
            self.voucher_sub_window.setEnabled(True)
        except Exception:
            ...

    def on_voucherEditRequested(self, date: datetime.date):
        self.enterVoucherEditMode()
        sub_window: QtWidgets.QMdiSubWindow = self.mdi_area.addSubWindow(VoucherEditWidget(date))
        sub_window.setWindowTitle(f'凭证录入 - {date.strftime("%Y年%m月")}')
        sub_window.show()
        sub_window.resize(1600, 600)
        sub_window.move(20, 20)
        sub_window.destroyed.connect(lambda *args: self.quitVoucherEditMode())

    def on_mecfRequested(self, date: datetime.date):
        self.enterVoucherEditMode()
        sub_window: QtWidgets.QMdiSubWindow = self.mdi_area.addSubWindow(MonthEndCarryForwardWidget(date))
        sub_window.setWindowTitle(f'月末结转凭证 - {date.strftime("%Y年%m月")}')
        sub_window.show()
        sub_window.resize(1600, 600)
        sub_window.move(20, 20)
        sub_window.destroyed.connect(lambda *args: self.quitVoucherEditMode())

    def on_yecfRequested(self, date: datetime.date):
        self.enterVoucherEditMode()
        sub_window: QtWidgets.QMdiSubWindow = self.mdi_area.addSubWindow(
            YearEndCarryForwardWidget(last_day_of_year(datetime.date(date.year - 1, date.month, date.day)))
        )
        sub_window.setWindowTitle(f'往年结转凭证 - {date.strftime("%Y年")}')
        sub_window.show()
        sub_window.resize(1600, 600)
        sub_window.move(20, 20)
        sub_window.destroyed.connect(lambda *args: self.quitVoucherEditMode())

    def on_subsidiaryLedgerRequested(self):
        self.enterVoucherEditMode()
        subsidiary_ledger_widget = SubsidiaryLedgerWidget()
        subsidiary_ledger_widget.signal_view_voucher.connect(self.on_viewVoucher)
        sub_window: QtWidgets.QMdiSubWindow = self.mdi_area.addSubWindow(
            subsidiary_ledger_widget
        )
        sub_window.show()
        sub_window.resize(1600, 600)
        sub_window.move(20, 20)
        sub_window.destroyed.connect(self.on_subsidiaryLedgerWindowDestroyed)

    def updateUI(self):
        meta = System.meta()
        self.setWindowTitle(f"{meta.company} "
                            f"{meta.month_from.strftime('%Y年%m月')}-{meta.month_until.strftime('%Y年%m月')}")

    def on_viewVoucher(self, date: datetime.date, voucher_number: str):
        if self.voucher_viewer_sub_window is None:
            viewer = VoucherEditWidget(month_of_date(date))
            viewer.setCurrentVoucher(voucher_number)
            viewer.setReadOnly(True)
            sub_window = self.mdi_area.addSubWindow(viewer)
            sub_window.destroyed.connect(self.on_voucherViewerSubWindowDestroyed)
            sub_window.show()
            sub_window.resize(1600, 600)
            self.voucher_viewer_sub_window = sub_window
        else:
            self.voucher_viewer_sub_window.widget().setDateMonth(month_of_date(date))
            self.voucher_viewer_sub_window.widget().setCurrentVoucher(voucher_number)

    def on_voucherViewerSubWindowDestroyed(self):
        self.voucher_viewer_sub_window = None

    def on_subsidiaryLedgerWindowDestroyed(self):
        if self.voucher_viewer_sub_window:
            self.voucher_viewer_sub_window.close()
            self.voucher_viewer_sub_window = None
        #
        self.quitVoucherEditMode()

    def on_action_showAccountsWindowTriggered(self):
        self.account_widget.show()

    def on_action_showCurrencyWindowTriggered(self):
        self.currency_widget.show()

    def on_action_showVoucherWindowTriggered(self):
        self.voucher_widget.show()
