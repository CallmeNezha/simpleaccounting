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
from qtpy import QtWidgets, QtCore, QtGui
from simpleaccounting.app.system import System
from simpleaccounting.tools.dateutil import last_day_of_month, first_day_of_month, month_of_date
from simpleaccounting.widgets.qwidgets import CustomQDialog, HorizontalSpacer
from simpleaccounting.tools.mymath import FloatWithPrecision
from simpleaccounting.tools import stringscores
from simpleaccounting.widgets.voucheredit import VoucherEditWidget, AccountSelectDialog


COLUMN_DATE= 0
COLUMN_VOUCHER_NUMBER = 1
COLUMN_BRIEF = 2
COLUMN_ACCOUNT = 3
COLUMN_DEBIT_CURRENCY_AMOUNT = 4
COLUMN_CREDIT_CURRENCY_AMOUNT = 5
COLUMN_CURRENCY = 6
COLUMN_EXCHANGE_RATE = 7
COLUMN_DEBIT_LOCAL_AMOUNT = 8
COLUMN_CREDIT_LOCAL_AMOUNT = 9
COLUMN_TAG = 10
COLUMN_COUNT = 11

COLUMNS = ["日期", "凭证记字号", "摘要", "科目名称", "借方币种金额", "贷方币种金额", "币种", "汇率", "借方金额", "贷方金额", "标签"]
COLUMNS_WIDTH = [12, 20, 20, 20, 12, 12, 8, 8, 12, 12, 6]


class SubsidaryLedgerTableWidget(QtWidgets.QTableWidget):
    """"""
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWordWrap(True)
        self.setAlternatingRowColors(True)
        self.setColumnCount(COLUMN_COUNT)
        self.setHorizontalHeaderLabels(COLUMNS)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.clear()

    def resizeEvent(self, *args, **kwargs):
        """"""
        for i in range(COLUMN_COUNT):
            width = self.fontMetrics().horizontalAdvance("9"*COLUMNS_WIDTH[i])
            self.setColumnWidth(i, width)
        # !for
        super().resizeEvent(*args, **kwargs)
        # 调整表格宽度变化时的行高
        self.resizeRowsToContents()

    def clear(self):
        super().clear()
        self.setHorizontalHeaderLabels(COLUMNS)
        super().setRowCount(0)
        self.insertRow(0)

        row_last = self.rowCount() - 1
        for i in range(COLUMN_COUNT):
            item = QtWidgets.QTableWidgetItem()
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            item.setBackground(QtGui.QColor("#1e58ff"))
            item.setForeground(QtGui.QColor("#ffffff"))
            self.setItem(row_last, i, item)
            if i == COLUMN_BRIEF:
                item.setText("合计")
            elif i in [COLUMN_DEBIT_LOCAL_AMOUNT, COLUMN_CREDIT_LOCAL_AMOUNT]:
                item.setText(str(FloatWithPrecision(0.0)))

    def insertRow(self, row: int):
        super().insertRow(row)
        for i in range(COLUMN_COUNT):
            item = QtWidgets.QTableWidgetItem()
            if i in [COLUMN_CURRENCY]:
                item.setTextAlignment(QtCore.Qt.AlignHCenter)
            else:
                item.setTextAlignment(QtCore.Qt.AlignRight)
            #
            if i == COLUMN_VOUCHER_NUMBER:
                font: QtGui.QFont = item.font()
                font.setUnderline(True)
                item.setFont(font)
                item.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 255)))
            if i == COLUMN_ACCOUNT:
                item.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 255)))
            #
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.setItem(row, i, item)

    def removeRow(self, row: int):
        if row == self.rowCount() - 1:
            return
        super().removeRow(row)

    def setRowCount(self, rows: int):
        self.clear()
        for _ in range(max(0, rows)):
            self.insertRow(0)


