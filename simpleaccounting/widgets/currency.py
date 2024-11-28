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

import sys
import datetime
from qtpy import QtWidgets, QtCore
from simpleaccounting.app.system import System, IllegalOperation, EntryNotFound
from simpleaccounting.tools.dateutil import last_day_of_month
from simpleaccounting.widgets.qwidgets import CustomInputDialog, HorizontalSpacer


class CurrencyWidget(QtWidgets.QWidget):
    """"""
    def __init__(self):
        """"""
        super().__init__()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        """"""
        self.setWindowTitle("币种管理")
        self.list_currency = QtWidgets.QListWidget()
        self.tbar_currency = QtWidgets.QToolBar()
        self.tbar_currency.addWidget(HorizontalSpacer())
        self.action_create_currency = QtWidgets.QAction( "创建", self)
        self.action_create_currency.triggered.connect(self.on_action_createCurrencyTriggered)
        self.action_delete_currency = QtWidgets.QAction("删除", self)
        self.action_delete_currency.triggered.connect(self.on_action_deleteCurrencyTriggered)
        self.action_delete_currency.setEnabled(False)
        self.tbar_currency.addAction(self.action_create_currency)
        self.tbar_currency.addAction(self.action_delete_currency)
        self.table_exchange = QtWidgets.QTableWidget()
        self.table_exchange.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_exchange.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_exchange.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_exchange.setColumnCount(2)
        self.table_exchange.setAlternatingRowColors(True)
        self.table_exchange.horizontalHeader().setStretchLastSection(True)
        self.table_exchange.verticalHeader().setVisible(False)
        self.table_exchange.setHorizontalHeaderLabels(["日期", "汇率"])
        self.tbar_exchange = QtWidgets.QToolBar()
        self.tbar_exchange.addWidget(HorizontalSpacer())
        self.action_create_exchange = QtWidgets.QAction("创建", self)
        self.action_create_exchange.triggered.connect(self.on_action_createExchangeTriggered)
        self.action_delete_exchange = QtWidgets.QAction("删除", self)
        self.action_delete_exchange.triggered.connect(self.on_action_deleteExchangeTriggered)
        self.action_delete_exchange.setEnabled(False)
        self.tbar_exchange.addAction(self.action_create_exchange)
        self.tbar_exchange.addAction(self.action_delete_exchange)
        self.gbox_currency = QtWidgets.QGroupBox("币种", self)
        self.gbox_currency.setLayout(QtWidgets.QVBoxLayout())
        self.gbox_currency.layout().addWidget(self.tbar_currency)
        self.gbox_currency.layout().addWidget(self.list_currency)
        self.gbox_exchange = QtWidgets.QGroupBox("汇率", self)
        self.gbox_exchange.setLayout(QtWidgets.QVBoxLayout())
        self.gbox_exchange.layout().addWidget(self.tbar_exchange)
        self.gbox_exchange.layout().addWidget(self.table_exchange)
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.gbox_currency)
        hbox.addWidget(self.gbox_exchange)
        self.list_currency.currentItemChanged.connect(self.on_list_currencyCurrentItemChanged)
        self.table_exchange.itemSelectionChanged.connect(self.on_table_exchangeItemSelectionChanged)

    def on_action_createCurrencyTriggered(self):
        """"""
        def createCurrency(name: str) -> bool:
            try:
                System.createCurrency(name)
                self.updateUI()
                return True
            except IllegalOperation as e:
                if e.args[0] == "A2.2/2":
                    QtWidgets.QMessageBox.critical(None, "创建失败", "错误代码 A2.2/2：币种已存在。")
                return False
        #
        CurrencyCreateDialog(createCurrency).exec_()

    def on_action_deleteCurrencyTriggered(self):
        """"""
        if self.list_currency.currentItem() is None:
            return
        #
        try:
            System.deleteCurrency(self.list_currency.currentItem().text())
            self.updateUI()
        except EntryNotFound as e:
            QtWidgets.QMessageBox.critical(None, "删除失败", f"错误：项\"{e}\"未找到。")
        except IllegalOperation as e:
            if e.args[0] == "A2.2/1":
                QtWidgets.QMessageBox.critical(None, "删除失败", "错误代码 A2.2/1：人民币为内置默认币种，不可删除。")
            elif e.args[0] == "A2.1/2":
                QtWidgets.QMessageBox.critical(None, "删除失败", "错误代码 A2.1/2：币种正在使用，不可删除。")

    def on_action_createExchangeTriggered(self):
        if self.list_currency.currentItem() is None:
            return
        # !if
        def addExchange(data):
            currency = self.list_currency.currentItem().text()
            date, rate = data
            try:
                System.createExchangeRate(currency, rate, date)
                self.on_list_currencyCurrentItemChanged()
            except IllegalOperation:
                QtWidgets.QMessageBox.critical(None, "删除失败", "当前日期已存在汇率")
            return True

        dialog = ExchangeCreateDialog(addExchange)
        date_until = last_day_of_month(System.meta().month_until)
        dialog.de.setDateRange(datetime.date(1999, 1, 1), date_until)
        dialog.de.setDate(date_until)
        dialog.exec_()

    def on_action_deleteExchangeTriggered(self):
        if self.list_currency.currentItem() is None:
            return

        row = self.table_exchange.currentRow()
        if row < 0:
            return

        date = list(map(int, self.table_exchange.item(row, 0).text().split('.')))
        date = datetime.date(date[0], date[1], date[2])

        if date.year == 1970:
            QtWidgets.QMessageBox.critical(None, "删除失败", "错误代码 A2.2/1：使用中的币种汇率的期间，不可删除。")
            return

        try:
            currency_name = self.list_currency.currentItem().text()
            System.deleteExchangeRate(currency_name, date)
            self.on_list_currencyCurrentItemChanged()
        except EntryNotFound as e:
            QtWidgets.QMessageBox.critical(None, "删除失败", f"错误：项\"{e}\"未找到。")
        except IllegalOperation as e:
            if e.args[0] == 'A2.2/1':
                QtWidgets.QMessageBox.critical(None, "删除失败", "错误代码 A2.2/1：人民币为内置默认币种，不可删除。")
            elif e.args[0] == 'A2.1/3':
                QtWidgets.QMessageBox.critical(None, "删除失败", "错误代码 A2.2/1：使用中的币种汇率的期间，不可删除。")

    def updateUI(self):
        self.gbox_exchange.setEnabled(False)
        self.list_currency.clear()
        for currency in System.currencies():
            self.list_currency.addItem(currency.name)

    def on_list_currencyCurrentItemChanged(self):
        item = self.list_currency.currentItem()
        self.gbox_exchange.setEnabled(bool(item))
        self.action_delete_currency.setEnabled(bool(item))
        self.gbox_exchange.setTitle((item.text() if item else "") + "汇率")

        if not item:
            return

        currency_name = item.text()
        self.table_exchange.clear()
        self.table_exchange.setHorizontalHeaderLabels(["日期", "汇率"])
        exchange_rates = System.exchangeRates(currency_name)
        self.table_exchange.setRowCount(len(exchange_rates))

        for row, rate in enumerate(exchange_rates):
            self.table_exchange.setItem(row, 0, QtWidgets.QTableWidgetItem(rate.effective_date.strftime("%Y.%m.%d")))
            self.table_exchange.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{rate.rate}"))
            row += 1

    def on_table_exchangeItemSelectionChanged(self):
        self.action_delete_exchange.setEnabled(bool(self.table_exchange.selectedItems()))


