import sys
import datetime
from qtpy import QtWidgets, QtGui, QtCore
from simpleaccounting.app.system import System, IllegalOperation, EntryNotFound
from simpleaccounting.widgets.qwidgets import CustomQDialog, CustomInputDialog, HorizontalSpacer


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
        self.lineedit = QtWidgets.QLineEdit()

        form = QtWidgets.QFormLayout()
        form.addRow("币种名称", self.lineedit)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(form)
        vbox.addWidget(self.button_box)

        self.lineedit.setFocus(QtCore.Qt.OtherFocusReason)

    def accept(self):
        """"""
        name = self.lineedit.text().strip()
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
        self.dateedit = QtWidgets.QDateEdit()
        self.dspbox = QtWidgets.QDoubleSpinBox()
        self.dspbox.setMinimum(0.0)
        self.dspbox.setMaximum(sys.float_info.max)
        form = QtWidgets.QFormLayout()
        form.addRow("日期", self.dateedit)
        form.addRow("汇率", self.dspbox)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(form)
        vbox.addWidget(self.button_box)
        self.dateedit.setFocus(QtCore.Qt.OtherFocusReason)

    def accept(self):
        """"""
        date = self.dateedit.date()
        date = datetime.date(date.year(), date.month(), date.day())
        rate = self.dspbox.value()
        if self.on_accept((date, rate)):
            super().accept()


