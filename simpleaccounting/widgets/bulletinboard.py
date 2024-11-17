"""
    Copyright 2024- ZiJian Jiang

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

from qtpy import QtWidgets
from simpleaccounting.app.system import System
from simpleaccounting.tools.dateutil import months_between
from simpleaccounting.widgets.qwidgets import CustomQDialog


class BulletinBoardDialog(CustomQDialog):

    def __init__(self):
        super().__init__()
        self.setupUI()
        meta = System.meta()
        self.label_version_db.setText(meta.version)
        self.label_company.setText(meta.company)
        self.label_date_from.setText(meta.month_from.strftime('%Y.%m'))
        self.label_date_until.setText(meta.month_until.strftime('%Y.%m'))
        self.label_months.setText(str(months_between(meta.month_from, meta.month_until)))

    def setupUI(self):
        #
        self.btn_currency = QtWidgets.QPushButton("货币汇率")
        self.btn_currency.clicked.connect(self.showCurrencyMgmtWindow)
        self.btn_account = QtWidgets.QPushButton("科目管理")
        self.btn_account.clicked.connect(self.showAccountMgmtWindow)
        self.btn_voucher = QtWidgets.QPushButton("记账凭证")
        self.btn_voucher.clicked.connect(self.showVoucherMgmtWindow)

        self.label_version_db = QtWidgets.QLabel()
        self.label_company = QtWidgets.QLabel()
        self.label_date_until = QtWidgets.QLabel()
        self.label_date_from = QtWidgets.QLabel()
        self.label_months = QtWidgets.QLabel()

        self.btn_detailed_ledger = QtWidgets.QPushButton("【Excel】明细账")
        self.btn_detailed_ledger.clicked.connect(self.exportDetailedLedgerToExcel)

        grid = QtWidgets.QGridLayout(self)
        gbox = QtWidgets.QGroupBox("账套信息")
        form = QtWidgets.QFormLayout(gbox)
        form.addRow("数据库版本", self.label_version_db)
        form.addRow("公司名称", self.label_company)
        form.addRow("当前日期", self.label_date_until)
        form.addRow("起始日期", self.label_date_from)
        form.addRow("共计月份", self.label_months)

        grid.addWidget(gbox, 0, 0, 4, 1)
        grid.addWidget(self.btn_currency, 0, 1)
        grid.addWidget(self.btn_account, 1, 1)
        grid.addWidget(self.btn_voucher, 2, 1)
        grid.addWidget(self.btn_detailed_ledger, 3, 1)
        grid.setColumnStretch(0, 10)
        self.resize(600, -1)

    def showAccountMgmtWindow(self):
        from simpleaccounting.widgets.account import AccountDialog
        dialog = AccountDialog()
        dialog.resize(600, 600)
        dialog.exec_()

    def showCurrencyMgmtWindow(self):
        from simpleaccounting.widgets.currency import CurrencyDialog
        dialog = CurrencyDialog()
        dialog.resize(600, 600)
        dialog.exec_()

    def showVoucherMgmtWindow(self):
        from simpleaccounting.widgets.voucher import VoucherDialog
        dialog = VoucherDialog()
        dialog.resize(600, 300)
        dialog.exec_()

    def exportDetailedLedgerToExcel(self):
        ...
        # dialog = DetailedLedgerSelectingDialog()
        # dialog.resize(600, 300)
        # dialog.exec_()