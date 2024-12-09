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
from datetime import datetime

from qtpy import QtWidgets, QtCore, QtGui

from simpleaccounting.tools.dateutil import last_day_of_month, last_day_of_year, last_day_of_previous_year, \
    qdate_to_date
from simpleaccounting.tools.mymath import FloatWithPrecision
from simpleaccounting.widgets.qwidgets import HorizontalSpacer
from simpleaccounting.app.system import System
from simpleaccounting.standards import BALANCE_SHEET_SMALL_STANDARD_2013, BALANCE_SHEET_GENERAL_STANDARD_2018

COLUMN_ASSET = 0
COLUMN_ASSET_ENDING_BALANCE = 1
COLUMN_ASSET_LAST_YEAR_ENDING_BALANCE = 2
COLUMN_DEBT = 3
COLUMN_DEBT_ENDING_BALANCE = 4
COLUMN_DEBT_LAST_YEAR_ENDING_BALANCE_BALANCE = 5
COLUMN_COUNT = 6


class BalanceSheetWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        self.setWindowTitle('资产负债表')
        self.action_edit_template = QtWidgets.QAction(QtGui.QIcon(":/icons/edit-property.png"), "编辑模板")
        self.action_edit_template.triggered.connect(self.on_action_editTemplateTriggered)
        self.action_pull = QtWidgets.QAction(QtGui.QIcon(":/icons/persistenceEntity.svg"), "拉取", self)
        self.action_pull.triggered.connect(self.on_action_pullTriggered)
        self.de_until = QtWidgets.QDateEdit()
        self.de_until.setDate(last_day_of_month(System.meta().month_until))
        # self.de_until
        container = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout(container)
        hbox.addWidget(QtWidgets.QLabel("截止日期"))
        hbox.addWidget(self.de_until)
        self.tbar = QtWidgets.QToolBar()
        self.tbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.tbar.addAction(self.action_edit_template)
        self.tbar.addWidget(HorizontalSpacer())
        self.tbar.addWidget(container)
        self.tbar.addSeparator()
        self.tbar.addAction(self.action_pull)
        # self.tbar
        self.table = QtWidgets.QTableWidget()
        self.table.verticalHeader().setHidden(True)
        self.table.setColumnCount(COLUMN_COUNT)
        self.table.setHorizontalHeaderLabels(["资产", "期末余额", "上年年末余额",
                                              "负债和所有者权益\n(或股东权益)", "期末余额", "上年年末余额"])
        self.table.setRowCount(80)
        COLUMN_WIDTHS = [30, 20, 20, 30, 20, 20]
        for i in range(len(COLUMN_WIDTHS)):
            self.table.setColumnWidth(i, self.fontMetrics().horizontalAdvance('9' * COLUMN_WIDTHS[i]))
            self.table.setColumnWidth(i, self.fontMetrics().horizontalAdvance('9' * COLUMN_WIDTHS[i]))
        # 1for
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.tbar)
        vbox.addWidget(self.table)

    def updateUI(self):
        entries = BALANCE_SHEET_SMALL_STANDARD_2013
        for i, (left, right) in enumerate(zip(entries['资产'], entries['负债和所有者权益（或股东权益）'])):
            for j in range(COLUMN_COUNT):
                item = QtWidgets.QTableWidgetItem("")
                item.setTextAlignment(QtCore.Qt.AlignRight)
                self.table.setItem(i, j, item)
                if j == COLUMN_ASSET:
                    item.setText(left[0])
                    item.setTextAlignment(QtCore.Qt.AlignLeft if left[1] is None else QtCore.Qt.AlignRight)
                elif j == COLUMN_DEBT:
                    item.setText(right[0])
                    item.setTextAlignment(QtCore.Qt.AlignLeft if right[1] is None else QtCore.Qt.AlignRight)
            # 1for
        # 1for
        self.table.resizeRowsToContents()

    def on_action_editTemplateTriggered(self):
        ...

    def on_action_pullTriggered(self):
        """"""
        date = qdate_to_date(self.de_until.date())
        self.setWindowTitle(f"{date.strftime('%Y年度')}资产负债表")
        entries = BALANCE_SHEET_SMALL_STANDARD_2013
        for i, (left, right) in enumerate(zip(entries['资产'], entries['负债和所有者权益（或股东权益）'])):
            if lineno := left[1]:
                beginning, ending = System.balance(lineno, date)
                if beginning is not None and ending is not None:
                    self.table.item(i, COLUMN_ASSET_LAST_YEAR_ENDING_BALANCE).setText(str(beginning))
                    self.table.item(i, COLUMN_ASSET_ENDING_BALANCE).setText(str(ending))

            if lineno := right[1]:
                beginning, ending = System.balance(lineno, date)
                if beginning is not None and ending is not None:
                    self.table.item(i, COLUMN_ASSET_LAST_YEAR_ENDING_BALANCE).setText(str(beginning))
                    self.table.item(i, COLUMN_ASSET_ENDING_BALANCE).setText(str(ending))