class SubsidiaryLedgerWidget(QtWidgets.QWidget):

    signal_view_voucher = QtCore.Signal(datetime.date, str)

    def __init__(self):
        super().__init__()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        self.setWindowTitle("明细账")
        self.cbox_account = QtWidgets.QComboBox(self)
        self.cbox_account.setMinimumHeight(int(self.fontMetrics().height() * 1.8))
        self.cbox_account.setMinimumWidth(int(self.fontMetrics().horizontalAdvance('x' * 20)))
        self.cbox_account.setEditable(True)
        self.cbox_account.lineEdit().editingFinished.connect(self.on_cbox_accountEditingFinished)
        self.tb_choose_account = QtWidgets.QToolButton(self)
        self.tb_choose_account.setStyleSheet('background-color: transparent')
        self.tb_choose_account.setIcon(QtGui.QIcon(":/icons/FindNavigatorSearch(Color).svg"))
        self.tb_choose_account.clicked.connect(self.on_tb_chooseAccountTriggered)
        self.de_from = QtWidgets.QDateEdit(self)
        self.de_until = QtWidgets.QDateEdit(self)
        self.table = SubsidaryLedgerTableWidget()
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.on_tableItemDoubleClicked)
        self.action_pull = QtWidgets.QAction(QtGui.QIcon(":/icons/persistenceEntity.svg"), "拉取", self)
        self.action_pull.triggered.connect(self.on_actionPullTriggered)
        self.action_print = QtWidgets.QAction(QtGui.QIcon(":/icons/print.svg"), "打印", self)
        self.action_print.triggered.connect(self.on_actionPrintTriggered)
        self.action_print.setShortcut(QtGui.QKeySequence('Ctrl+P'))
        self.action_print.setToolTip('Ctrl+P')
        #
        self.tbar = QtWidgets.QToolBar(self)
        self.tbar.addAction(self.action_print)
        self.tbar.addWidget(HorizontalSpacer())
        container = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout(container)
        hbox.addWidget(QtWidgets.QLabel("科目"))
        hbox.addWidget(self.tb_choose_account)
        hbox.addWidget(self.cbox_account)
        hbox.addWidget(QtWidgets.QLabel("起始日期"))
        hbox.addWidget(self.de_from)
        hbox.addWidget(QtWidgets.QLabel("结束日期"))
        hbox.addWidget(self.de_until)
        self.tbar.addWidget(container)
        self.tbar.addSeparator()
        self.tbar.addAction(self.action_pull)
        self.tbar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tbar)
        layout.addWidget(self.table)

    def updateUI(self):
        self.de_from.setDate(first_day_of_month(System.meta().month_from))
        self.de_until.setDate(last_day_of_month(System.meta().month_until))
        self.cbox_account.clear()
        for account in System.accounts():
            self.cbox_account.addItem(f"{account.code} {account.name}", account)
        # 1for

    def on_actionPullTriggered(self):
        """"""
        account = self.cbox_account.currentData(QtCore.Qt.UserRole)
        if not account:
            return

        date_from = datetime.date(
            self.de_from.date().year(),
            self.de_from.date().month(),
            self.de_from.date().day()
        )
        date_until = datetime.date(
            self.de_until.date().year(),
            self.de_until.date().month(),
            self.de_until.date().day()
        )

        if date_from > date_until:
            date_until, date_from = date_from, date_until

        entries = []
        for v in System.vouchers(lambda v: v.date >= date_from and v.date <= date_until):
            for entry in v.debit_entries:
                if entry.account.code.startswith(account.code):
                    entries.append(('debit', v, entry))
                # 1if
            # 1for
            for entry in v.credit_entries:
                if entry.account.code.startswith(account.code):
                    entries.append(('credit', v, entry))
                # 1if
            # 1for
        # 1for
        self.table.setRowCount(len(entries))

        for i, (direction, voucher, entry) in enumerate(entries):
            self.table.item(i, COLUMN_DATE).setText(voucher.date.strftime('%Y-%m-%d'))
            self.table.item(i, COLUMN_VOUCHER_NUMBER).setText(voucher.number)
            self.table.item(i, COLUMN_VOUCHER_NUMBER).setData(
                QtCore.Qt.UserRole,
                voucher
            )
            self.table.item(i, COLUMN_BRIEF).setText(entry.brief)
            self.table.item(i, COLUMN_ACCOUNT).setText(entry.account.qualname)
            self.table.item(i, COLUMN_CURRENCY).setText(entry.currency)
            self.table.item(i, COLUMN_EXCHANGE_RATE).setText(str(entry.exchange_rate))
            if direction == 'debit':
                self.table.item(i, COLUMN_DEBIT_CURRENCY_AMOUNT).setText(str(entry.amount))
                self.table.item(i, COLUMN_DEBIT_LOCAL_AMOUNT).setText(
                    str(entry.amount * entry.exchange_rate)
                )
                self.table.item(i, COLUMN_DEBIT_LOCAL_AMOUNT).setData(
                    QtCore.Qt.ItemDataRole.UserRole,
                    entry.amount * entry.exchange_rate
                )
            else:
                self.table.item(i, COLUMN_CREDIT_CURRENCY_AMOUNT).setText(str(entry.amount))
                self.table.item(i, COLUMN_CREDIT_LOCAL_AMOUNT).setText(
                    str(entry.amount * entry.exchange_rate)
                )
                self.table.item(i, COLUMN_CREDIT_LOCAL_AMOUNT).setData(
                    QtCore.Qt.ItemDataRole.UserRole,
                    entry.amount * entry.exchange_rate
                )

        self.table.resizeRowsToContents()
        self.setWindowTitle(f"明细账 - {account.qualname } - {date_from.strftime('%Y年%m月%d日')}至{date_until.strftime('%Y年%m月%d日')}")
        self.refreshDebitCreditTotal()

    def refreshDebitCreditTotal(self):
        debit_total = FloatWithPrecision(0.0)
        credit_total = FloatWithPrecision(0.0)
        last_row = self.table.rowCount() - 1
        for row in range(last_row):
            debit_currency_amount = self.table.item(row, COLUMN_DEBIT_LOCAL_AMOUNT).data(QtCore.Qt.ItemDataRole.UserRole)
            credit_currency_amount = self.table.item(row, COLUMN_CREDIT_LOCAL_AMOUNT).data(QtCore.Qt.ItemDataRole.UserRole)
            if debit_currency_amount:
                debit_total += debit_currency_amount
            if credit_currency_amount:
                credit_total += credit_currency_amount
        # 1for
        self.table.item(last_row, COLUMN_DEBIT_LOCAL_AMOUNT).setText(str(debit_total))
        self.table.item(last_row, COLUMN_DEBIT_LOCAL_AMOUNT).setData(QtCore.Qt.ItemDataRole.UserRole, debit_total)
        self.table.item(last_row, COLUMN_CREDIT_LOCAL_AMOUNT).setText(str(credit_total))
        self.table.item(last_row, COLUMN_CREDIT_LOCAL_AMOUNT).setData(QtCore.Qt.ItemDataRole.UserRole, credit_total)

    def on_cbox_accountEditingFinished(self):
        editedText = self.cbox_account.lineEdit().text()
        # To prevent the text entered in a QComboBox's QLineEdit from being added to the list of items
        for i in reversed(range(self.cbox_account.count())):
            if self.cbox_account.itemData(i, QtCore.Qt.UserRole) is None:
                self.cbox_account.removeItem(i)
        # 1To
        accounts = [self.cbox_account.itemData(i, QtCore.Qt.UserRole) for i in range(self.cbox_account.count())]

        rets = stringscores.findMatchingChoices(
            editedText,
            [f"{a.code} {a.name}" for a in accounts],
            template='<b>{0}</b>',
            valid_only=True,
            sort=True
        )
        if rets:
            name, named, _ = rets[0]
            index = next((i for i, a in enumerate(accounts) if f"{a.code} {a.name}" == name), None)
            self.cbox_account.setCurrentIndex(index) if index else ...
        else:
            self.cbox_account.setCurrentIndex(0)

    def on_tb_chooseAccountTriggered(self):
        def on_accept(account):
            accounts = [self.cbox_account.itemData(i, QtCore.Qt.UserRole) for i in range(self.cbox_account.count())]
            index = next((i for i, a in enumerate(accounts) if a.code == account.code), None)
            self.cbox_account.setCurrentIndex(index) if index != -1 else ...
            return True
        #
        AccountSelectDialog(on_accept).exec_()

    def on_tableItemDoubleClicked(self, item: QtWidgets.QTableWidgetItem):
        if item.column() == COLUMN_VOUCHER_NUMBER:
            voucher = item.data(QtCore.Qt.UserRole)
            if voucher:
                self.signal_view_voucher.emit(voucher.date, voucher.number)

    def on_actionPrintTriggered(self):
        print("打印明细账")


