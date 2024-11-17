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
from simpleaccounting.app.system import System, VoucherEntry, Voucher, IllegalOperation
from simpleaccounting.tools.mymath import FloatWithPrecision
from simpleaccounting.widgets.qwidgets import CustomQDialog, HorizontalSpacer
from simpleaccounting.widgets.account import AccountActivateDialog
from simpleaccounting.tools.dateutil import last_day_of_month, first_day_of_month

COLUMNS = ["摘要", "科目名称", "借方币种金额", "贷方币种金额", "币种", "汇率", "借方金额", "贷方金额", "标签"]
COLUMNS_WIDTH = [20, 20, 12, 12, 6, 8, 12, 12, 6]
COLUMN_BRIEF = 0
COLUMN_ACCOUNT = 1
COLUMN_DEBIT_CURRENCY_AMOUNT = 2
COLUMN_CREDIT_CURRENCY_AMOUNT = 3
COLUMN_CURRENCY = 4
COLUMN_EXCHANGE_RATE = 5
COLUMN_DEBIT_LOCAL_AMOUNT = 6
COLUMN_CREDIT_LOCAL_AMOUNT = 7
COLUMN_TAG = 8
COLUMN_COUNT = 9


class ReadOnlyDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        # Return None to make the cell uneditable
        return None


class AccountItemDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        comboBox = QtWidgets.QComboBox(parent)
        comboBox.setEditable(True)
        for account in System.topMRUAccounts(20):
            comboBox.addItem(f"{account.name}")
        return comboBox

    def setEditorData(self, comboBox, index):
        # 从模型中获取数据，并在编辑器中设置多行文本
        text = index.model().data(index, QtCore.Qt.ItemDataRole.EditRole)
        comboBox.lineEdit().setText(text) if text else ...

    def setModelData(self, comboBox, model, index):
        # 将编辑器中的多行文本保存回模型
        text = comboBox.lineEdit().text()
        if text.strip() == "":
            model.setData(index, "", QtCore.Qt.ItemDataRole.EditRole)
            model.setData(index, None, QtCore.Qt.ItemDataRole.UserRole)
        elif account := System.account(text):
            model.setData(index, account.qualname, QtCore.Qt.ItemDataRole.EditRole)
            model.setData(index, account, QtCore.Qt.ItemDataRole.UserRole)
            self.setCurrencyIfNot(account)
        elif account := System.accountByName(text):
            model.setData(index, account.qualname, QtCore.Qt.ItemDataRole.EditRole)
            model.setData(index, account, QtCore.Qt.ItemDataRole.UserRole)
            self.setCurrencyIfNot(account)
        elif account := System.accountByQualname(text):
            model.setData(index, account.qualname, QtCore.Qt.ItemDataRole.EditRole)
            model.setData(index, account, QtCore.Qt.ItemDataRole.UserRole)
            self.setCurrencyIfNot(account)
        else:
            model.setData(index, "", QtCore.Qt.ItemDataRole.EditRole)
            model.setData(index, None, QtCore.Qt.ItemDataRole.UserRole)
        #
        model.setData(index, datetime.datetime.now(), QtCore.Qt.ItemDataRole.StatusTipRole)

    def setCurrencyIfNot(self, account):
        if not account.children and account.currency is None:
            def setCurrency(currency_name):
                System.setAccountCurrency(account.code, currency_name)
                return True
            AccountActivateDialog(account.name, account.code, setCurrency).exec_()


class CurrencyItemDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        # Create a QLineEdit as editor
        editor = QtWidgets.QLineEdit(parent)
        editor.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        validator = QtGui.QDoubleValidator(0.00,
                                           10000000.00,
                                           2)  # limits between 0 and 10 million, 2 decimal points
        editor.setValidator(validator)
        return editor

    def setModelData(self, editor, model, index):
        value = FloatWithPrecision.from_string(editor.text())
        if value == 0.0:
            model.setData(index, "", QtCore.Qt.ItemDataRole.EditRole)
            model.setData(index, None, QtCore.Qt.ItemDataRole.UserRole)
        else:
            model.setData(index, str(value), QtCore.Qt.ItemDataRole.EditRole)
            model.setData(index, value, QtCore.Qt.ItemDataRole.UserRole)
        # !if
        model.setData(index, datetime.datetime.now(), QtCore.Qt.ItemDataRole.StatusTipRole)