class CurrencyCreateDialog(CustomInputDialog):
    """"""
    def __init__(self, on_accept=lambda b: ...):
        """"""
        super().__init__()
        self.setupUI()
        self.on_accept = on_accept

    def setupUI(self):
        """"""
        self.setWindowTitle("创建币种")
        self.le_name = QtWidgets.QLineEdit()
        form = QtWidgets.QFormLayout()
        form.addRow("币种名称", self.le_name)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(form)
        vbox.addWidget(self.button_box)
        self.le_name.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)

    def accept(self):
        """"""
        name = self.le_name.text().strip()
        if not name:
            QtWidgets.QMessageBox.critical(None, "创建失败", "名称项不可为空")
            return
        if self.on_accept(name):
            super().accept()


class ExchangeCreateDialog(CustomInputDialog):

    def __init__(self, on_accept=lambda b: ...):
        """"""
        super().__init__()
        self.setupUI()
        self.on_accept = on_accept

    def setupUI(self):
        """"""
        self.setWindowTitle("设置汇率")
        self.de = QtWidgets.QDateEdit()
        self.dspbox_rate = QtWidgets.QDoubleSpinBox()
        self.dspbox_rate.setMinimum(0.0)
        self.dspbox_rate.setMaximum(sys.float_info.max)
        form = QtWidgets.QFormLayout()
        form.addRow("日期", self.de)
        form.addRow("汇率", self.dspbox_rate)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(form)
        vbox.addWidget(self.button_box)
        self.de.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)

    def accept(self):
        """"""
        date = self.de.date()
        date = datetime.date(date.year(), date.month(), date.day())
        rate = self.dspbox_rate.value()
        if self.on_accept((date, rate)):
            super().accept()
