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
from tkinter.tix import COLUMN

from qtpy import QtWidgets, QtCore, QtGui

from simpleaccounting.app.system import System
from simpleaccounting.tools.dateutil import last_day_of_month, qdate_to_date
from simpleaccounting.tools.mymath import FloatWithPrecision
from simpleaccounting.widgets.qwidgets import HorizontalSpacer
from simpleaccounting.widgets.subsidiaryledger import AccountSelectDialog
from simpleaccounting.tools import stringscores


COLUMN_ACCOUNT_CODE = 0
COLUMN_ACCOUNT_NAME = 1
COLUMN_CURRENCY_AMOUNT = 2
COLUMN_LOCAL_CURRENCY_AMOUNT = 3

class EndingBalanceWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        self.setWindowTitle("期末余额")
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["代码", "科目", "货币余额", "本币余额"])
        self.tree.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.dateedit_end = QtWidgets.QDateEdit(last_day_of_month(System.meta().month_until))
        self.tb_choose_account = QtWidgets.QToolButton(self)
        self.tb_choose_account.setToolTip('选择')
        self.tb_choose_account.setStyleSheet('background-color: transparent')
        self.tb_choose_account.setIcon(QtGui.QIcon(":/icons/FindNavigatorSearch(Color).svg"))
        self.tb_choose_account.clicked.connect(self.on_tb_chooseAccountTriggered)
        self.cbox_account = QtWidgets.QComboBox(self)
        self.cbox_account.setMinimumHeight(int(self.fontMetrics().height() * 1.8))
        self.cbox_account.setEditable(True)
        self.cbox_account.lineEdit().editingFinished.connect(self.on_cbox_accountEditingFinished)
        self.tb_locate = QtWidgets.QToolButton()
        self.tb_locate.setToolTip('选中')
        self.tb_locate.setIcon(QtGui.QIcon(":/icons/location.png"))
        self.tb_locate.setStyleSheet("background: transparent;")
        self.tb_locate.clicked.connect(self.on_tb_locateTriggered)
        #
        container = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout(container)
        hbox.addWidget(QtWidgets.QLabel("截止日期"))
        hbox.addWidget(self.dateedit_end)
        self.action_pull = QtWidgets.QAction(QtGui.QIcon(":/icons/persistenceEntity.svg"), "拉取", self)
        self.action_pull.triggered.connect(self.on_action_pullTriggered)
        self.tbar = QtWidgets.QToolBar()
        self.tbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.tbar.addWidget(HorizontalSpacer())
        self.tbar.addWidget(container)
        self.tbar.addSeparator()
        self.tbar.addAction(self.action_pull)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(1)
        vbox.addWidget(self.tbar)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(10)
        hbox.addWidget(QtWidgets.QLabel("科目"))
        hbox.addWidget(self.tb_choose_account)
        hbox.addWidget(self.cbox_account)
        hbox.addWidget(self.tb_locate)
        vbox.addLayout(hbox)
        vbox.addWidget(self.tree)

    def updateUI(self):
        self.items = {}
        for a in System.accounts():
            item = QtWidgets.QTreeWidgetItem()
            item.setText(COLUMN_ACCOUNT_CODE, a.code)
            item.setText(COLUMN_ACCOUNT_NAME, a.name)
            item.setData(COLUMN_ACCOUNT_CODE, QtCore.Qt.UserRole, a)
            item.setTextAlignment(COLUMN_CURRENCY_AMOUNT, QtCore.Qt.AlignRight)
            item.setTextAlignment(COLUMN_LOCAL_CURRENCY_AMOUNT, QtCore.Qt.AlignRight)
            self.items[a.code] = item
        # 1for
        for code, item in self.items.items():
            account = System.account(code)
            if account.parent:
                self.items[account.parent.code].addChild(item)
            else:
                self.tree.addTopLevelItem(item)
        # 1for
        self.cbox_account.clear()
        for account in System.accounts():
            self.cbox_account.addItem(f"{account.code} {account.name}", account)
        # 1for

    def on_action_pullTriggered(self):
        font = self.font()
        font.setBold(True)

        for item in self.items.values():
            if item.childCount() > 0:
                item.setText(COLUMN_LOCAL_CURRENCY_AMOUNT, "")
                item.setData(COLUMN_LOCAL_CURRENCY_AMOUNT, QtCore.Qt.UserRole, None)

        for item in self.items.values():
            account = item.data(COLUMN_ACCOUNT_CODE, QtCore.Qt.UserRole)
            if not account.children and account.currency:
                currency_amount, currency_local_amount = System.endingBalance(account.code, qdate_to_date(self.dateedit_end.date()))
                item.setText(COLUMN_CURRENCY_AMOUNT, str(currency_amount))
                item.setText(COLUMN_LOCAL_CURRENCY_AMOUNT, str(currency_local_amount))
                while item.parent():
                    amount = item.parent().data(COLUMN_LOCAL_CURRENCY_AMOUNT, QtCore.Qt.UserRole)
                    if amount is None:
                        amount = FloatWithPrecision(0.0) + currency_local_amount
                        item.parent().setData(COLUMN_LOCAL_CURRENCY_AMOUNT, QtCore.Qt.UserRole, amount)
                        item.parent().setText(COLUMN_LOCAL_CURRENCY_AMOUNT, str(amount))
                        item.parent().setFont(COLUMN_LOCAL_CURRENCY_AMOUNT, font)
                    else:
                        amount = amount + currency_local_amount
                        item.parent().setData(COLUMN_LOCAL_CURRENCY_AMOUNT, QtCore.Qt.UserRole, amount)
                        item.parent().setText(COLUMN_LOCAL_CURRENCY_AMOUNT, str(amount))
                        item.parent().setFont(COLUMN_LOCAL_CURRENCY_AMOUNT, font)
                    #
                    item = item.parent()

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

    def on_tb_locateTriggered(self):
        if account := self.cbox_account.currentData(QtCore.Qt.UserRole):
            if item := self.items.get(account.code):
                self.tree.setCurrentItem(item)
