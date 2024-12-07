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

from qtpy import QtWidgets, QtCore, QtGui

from simpleaccounting.app.system import System
from simpleaccounting.tools.dateutil import last_day_of_month, qdate_to_date, first_day_of_month
from simpleaccounting.widgets.qwidgets import HorizontalSpacer
from simpleaccounting.widgets.freezabletableview import FreezableTableView

COLUMN_ACCOUNT_CODE = 0
COLUMN_ACCOUNT_NAME = 1
COLUMN_BEGINNING_DEBIT_CURRENCY = 2
COLUMN_BEGINNING_DEBIT_LOCAL = 3
COLUMN_BEGINNING_CREDIT_CURRENCY = 4
COLUMN_BEGINNING_CREDIT_LOCAL = 5
COLUMN_INCURRED_DEBIT_CURRENCY = 6
COLUMN_INCURRED_DEBIT_LOCAL = 7
COLUMN_INCURRED_CREDIT_CURRENCY = 8
COLUMN_INCURRED_CREDIT_LOCAL = 9
COLUMN_ENDING_DEBIT_CURRENCY = 10
COLUMN_ENDING_DEBIT_LOCAL = 11
COLUMN_ENDING_CREDIT_CURRENCY = 12
COLUMN_ENDING_CREDIT_LOCAL = 13
COLUMN_COUNT = 14

HORIZONTAL_HEADERS_ROW1 = [('科目', 2), ('期初余额', 4), ('本期发生额', 4), ('期末余额', 4)]
HORIZONTAL_HEADERS_ROW2 = [('代码', 1), ('名称', 1),
                           *[('借方（币种）', 1), ('借方（本位币）', 1), ('贷方（币种）', 1), ('贷方（本位币）', 1)] * 3]


class EndingBalanceWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setupUI()
        self.updateUI()
        self.setCurrencyVisible(False)

    def setupUI(self):
        self.setWindowTitle("发生额及余额")
        self.de_begin = QtWidgets.QDateEdit(first_day_of_month(System.meta().month_until))
        self.de_end = QtWidgets.QDateEdit(last_day_of_month(System.meta().month_until))
        self.model = QtGui.QStandardItemModel()
        self.table = FreezableTableView(self.model)
        self.tbar = QtWidgets.QToolBar()
        self.tbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.action_currency_visible = QtWidgets.QAction(QtGui.QIcon(":/icons/dollar-yuan-exchange.png"), "币种", self)
        self.action_currency_visible.setCheckable(True)
        self.action_currency_visible.toggled.connect(self.setCurrencyVisible)
        self.action_pull = QtWidgets.QAction(QtGui.QIcon(":/icons/persistenceEntity.svg"), "拉取", self)
        self.action_pull.triggered.connect(self.on_action_pullTriggered)
        self.action_level_1 = QtWidgets.QAction(QtGui.QIcon(":/icons/1.png"), "一级", self)
        self.action_level_1.triggered.connect(self.on_action_level1Triggered)
        self.action_level_2 = QtWidgets.QAction(QtGui.QIcon(":/icons/2.png"), "二级", self)
        self.action_level_2.triggered.connect(self.on_action_level2Triggered)
        self.action_level_3 = QtWidgets.QAction(QtGui.QIcon(":/icons/3.png"), "三级以下", self)
        self.action_level_3.triggered.connect(self.on_action_level3Triggered)

        container = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout(container)
        hbox.addWidget(QtWidgets.QLabel("起始日期"))
        hbox.addWidget(self.de_begin)
        hbox.addWidget(QtWidgets.QLabel("结束日期"))
        hbox.addWidget(self.de_end)
        self.tbar.addWidget(HorizontalSpacer())
        self.tbar.addWidget(container)
        self.tbar.addSeparator()
        self.tbar.addAction(self.action_currency_visible)
        self.tbar.addSeparator()
        self.tbar.addAction(self.action_level_1)
        self.tbar.addAction(self.action_level_2)
        self.tbar.addAction(self.action_level_3)
        self.tbar.addSeparator()
        self.tbar.addAction(self.action_pull)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.tbar)
        vbox.addWidget(self.table)

    def headerLabels(self, num_columns: int):
        def number_to_excel_columns(n):
            columns = []
            while n > 0:
                n -= 1  # 让数字从 0 开始计数
                columns.append(chr(n % 26 + ord('A')))  # 计算当前字符
                n //= 26  # 对列数进行整除，处理进位
            return ''.join(columns[::-1])  # 反转字符顺序

        return [number_to_excel_columns(i + 1) for i in range(num_columns)]

    def setCurrencyVisible(self, b: bool):
        for col in [COLUMN_BEGINNING_DEBIT_CURRENCY, COLUMN_BEGINNING_CREDIT_CURRENCY,
                    COLUMN_ENDING_DEBIT_CURRENCY, COLUMN_ENDING_CREDIT_CURRENCY,
                    COLUMN_INCURRED_DEBIT_CURRENCY, COLUMN_INCURRED_CREDIT_CURRENCY]:
            self.table.setColumnHidden(col, not b)

    def updateUI(self):
        self.model.clear()
        self.model.setColumnCount(COLUMN_COUNT)
        self.model.setHorizontalHeaderLabels(self.headerLabels(COLUMN_COUNT))
        col = 0
        for header, span in HORIZONTAL_HEADERS_ROW1:
            item = QtGui.QStandardItem()
            item.setText(header)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.model.setItem(0, col, item)
            self.table.setSpan(0, col, 1, span)
            col += span

        col = 0
        for header, span in HORIZONTAL_HEADERS_ROW2:
            item = QtGui.QStandardItem()
            item.setText(header)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.model.setItem(1, col, item)
            self.table.setSpan(1, col, 1, span)
            col += span

        font_bold = self.font()
        font_bold.setBold(True)
        for r, account in enumerate(System.accounts()):
            r = r + 2  # first two header row
            item = QtGui.QStandardItem(account.code)
            if account.children:
                item.setFont(font_bold)
            self.model.setItem(r, COLUMN_ACCOUNT_CODE, item)
            item = QtGui.QStandardItem(account.name)
            if account.children:
                item.setFont(font_bold)
            self.model.setItem(r, COLUMN_ACCOUNT_NAME, item)
        # 1for
        self.table.freezeToRow(2)
        self.setCurrencyVisible(self.action_currency_visible.isChecked())

    def on_action_pullTriggered(self):

        class AlignRightStandardItem(QtGui.QStandardItem):
            def __init__(self, text: str, bold=False):
                super().__init__(text)
                self.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.setBold(bold)

            def setBold(self, b: bool):
                font = self.font()
                font.setBold(b)
                self.setFont(font)

        self.updateUI()

        pre = qdate_to_date(self.de_begin.date())
        cur = qdate_to_date(self.de_end.date())

        for r, account in enumerate(System.accounts()):
            r = r + 2  # first two header row
            bold = bool(account.children)
            (begin_amount, begin_local_amount,
             incurred_debit_sum, incurred_debit_sum_local,
             incurred_credit_sum, incurred_credit_sum_local,
             end_amount, end_local_amount) = System.incurredBalances(account.code, pre, cur)
            # --- beginning balance
            if begin_amount and begin_amount > 0.0:
                self.model.setItem(r, COLUMN_BEGINNING_DEBIT_CURRENCY, AlignRightStandardItem(str(begin_amount), bold))
            elif begin_amount and begin_amount < 0.0:
                self.model.setItem(r, COLUMN_BEGINNING_CREDIT_CURRENCY, AlignRightStandardItem(str(abs(begin_amount)), bold))
            if begin_local_amount > 0.0:
                self.model.setItem(r, COLUMN_BEGINNING_DEBIT_LOCAL, AlignRightStandardItem(str(begin_local_amount), bold))
            elif begin_local_amount < 0.0:
                self.model.setItem(r, COLUMN_BEGINNING_CREDIT_LOCAL, AlignRightStandardItem(str(abs(begin_local_amount)), bold))

            # --- incurred summary
            if incurred_debit_sum and incurred_debit_sum != 0.0:
                self.model.setItem(r, COLUMN_INCURRED_DEBIT_CURRENCY, AlignRightStandardItem(str(incurred_debit_sum), bold))
            if incurred_debit_sum_local != 0.0:
                self.model.setItem(r, COLUMN_INCURRED_DEBIT_LOCAL, AlignRightStandardItem(str(incurred_debit_sum_local), bold))
            if incurred_credit_sum and incurred_credit_sum != 0.0:
                self.model.setItem(r, COLUMN_INCURRED_CREDIT_CURRENCY, AlignRightStandardItem(str(incurred_credit_sum), bold))
            if incurred_credit_sum_local != 0.0:
                self.model.setItem(r, COLUMN_INCURRED_CREDIT_LOCAL, AlignRightStandardItem(str(incurred_credit_sum_local), bold))

            # --- ending balance
            if end_amount and end_amount > 0.0:
                self.model.setItem(r, COLUMN_ENDING_DEBIT_CURRENCY, AlignRightStandardItem(str(end_amount), bold))
            elif end_amount and end_amount < 0.0:
                self.model.setItem(r, COLUMN_ENDING_CREDIT_CURRENCY, AlignRightStandardItem(str(abs(end_amount)), bold))
            if end_local_amount > 0.0:
                self.model.setItem(r, COLUMN_ENDING_DEBIT_LOCAL, AlignRightStandardItem(str(end_local_amount), bold))
            elif end_local_amount < 0.0:
                self.model.setItem(r, COLUMN_ENDING_CREDIT_LOCAL, AlignRightStandardItem(str(abs(end_local_amount)), bold))
            #

    def on_action_level1Triggered(self):
        """"""
        for r in range(2, self.model.rowCount()):
            account_code = self.model.item(r, 0).text()
            if len(account_code.split('.')) > 1:
                self.table.hideRow(r)
            else:
                self.table.showRow(r)

    def on_action_level2Triggered(self):
        for r in range(2, self.model.rowCount()):
            account_code = self.model.item(r, 0).text()
            if len(account_code.split('.')) > 2:
                self.table.hideRow(r)
            else:
                self.table.showRow(r)

    def on_action_level3Triggered(self):
        for r in range(2, self.model.rowCount()):
            self.table.showRow(r)

