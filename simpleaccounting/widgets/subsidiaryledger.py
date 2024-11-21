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
from simpleaccounting.tools.dateutil import last_day_of_month, first_day_of_month
from simpleaccounting.widgets.qwidgets import CustomQDialog, HorizontalSpacer
from simpleaccounting.tools.mymath import FloatWithPrecision


COLUMNS = ["日期", "凭证记字号", "摘要", "科目名称", "借方币种金额", "贷方币种金额", "币种", "汇率", "借方金额", "贷方金额", "标签"]
COLUMNS_WIDTH = [12, 12, 20, 20, 12, 12, 6, 8, 12, 12, 6]
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
            if i in [COLUMN_DEBIT_CURRENCY_AMOUNT, COLUMN_CREDIT_CURRENCY_AMOUNT,
                     COLUMN_DEBIT_LOCAL_AMOUNT, COLUMN_CREDIT_LOCAL_AMOUNT,
                     COLUMN_CURRENCY, COLUMN_EXCHANGE_RATE]:
                item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
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


class SubsidiaryLedgerDialog(CustomQDialog):

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
        self.tb_choose_account = QtWidgets.QToolButton(self)
        self.tb_choose_account.setStyleSheet('background-color: transparent')
        self.tb_choose_account.setIcon(QtGui.QIcon(":/icons/FindNavigatorSearch(Color).svg"))
        self.tb_choose_account.setParent(self.cbox_account)
        self.tb_choose_account.move(self.cbox_account.rect().topRight() - QtCore.QPoint(60, 0))
        self.de_from = QtWidgets.QDateEdit(self)
        self.de_until = QtWidgets.QDateEdit(self)
        self.table = SubsidaryLedgerTableWidget()
        self.action_pull = QtWidgets.QAction(QtGui.QIcon(":/icons/persistenceEntity.svg"), "拉取", self)
        self.action_pull.triggered.connect(self.on_actionPullTriggered)

        self.tbar = QtWidgets.QToolBar(self)
        self.tbar.addWidget(HorizontalSpacer())
        container = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout(container)
        hbox.addWidget(QtWidgets.QLabel("科目"))
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
        self.de_from.setDateRange(
            first_day_of_month(System.meta().month_from),
            last_day_of_month(System.meta().month_until)
        )
        self.cbox_account.clear()
        for account in System.accounts():
            self.cbox_account.addItem(f"{account.code} {account.name}", account)
        # 1for
        self.tb_choose_account.move(self.cbox_account.rect().topRight() - QtCore.QPoint(60, 0))
        self.tb_choose_account.resizeEvent()

    def on_actionPullTriggered(self):
        ...