class MultiLineEditDelegate(QtWidgets.QStyledItemDelegate):
    class PlainTextEditWithEnter(QtWidgets.QPlainTextEdit):
        """Custom QPlainTextEdit where Enter submits and Ctrl+Enter creates a new line."""

        def __init__(self, parent=None):
            super().__init__(parent)

        def keyPressEvent(self, event):
            # Ctrl + Enter for newline
            if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                if event.modifiers() & QtCore.Qt.ControlModifier:
                    # Insert a new line if Ctrl is pressed
                    self.insertPlainText("\n")
                else:
                    # If Enter alone is pressed, submit the content
                    self.parent().parent().commitData(self)  # Commit the data back to the table
                    self.clearFocus()  # Lose focus to finish editing
            else:
                # Call the default event handler for other keys
                super().keyPressEvent(event)

    """Delegate for providing multi-line text editing in QTableWidget."""

    def createEditor(self, parent, option, index):
        # 使用 QPlainTextEdit 作为编辑器
        editor = VoucherTableWidget.MultiLineEditDelegate.PlainTextEditWithEnter(parent)
        return editor

    def setEditorData(self, editor, index):
        # 从模型中获取数据，并在编辑器中设置多行文本
        text = index.model().data(index, QtCore.Qt.ItemDataRole.EditRole)
        editor.setPlainText(text)

    def setModelData(self, editor, model, index):
        # 将编辑器中的多行文本保存回模型
        text = editor.toPlainText()
        model.setData(index, text, QtCore.Qt.EditRole)