class CurrencyDialog(CustomQDialog):
    """"""
    def __init__(self):
        """"""
        super().__init__()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        """"""
        self.setWindowTitle("货币汇率")

        self.list_currency = QtWidgets.QListWidget()
        self.toolbar_currency = QtWidgets.QToolBar()
        self.toolbar_currency.addWidget(HorizontalSpacer())

        self.action_create_currency = QtWidgets.QAction(QtGui.QIcon(":/icons/RuleCreate(Color).svg"), "创建", self)
        self.action_create_currency.triggered.connect(self.on_createCurrency)
        self.action_delete_currency = QtWidgets.QAction(QtGui.QIcon(":/icons/RuleDelete1(Color).svg"), "删除", self)
        self.action_delete_currency.triggered.connect(self.on_deleteCurrency)

        self.toolbar_currency.addAction(self.action_create_currency)
        self.toolbar_currency.addAction(self.action_delete_currency)

        self.table_exchange = QtWidgets.QTableWidget()
        self.table_exchange.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_exchange.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_exchange.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_exchange.setColumnCount(2)
        self.table_exchange.setAlternatingRowColors(True)
        self.table_exchange.horizontalHeader().setStretchLastSection(True)
        self.table_exchange.verticalHeader().setVisible(False)
        self.table_exchange.setHorizontalHeaderLabels(["日期", "汇率"])

        self.toolbar_exchange = QtWidgets.QToolBar()
        self.toolbar_exchange.addWidget(HorizontalSpacer())

        self.action_create_exchange = QtWidgets.QAction(QtGui.QIcon(":/icons/RuleCreate(Color).svg"), "创建", self)
        self.action_create_exchange.triggered.connect(self.on_createExchange)
        self.action_delete_exchange = QtWidgets.QAction(QtGui.QIcon(":/icons/RuleDelete1(Color).svg"), "删除", self)
        self.action_delete_exchange.triggered.connect(self.on_deleteExchange)

        self.toolbar_exchange.addAction(self.action_create_exchange)
        self.toolbar_exchange.addAction(self.action_delete_exchange)

        self.gbox_currency = QtWidgets.QGroupBox("币种", self)
        self.gbox_currency.setLayout(QtWidgets.QVBoxLayout())
        self.gbox_currency.layout().addWidget(self.toolbar_currency)
        self.gbox_currency.layout().addWidget(self.list_currency)

        self.gbox_exchange = QtWidgets.QGroupBox("汇率", self)
        self.gbox_exchange.setLayout(QtWidgets.QVBoxLayout())
        self.gbox_exchange.layout().addWidget(self.toolbar_exchange)
        self.gbox_exchange.layout().addWidget(self.table_exchange)

        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.gbox_currency)
        hbox.addWidget(self.gbox_exchange)
        self.list_currency.currentItemChanged.connect(self.updateExchangeUI)

    def on_createCurrency(self):
        """"""
        def createCurrency(name: str) -> bool:
            try:
                System.createCurrency(name)
                self.list_currency.addItem(name)
                return True
            except IllegalOperation as e:
                if e.args[0] == "A2.2/2":
                    QtWidgets.QMessageBox.critical(None, "创建失败", "错误代码 A2.2/2：币种已存在。")
                return False
        #
        CurrencyCreateDialog(createCurrency).exec_()

    def on_deleteCurrency(self):
        """"""
        if self.list_currency.currentItem() is None:
            return

        name = self.list_currency.currentItem().text()
        try:
            System.deleteCurrency(name)
            self.list_currency.takeItem(self.list_currency.currentRow())
        except EntryNotFound as e:
            QtWidgets.QMessageBox.critical(None, "删除失败", f"错误：项\"{e}\"未找到。")
        except IllegalOperation as e:
            if e.args[0] == "A2.2/1":
                QtWidgets.QMessageBox.critical(None, "删除失败", "错误代码 A2.2/1：人民币为内置默认币种，不可删除。")
            elif e.args[0] == "A2.1/2":
                QtWidgets.QMessageBox.critical(None, "删除失败", "错误代码 A2.1/2：币种正在使用，不可删除。")

    def on_createExchange(self):
        if self.list_currency.currentItem() is None:
            return
        # !if
        def addExchange(data):
            currency = self.list_currency.currentItem().text()
            date, rate = data
            try:
                System.createExchangeRate(currency, rate, date)
            except IllegalOperation:
                QtWidgets.QMessageBox.critical(None, "删除失败", "当前日期已存在汇率")
            self.updateExchangeUI()
            return True

        dialog = ExchangeCreateDialog(addExchange)
        dialog.dateedit.setDisplayFormat("yyyy.MM")

        date_until = System.meta().date_until
        dialog.dateedit.setDateRange(datetime.date(1999, 1, 1), date_until)
        dialog.dateedit.setDate(QtCore.QDate(date_until.year, date_until.month, 1))
        dialog.exec_()

    def on_deleteExchange(self):
        if self.list_currency.currentItem() is None:
            return

        row = self.table_exchange.currentRow()
        if row < 0:
            return

        date = list(map(int, self.table_exchange.item(row, 0).text().split('.')))
        date = datetime.date(date[0], date[1], 1)

        try:
            currency_name = self.list_currency.currentItem().text()
            System.deleteExchangeRate(currency_name, date)
        except EntryNotFound as e:
            QtWidgets.QMessageBox.critical(None, "删除失败", f"错误：项\"{e}\"未找到。")
        except IllegalOperation as e:
            if e.args[0] == 'A2.2/1':
                QtWidgets.QMessageBox.critical(None, "删除失败", "错误代码 A2.2/1：人民币为内置默认币种，不可删除。")
            elif e.args[0] == 'A2.1/3':
                QtWidgets.QMessageBox.critical(None, "删除失败", "错误代码 A2.2/1：使用中的币种汇率的期间，不可删除。")

        self.updateExchangeUI()

    def updateUI(self):
        self.gbox_exchange.setEnabled(False)
        self.list_currency.clear()
        for currency in System.currencies():
            self.list_currency.addItem(currency.name)
        #
        self.updateExchangeUI()

    def updateExchangeUI(self):
        item = self.list_currency.currentItem()
        if not item:
            self.gbox_exchange.setEnabled(False)
            return

        self.gbox_exchange.setEnabled(True)
        self.table_exchange.clear()
        self.table_exchange.setHorizontalHeaderLabels(["日期", "汇率"])

        currency_name = item.text()
        exchange_rates = System.exchangeRates(currency_name)
        self.table_exchange.setRowCount(len(exchange_rates))

        for row, rate in enumerate(exchange_rates):
            self.table_exchange.setItem(row, 0, QtWidgets.QTableWidgetItem(rate.effective_date.strftime("%Y.%m")))
            self.table_exchange.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{rate.rate:.2f}"))
            row += 1