class VoucherTableWidget(QtWidgets.QTableWidget):
    """"""
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWordWrap(True)
        self.setAlternatingRowColors(True)
        self.setColumnCount(COLUMN_COUNT)
        self.setHorizontalHeaderLabels(COLUMNS)
        self.currencyItemDelegate = CurrencyItemDelegate(self)
        self.accountItemDelegate = AccountItemDelegate(self)
        self.readonlyItemDelegate = ReadOnlyDelegate(self)
        self.multilineItemDelegate = MultiLineEditDelegate(self)
        self.setItemDelegateForColumn(COLUMN_BRIEF, self.multilineItemDelegate)
        self.setItemDelegateForColumn(COLUMN_ACCOUNT, self.accountItemDelegate)
        self.setItemDelegateForColumn(COLUMN_DEBIT_CURRENCY_AMOUNT, self.currencyItemDelegate)
        self.setItemDelegateForColumn(COLUMN_CREDIT_CURRENCY_AMOUNT, self.currencyItemDelegate)
        self.setItemDelegateForColumn(COLUMN_CURRENCY, self.readonlyItemDelegate)
        self.setItemDelegateForColumn(COLUMN_EXCHANGE_RATE, self.readonlyItemDelegate)
        self.setItemDelegateForColumn(COLUMN_DEBIT_LOCAL_AMOUNT, self.readonlyItemDelegate)
        self.setItemDelegateForColumn(COLUMN_CREDIT_LOCAL_AMOUNT, self.readonlyItemDelegate)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.tb_choose_account = QtWidgets.QToolButton(self)
        self.tb_choose_account.setStyleSheet('background-color: transparent')
        self.tb_choose_account.setIcon(QtGui.QIcon(":/icons/FindNavigatorSearch(Color).svg"))
        self.tb_choose_account.hide()
        self.selectionModel().selectionChanged.connect(self.on_selectionChanged)

    def resizeEvent(self, *args, **kwargs):
        """"""
        for i in range(COLUMN_COUNT):
            width = self.fontMetrics().horizontalAdvance("9"*COLUMNS_WIDTH[i])
            self.setColumnWidth(i, width)
        # !for
        if self.tb_choose_account.isVisible():
            rect = self.visualRect(self.currentIndex())
            pos = (self.viewport().mapToParent(rect.bottomRight()) -
                   QtCore.QPoint(self.tb_choose_account.width() * 2,
                                 self.tb_choose_account.height() +
                                 (rect.height() - self.tb_choose_account.height()) // 2))
            self.tb_choose_account.move(pos)
        # !if
        super().resizeEvent(*args, **kwargs)
        # 调整表格宽度变化时的行高
        self.resizeRowsToContents()

    def on_selectionChanged(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        """On user table cell/row selection changed, show/hide the helper tool button"""
        if len(selected.indexes()) == 1:
            index = selected.indexes()[0]
            if index.column() == 1:
                self.tb_choose_account.show()
                # move the helper tool button to correct position
                rect = self.visualRect(index)
                pos = (self.viewport().mapToParent(rect.bottomRight()) -
                       QtCore.QPoint(self.tb_choose_account.width() * 2,
                                     self.tb_choose_account.height() + (rect.height() - self.tb_choose_account.height()) // 2))
                self.tb_choose_account.move(pos)
            else:
                self.tb_choose_account.hide()
        else:
            self.tb_choose_account.hide()

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
            if i == 0:
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


class VoucherEditDialog(CustomQDialog):

    def __init__(self, date_month: datetime.date):
        super().__init__()
        self.setupUI()
        self.date_month = date_month
        self.de.setDateRange(
            first_day_of_month(self.date_month),
            last_day_of_month(self.date_month)
        )
        self.vouchers = System.vouchers(
            lambda v: first_day_of_month(self.date_month) <= v.date and
                      last_day_of_month(self.date_month) >= v.date
        )
        self.index_current = -1 if len(self.vouchers) == 0 else 0
        self.updateUI()
        self.startTimer(200)

    def setupUI(self):
        self.setWindowTitle("凭证录入")
        self.lbl_hint = QtWidgets.QLabel("点击下一张以录入下一张凭证")
        self.lbl_hint.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        font = self.font()
        font.setBold(True)
        self.de = QtWidgets.QDateEdit()
        self.de.setStyleSheet('color: blue;')
        self.de.setFont(font)
        self.lbl_voucher_number = QtWidgets.QLabel()
        self.lbl_voucher_number.setStyleSheet('color: blue;')
        self.lbl_voucher_number.setFont(font)
        self.table = VoucherTableWidget()
        self.action_print = QtWidgets.QAction(QtGui.QIcon(":/icons/print.svg"), "打印", self)
        self.action_print.triggered.connect(self.printVoucher)
        self.action_print.setShortcut(QtGui.QKeySequence('Ctrl+P'))
        self.action_print.setToolTip('Ctrl+P')
        self.action_insert_row_last = QtWidgets.QAction(QtGui.QIcon(":/icons/insertRowBelow.svg"), "新增行", self)
        self.action_insert_row_last.triggered.connect(self.insertRowLast)
        self.action_insert_row_last.setShortcut(QtGui.QKeySequence('Alt+A'))
        self.action_insert_row_last.setToolTip('Alt+A')
        self.action_remove_current_row = QtWidgets.QAction(QtGui.QIcon(":/icons/Remove(Color).svg"), "删除行", self)
        self.action_remove_current_row.triggered.connect(self.removeCurrentRow)
        self.action_remove_current_row.setShortcut(QtGui.QKeySequence('Alt+D'))
        self.action_remove_current_row.setToolTip('Alt+D')
        self.action_first = QtWidgets.QAction(QtGui.QIcon(":/icons/play_first.svg"), "第一张", self)
        self.action_first.triggered.connect(self.on_actionFirstTriggered)
        self.action_first.setShortcut(QtGui.QKeySequence('Ctrl+Alt+Left'))
        self.action_first.setToolTip('Ctrl+Alt+Left')
        self.action_last = QtWidgets.QAction(QtGui.QIcon(":/icons/play_last.svg"), "最末张", self)
        self.action_last.triggered.connect(self.on_actionLastTriggered)
        self.action_last.setShortcut(QtGui.QKeySequence('Ctrl+Alt+Right'))
        self.action_last.setToolTip('Ctrl+Alt+Right')
        self.action_back = QtWidgets.QAction(QtGui.QIcon(":/icons/play_back.svg"), "上一张", self)
        self.action_back.triggered.connect(self.on_actionBackTriggered)
        self.action_back.setShortcut(QtGui.QKeySequence('Alt+Left'))
        self.action_back.setToolTip('Alt+Left')
        self.action_forward = QtWidgets.QAction(QtGui.QIcon(":/icons/play_forward.svg"), "下一张", self)
        self.action_forward.triggered.connect(self.on_actionForwardTriggered)
        self.action_forward.setShortcut(QtGui.QKeySequence('Alt+Right'))
        self.action_forward.setToolTip('Alt+Right')
        self.action_save = QtWidgets.QAction(QtGui.QIcon(":/icons/Save(Color).svg"), "保存", self)
        self.action_save.triggered.connect(self.on_actionSaveTriggered)
        self.action_save.setShortcut(QtGui.QKeySequence('Ctrl+S'))
        self.action_save.setToolTip('Ctrl+S')
        self.action_void = QtWidgets.QAction(QtGui.QIcon(":/icons/Remove(Color).svg"), "作废", self)
        self.action_void.triggered.connect(self.on_actionVoidTriggered)
        self.action_void.setShortcut(QtGui.QKeySequence('Alt+V'))
        self.action_void.setToolTip('Alt+V')
        self.tbar = QtWidgets.QToolBar()
        self.tbar.addAction(self.action_print)
        self.tbar.addAction(self.action_insert_row_last)
        self.tbar.addAction(self.action_remove_current_row)
        self.tbar.addWidget(HorizontalSpacer())
        self.tbar.addSeparator()
        self.tbar.addAction(self.action_first)
        self.tbar.addAction(self.action_back)
        self.tbar.addAction(self.action_forward)
        self.tbar.addAction(self.action_last)
        self.tbar.addSeparator()
        self.tbar.addAction(self.action_save)
        self.tbar.addAction(self.action_void)
        self.tbar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.tbar)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(10)
        hbox.addWidget(QtWidgets.QLabel("日期"))
        hbox.addWidget(self.de)
        hbox.addWidget(QtWidgets.QLabel("记字号"))
        hbox.addWidget(self.lbl_voucher_number)
        vbox.addLayout(hbox)
        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.lbl_hint)
        self.stack.addWidget(self.table)
        vbox.addWidget(self.stack)

    def printVoucher(self):
        print("打印凭证")

    def insertRowLast(self):
        row = self.table.rowCount() - 1
        self.table.insertRow(row)

    def removeCurrentRow(self):
        row = self.table.currentRow()
        if row != -1:
            self.table.removeRow(row)

    def on_modificationChanged(self):
        self.action_save.setEnabled(True)

    def on_actionSaveTriggered(self):
        try:
            System.updateDebitCreditEntries(
                self.vouchers[self.index_current].number,
                *self.voucherEntries()
            )
            self.vouchers[self.index_current] = System.voucher(self.vouchers[self.index_current].number)
        except IllegalOperation as e:
            if e.args[0] == 'A2.1/1':
                QtWidgets.QMessageBox.critical(None, "保存失败", f"错误代码 {e.args[0]}：科目未设定币种。")
            elif e.args[0] == 'A3.2/2':
                QtWidgets.QMessageBox.critical(None, "保存失败", f"错误代码 {e.args[0]}：借贷试算平衡。")


    def on_actionVoidTriggered(self):
        ret = QtWidgets.QMessageBox.question(None, "提示", "作废凭证将重排所有当月凭证号，是否作废该凭证?")
        if ret == QtWidgets.QDialogButtonBox.Yes:
            System.deleteVoucher(self.vouchers[self.index_current].number)
            self.vouchers.pop(self.index_current)
            for i, v in enumerate(self.vouchers):
                System.changeVoucherNumber(
                    v.number,
                    f"{self.date_month.strftime('%Y-%m')}/{i + 1:04d}"
                )

            self.vouchers = System.vouchers(
                lambda v: first_day_of_month(self.date_month) <= v.date and
                          last_day_of_month(self.date_month) >= v.date
            )
            self.index_current = min(self.index_current, len(self.vouchers) - 1)
            self.updateUI()

    def on_actionForwardTriggered(self):
        if self.index_current + 1 >= len(self.vouchers):
            # 新增凭证
            ret = QtWidgets.QMessageBox.question(None, "提示", "已经是最末张了，是否添加新的凭证?")
            if ret == QtWidgets.QMessageBox.Yes:
                date = datetime.date(
                    self.de.date().year(),
                    self.de.date().month(),
                    self.de.date().day()
                )
                #
                voucher = System.createVoucher(
                    number=f"{self.date_month.strftime('%Y-%m')}/{len(self.vouchers) + 1:04d}",
                    date=date,
                    note=""
                )
                self.vouchers.append(voucher)
                self.index_current = len(self.vouchers) - 1
                self.updateUI()
            else:
                return
        else:
            # 下一个凭证
            self.index_current += 1
            self.updateUI()

    def on_actionBackTriggered(self):
        self.index_current -= 1
        self.updateUI()

    def on_actionFirstTriggered(self):
        self.index_current = 0
        self.updateUI()

    def on_actionLastTriggered(self):
        self.index_current = len(self.vouchers) - 1
        self.updateUI()

    def updateUI(self):
        """"""
        # update title
        self.setWindowTitle(f"凭证录入 ({self.index_current + 1}/{len(self.vouchers)})")
        # enable/disable actions
        self.action_back.setEnabled(self.index_current > 0)
        self.action_first.setEnabled(self.index_current > 0)
        self.action_last.setEnabled(self.index_current < len(self.vouchers) - 1)
        for a in [self.action_print, self.action_insert_row_last,
                  self.action_save, self.action_void]:
            a.setEnabled(self.index_current != -1)
        # change visible widget
        if self.index_current != -1:
            self.stack.setCurrentWidget(self.table)
            voucher = self.vouchers[self.index_current]
            self.de.setDate(voucher.date)
            self.lbl_voucher_number.setText(voucher.number)
            self.loadVoucherIntoTable(voucher)
        else:
            self.stack.setCurrentWidget(self.lbl_hint)
            self.lbl_voucher_number.setText("")
        #
        self.action_save.setEnabled(False)

    def loadVoucherIntoTable(self, voucher: Voucher):
        self.table.clear()
        row_count = len(voucher.debit_entries) + len(voucher.credit_entries)
        self.table.setRowCount(row_count if row_count > 0 else 8)
        for r, entry in enumerate(voucher.debit_entries):
            self.table.item(r, COLUMN_BRIEF).setText(entry.brief)
            self.table.item(r, COLUMN_ACCOUNT).setText(entry.account.qualname)
            self.table.item(r, COLUMN_ACCOUNT).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                entry.account
            )
            self.table.item(r, COLUMN_DEBIT_CURRENCY_AMOUNT).setText(str(FloatWithPrecision(entry.amount)))
            self.table.item(r, COLUMN_DEBIT_CURRENCY_AMOUNT).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                FloatWithPrecision(entry.amount)
            )
            self.table.item(r, COLUMN_CURRENCY).setText(entry.account.currency.name)
            self.table.item(r, COLUMN_CURRENCY).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                entry.account.currency
            )
            self.table.item(r, COLUMN_EXCHANGE_RATE).setText(str(FloatWithPrecision(entry.exchange_rate.rate)))
            self.table.item(r, COLUMN_EXCHANGE_RATE).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                entry.exchange_rate
            )
            self.table.item(r, COLUMN_DEBIT_LOCAL_AMOUNT).setText(
                str(FloatWithPrecision(entry.exchange_rate.rate * entry.amount)))
            self.table.item(r, COLUMN_DEBIT_LOCAL_AMOUNT).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                FloatWithPrecision(entry.exchange_rate.rate * entry.amount)
            )
        # !for
        offset = len(voucher.debit_entries)
        for i, entry in enumerate(voucher.credit_entries):
            r = i + offset
            self.table.item(r, COLUMN_BRIEF).setText(entry.brief)
            self.table.item(r, COLUMN_ACCOUNT).setText(entry.account.qualname)
            self.table.item(r, COLUMN_ACCOUNT).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                entry.account
            )
            self.table.item(r, COLUMN_CREDIT_CURRENCY_AMOUNT).setText(str(FloatWithPrecision(entry.amount)))
            self.table.item(r, COLUMN_CREDIT_CURRENCY_AMOUNT).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                FloatWithPrecision(entry.amount)
            )
            self.table.item(r, COLUMN_CURRENCY).setText(entry.account.currency.name)
            self.table.item(r, COLUMN_CURRENCY).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                entry.account.currency
            )
            self.table.item(r, COLUMN_EXCHANGE_RATE).setText(str(FloatWithPrecision(entry.exchange_rate.rate)))
            self.table.item(r, COLUMN_EXCHANGE_RATE).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                entry.exchange_rate
            )
            self.table.item(r, COLUMN_CREDIT_LOCAL_AMOUNT).setText(
                str(FloatWithPrecision(entry.exchange_rate.rate * entry.amount)))
            self.table.item(r, COLUMN_CREDIT_LOCAL_AMOUNT).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                FloatWithPrecision(entry.exchange_rate.rate * entry.amount)
            )
        # !for

    def close(self):
        super().close()

    def timerEvent(self, *args, **kwargs):
        super().timerEvent(*args, **kwargs)
        self.refresh()

    def refresh(self):

        def isRefreshNeeded(item) -> bool:
            needed = item.data(QtCore.Qt.ItemDataRole.StatusTipRole) is not None
            item.setData(QtCore.Qt.ItemDataRole.StatusTipRole, None) if needed else ...
            self.action_save.setEnabled(True) if needed else ...
            return needed

        def setDirty(item):
            item.setData(QtCore.Qt.ItemDataRole.StatusTipRole, datetime.datetime.now())

        def refreshLocalAmount(row):
            exchange_rate = self.table.item(row, COLUMN_EXCHANGE_RATE).data(QtCore.Qt.ItemDataRole.UserRole)
            debit_currency_amount = self.table.item(row, COLUMN_DEBIT_CURRENCY_AMOUNT).data(QtCore.Qt.ItemDataRole.UserRole)
            credit_currency_amount = self.table.item(row, COLUMN_CREDIT_CURRENCY_AMOUNT).data(QtCore.Qt.ItemDataRole.UserRole)

            self.table.item(row, COLUMN_DEBIT_LOCAL_AMOUNT).setText("")
            self.table.item(row, COLUMN_DEBIT_LOCAL_AMOUNT).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                None
            )
            self.table.item(row, COLUMN_CREDIT_LOCAL_AMOUNT).setText("")
            self.table.item(row, COLUMN_CREDIT_LOCAL_AMOUNT).setData(
                QtCore.Qt.ItemDataRole.UserRole,
                None
            )
            if exchange_rate and debit_currency_amount:
                self.table.item(row, COLUMN_DEBIT_LOCAL_AMOUNT).setText(
                    str(debit_currency_amount * exchange_rate.rate)
                )
                self.table.item(row, COLUMN_DEBIT_LOCAL_AMOUNT).setData(
                    QtCore.Qt.ItemDataRole.UserRole,
                    debit_currency_amount * exchange_rate.rate
                )
                setDirty(self.table.item(row, COLUMN_DEBIT_LOCAL_AMOUNT))
            elif exchange_rate and credit_currency_amount:
                self.table.item(row, COLUMN_CREDIT_LOCAL_AMOUNT).setText(
                    str(credit_currency_amount * exchange_rate.rate)
                )
                self.table.item(row, COLUMN_CREDIT_LOCAL_AMOUNT).setData(
                    QtCore.Qt.ItemDataRole.UserRole,
                    credit_currency_amount * exchange_rate.rate
                )
                setDirty(self.table.item(row, COLUMN_CREDIT_LOCAL_AMOUNT))
            #
            refreshDebitCreditTotal()

        def refreshDebitCreditTotal():
            debit_total = FloatWithPrecision(0.0)
            credit_total = FloatWithPrecision(0.0)
            for row in range(self.table.rowCount() - 1):
                debit_currency_amount = self.table.item(row, COLUMN_DEBIT_LOCAL_AMOUNT).data(QtCore.Qt.ItemDataRole.UserRole)
                credit_currency_amount = self.table.item(row, COLUMN_CREDIT_LOCAL_AMOUNT).data(QtCore.Qt.ItemDataRole.UserRole)
                if debit_currency_amount:
                    debit_total += debit_currency_amount
                if credit_currency_amount:
                    credit_total += credit_currency_amount
            # 1for
            self.table.item(self.table.rowCount() - 1, COLUMN_DEBIT_LOCAL_AMOUNT).setText(str(debit_total))
            self.table.item(self.table.rowCount() - 1, COLUMN_DEBIT_LOCAL_AMOUNT).setData(QtCore.Qt.ItemDataRole.UserRole, debit_total)
            self.table.item(self.table.rowCount() - 1, COLUMN_CREDIT_LOCAL_AMOUNT).setText(str(credit_total))
            self.table.item(self.table.rowCount() - 1, COLUMN_CREDIT_LOCAL_AMOUNT).setData(QtCore.Qt.ItemDataRole.UserRole, credit_total)

        for row in range(self.table.rowCount()):
            if isRefreshNeeded(self.table.item(row, COLUMN_ACCOUNT)):
                account = self.table.item(row, COLUMN_ACCOUNT).data(QtCore.Qt.ItemDataRole.UserRole)
                if account and account.currency:
                    self.table.item(row, COLUMN_CURRENCY).setText(
                        account.currency.name
                    )
                    self.table.item(row, COLUMN_CURRENCY).setData(
                        QtCore.Qt.ItemDataRole.UserRole,
                        account.currency
                    )
                    self.table.item(row, COLUMN_EXCHANGE_RATE).setText(
                        str(FloatWithPrecision(
                            System.exchangeRate(account.currency.name, self.date_month).rate
                        ))
                    )
                    self.table.item(row, COLUMN_EXCHANGE_RATE).setData(
                        QtCore.Qt.ItemDataRole.UserRole,
                        System.exchangeRate(account.currency.name, self.date_month)
                    )
                    setDirty(self.table.item(row, COLUMN_EXCHANGE_RATE))
                else:
                    self.table.item(row, COLUMN_CURRENCY).setText("")
                    self.table.item(row, COLUMN_CURRENCY).setData(
                        QtCore.Qt.ItemDataRole.UserRole,
                        None
                    )
                    self.table.item(row, COLUMN_EXCHANGE_RATE).setText("")
                    self.table.item(row, COLUMN_EXCHANGE_RATE).setData(
                        QtCore.Qt.ItemDataRole.UserRole,
                        None
                    )
                    setDirty(self.table.item(row, COLUMN_EXCHANGE_RATE))

            if isRefreshNeeded(self.table.item(row, COLUMN_EXCHANGE_RATE)):
                refreshLocalAmount(row)

            if isRefreshNeeded(self.table.item(row, COLUMN_DEBIT_CURRENCY_AMOUNT)):
                self.table.item(row, COLUMN_CREDIT_CURRENCY_AMOUNT).setText("")
                self.table.item(row, COLUMN_CREDIT_CURRENCY_AMOUNT).setData(
                    QtCore.Qt.ItemDataRole.UserRole,
                    None
                )
                refreshLocalAmount(row)

            if isRefreshNeeded(self.table.item(row, COLUMN_CREDIT_CURRENCY_AMOUNT)):
                self.table.item(row, COLUMN_DEBIT_CURRENCY_AMOUNT).setText("")
                self.table.item(row, COLUMN_DEBIT_CURRENCY_AMOUNT).setData(
                    QtCore.Qt.ItemDataRole.UserRole,
                    None
                )
                refreshLocalAmount(row)

    def voucherEntries(self) -> tuple[list[VoucherEntry], list[VoucherEntry]]:
        """
        Returns debit and credit voucher entries
        """
        debit_entries = []
        credit_entries = []
        for row in range(self.table.rowCount() - 1):
            brief = self.table.item(row, COLUMN_BRIEF).text()
            account = self.table.item(row, COLUMN_ACCOUNT).data(QtCore.Qt.ItemDataRole.UserRole)
            currency = self.table.item(row, COLUMN_CURRENCY).data(QtCore.Qt.ItemDataRole.UserRole)
            exchange_rate = self.table.item(row, COLUMN_EXCHANGE_RATE).data(QtCore.Qt.ItemDataRole.UserRole)
            debit_amount = self.table.item(row, COLUMN_DEBIT_CURRENCY_AMOUNT).data(QtCore.Qt.ItemDataRole.UserRole)
            credit_amount = self.table.item(row, COLUMN_CREDIT_CURRENCY_AMOUNT).data(QtCore.Qt.ItemDataRole.UserRole)
            if account and currency and exchange_rate and (debit_amount or credit_amount):
                if debit_amount:
                    debit_entries.append(
                        VoucherEntry(
                        account_code=account.code,
                        amount=debit_amount.value,
                        brief=brief
                        )
                    )
                else:
                    credit_entries.append(
                        VoucherEntry(
                            account_code=account.code,
                            amount=credit_amount.value,
                            brief=brief
                        )
                    )
        return debit_entries, credit_entries
