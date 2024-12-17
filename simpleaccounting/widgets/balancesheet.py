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

from simpleaccounting.tools.dateutil import last_day_of_month, qdate_to_date
from simpleaccounting.widgets.qwidgets import HorizontalSpacer, CustomInputDialog
from simpleaccounting.app.system import System

import typing

def newname(name: str, exisitingNames: typing.Iterable[str]):
    """
    :param name:
    :param exisitingNames:
    :return:

    >>> assert newname("main", ["main", "main (1)"]) == "main (2)"
    """
    if name in exisitingNames:
        i = 1
        newName = f'{name} ({i})'
        while newName in exisitingNames:
            i += 1
            newName = f'{name} ({i})'
        #
        name = newName
    #
    return name

COLUMN_ASSET_NAME = 0
COLUMN_ASSET_LINENO = 1
COLUMN_ASSET_ENDING_BALANCE = 2
COLUMN_ASSET_LAST_YEAR_ENDING_BALANCE = 3
COLUMN_LIABILITY_NAME = 4
COLUMN_LIABILITY_LINENO = 5
COLUMN_LIABILITY_ENDING_BALANCE = 6
COLUMN_LIABILITY_LAST_YEAR_ENDING_BALANCE = 7
COLUMN_COUNT = 8


class BalanceSheetWidget(QtWidgets.QWidget):
    """"""
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        """"""
        # ---
        self.setWindowTitle('资产负债表')
        # ---
        self.action_edit_template = QtWidgets.QAction(QtGui.QIcon(":/icons/edit-property.png"), "编辑模板")
        self.action_edit_template.triggered.connect(self.on_action_editTemplateTriggered)
        self.action_pull = QtWidgets.QAction(QtGui.QIcon(":/icons/persistenceEntity.svg"), "拉取", self)
        self.action_pull.triggered.connect(self.on_action_pullTriggered)
        # ---
        self.de_until = QtWidgets.QDateEdit()
        self.de_until.setDate(last_day_of_month(System.meta().month_until))
        self.cb_template = QtWidgets.QComboBox()
        # --- layout
        container = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout(container)
        hbox.addWidget(QtWidgets.QLabel("模板"))
        hbox.addWidget(self.cb_template)
        hbox.addWidget(QtWidgets.QLabel("截止日期"))
        hbox.addWidget(self.de_until)
        self.tbar = QtWidgets.QToolBar()
        self.tbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.tbar.addAction(self.action_edit_template)
        self.tbar.addWidget(HorizontalSpacer())
        self.tbar.addWidget(container)
        self.tbar.addSeparator()
        self.tbar.addAction(self.action_pull)
        self.table = QtWidgets.QTableWidget()
        self.table.verticalHeader().setHidden(True)
        self.table.setColumnCount(COLUMN_COUNT)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.tbar)
        vbox.addWidget(self.table)

    def updateUI(self):
        """"""
        self.cb_template.clear()
        for bste in System.balanceSheetTemplates():
            self.cb_template.addItem(bste.name, bste)
        # 1for
        self.clearTable()

    def clearTable(self):
        """"""
        self.table.clear()
        self.table.setHorizontalHeaderLabels(["资产", "行次",
                                              "期末余额", "上年年末余额",
                                              "负债和所有者权益\n(或股东权益)", "行次",
                                              "期末余额", "上年年末余额"])
        self.table.setRowCount(80)
        COLUMN_WIDTHS = [30, 10, 20, 20, 30, 10, 20, 20]
        for i in range(len(COLUMN_WIDTHS)):
            self.table.setColumnWidth(i, self.fontMetrics().horizontalAdvance('9' * COLUMN_WIDTHS[i]))
            self.table.setColumnWidth(i, self.fontMetrics().horizontalAdvance('9' * COLUMN_WIDTHS[i]))
        # 1for

    def updateTable(self):
        """"""
        self.clearTable()
        #
        bste = self.cb_template.currentData(QtCore.Qt.UserRole)
        if not bste:
            return
        # 1if
        asset_entries = [e for e in bste.entries if e.category == '资产']
        liability_entries = [e for e in bste.entries if e.category == '负债和所有者权益（或股东权益）']
        for i, (left, right) in enumerate(zip(asset_entries, liability_entries)):
            for j in range(COLUMN_COUNT):
                item = QtWidgets.QTableWidgetItem("")
                item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.table.setItem(i, j, item)
                if j == COLUMN_ASSET_NAME:
                    item.setText(left.item)
                    if left.line_number is None:
                        font = item.font()
                        font.setBold(True)
                        item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                        item.setFont(font)
                    else:
                        item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                    # 1if
                elif j == COLUMN_LIABILITY_NAME:
                    item.setText(right.item)
                    if right.line_number is None:
                        font = item.font()
                        font.setBold(True)
                        item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                        item.setFont(font)
                    else:
                        item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                    # 1if
                elif j == COLUMN_ASSET_LINENO:
                    item.setText(str(left.line_number)) if left.line_number else ...
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                elif j == COLUMN_LIABILITY_LINENO:
                    item.setText(str(right.line_number)) if right.line_number else ...
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
            # 1for
        # 1for
        date = qdate_to_date(self.de_until.date())
        self.setWindowTitle(f"{date.strftime('%Y年度')}资产负债表")
        #!
        bste = self.cb_template.currentData(QtCore.Qt.UserRole)
        asset_entries = [e for e in bste.entries if e.category == '资产']
        liability_entries = [e for e in bste.entries if e.category == '负债和所有者权益（或股东权益）']
        #!
        beginnings, endings = System.balanceSheet(bste, date)
        #!
        for i, (left, right) in enumerate(zip(asset_entries, liability_entries)):
            if lineno := left.line_number:
                beginning, ending = beginnings[lineno], endings[lineno]
                if beginning is not None and ending is not None:
                    self.table.item(i, COLUMN_ASSET_LAST_YEAR_ENDING_BALANCE).setText(str(beginning))
                    self.table.item(i, COLUMN_ASSET_ENDING_BALANCE).setText(str(ending))

            if lineno := right.line_number:
                beginning, ending = beginnings[lineno], endings[lineno]
                if beginning is not None and ending is not None:
                    self.table.item(i, COLUMN_LIABILITY_LAST_YEAR_ENDING_BALANCE).setText(str(beginning))
                    self.table.item(i, COLUMN_LIABILITY_ENDING_BALANCE).setText(str(ending))
        # 1for
        self.table.resizeRowsToContents()

    def on_action_editTemplateTriggered(self):
        dialog = BalanceSheetTemplateDialog()
        dialog.resize(1600, 600)
        dialog.exec_()
        self.updateUI()

    def on_action_pullTriggered(self):
        """"""
        self.updateTable()


class BalanceSheetTemplateDialog(CustomInputDialog):

    COLUMN_ASSET_NAME = 0
    COLUMN_ASSET_LINENO = 1
    COLUMN_ASSET_FORMULAR = 2
    COLUMN_LIABILITY_NAME = 3
    COLUMN_LIABILITY_LINENO = 4
    COLUMN_LIABILITY_FORMULAR = 5

    def __init__(self):
        super().__init__()
        self.model = QtGui.QStandardItemModel()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        # ---
        self.action_add = QtWidgets.QAction(QtGui.QIcon(":/icons/add.png"), "添加")
        self.action_add.triggered.connect(self.on_action_addTriggered)
        self.action_rm = QtWidgets.QAction(QtGui.QIcon(":/icons/remove.png"), "删除")
        self.action_rm.triggered.connect(self.on_action_removeTriggered)
        self.action_copy = QtWidgets.QAction(QtGui.QIcon(":/icons/copy.png"), "拷贝")
        self.action_copy.triggered.connect(self.on_action_copyTriggered)
        self.action_rename = QtWidgets.QAction(QtGui.QIcon(":/icons/rename.png"), "重命名")
        self.action_rename.triggered.connect(self.on_action_renameTriggered)

        self.tbar = QtWidgets.QToolBar()
        self.tbar.addActions([self.action_add, self.action_rm, self.action_copy, self.action_rename])
        self.list = QtWidgets.QListWidget()
        self.list.currentItemChanged.connect(self.on_list_currentItemChanged)
        container = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(container)
        vbox.addWidget(self.tbar)
        vbox.addWidget(self.list)
        self.table = QtWidgets.QTableView()
        self.table.setModel(self.model)
        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(container)
        self.splitter.addWidget(self.table)
        self.splitter.setSizes([150, 600])
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.splitter)
        self.apply_button = self.button_box.addButton(QtWidgets.QDialogButtonBox.StandardButton.Apply)
        self.apply_button.clicked.connect(self.on_applyButtonClicked)
        self.apply_button.setEnabled(False)
        self.model.itemChanged.connect(lambda *args: self.apply_button.setEnabled(True))
        vbox.addWidget(self.button_box)
        # ---
        self.action_copy.setEnabled(False)
        self.action_rm.setEnabled(False)
        self.action_rename.setEnabled(False)
        self.table.setEnabled(False)

    def updateUI(self):
        self.list.clear()
        for bste in System.balanceSheetTemplates():
            self.list.addItem(bste.name)
        # 1for

    def on_applyButtonClicked(self, button):
        self.saveCurrent()
        self.apply_button.setEnabled(False)

    def accept(self):
        """"""
        self.saveCurrent()
        super().accept()

    def saveCurrent(self):
        """"""
        if not self.list.currentItem():
            return

        asset_end_line = 0
        for r in reversed(range(self.model.rowCount())):
            if self.model.item(r, self.COLUMN_ASSET_NAME):
                asset_end_line = r + 1
                break
        # 1if
        liability_end_line = 0
        for r in reversed(range(self.model.rowCount())):
            if self.model.item(r, self.COLUMN_LIABILITY_NAME):
                liability_end_line = r + 1
                break
        # 1if

        asset_entries = []
        for r in range(asset_end_line):
            name = self.model.item(r, self.COLUMN_ASSET_NAME).text().strip() if self.model.item(r, self.COLUMN_ASSET_NAME) else ''
            lineno_str = self.model.item(r, self.COLUMN_ASSET_LINENO).text().strip() if self.model.item(r, self.COLUMN_ASSET_LINENO) else None
            try:
                lineno = int(lineno_str)
            except ValueError:
                lineno = None
            formula = self.model.item(r, self.COLUMN_ASSET_FORMULAR).text().strip() if self.model.item(r, self.COLUMN_ASSET_FORMULAR) else ''
            formula = formula if formula else None
            asset_entries.append((name, lineno, formula))

        liability_entries = []
        for r in range(liability_end_line):
            name = self.model.item(r, self.COLUMN_LIABILITY_NAME).text().strip() if self.model.item(r, self.COLUMN_LIABILITY_NAME) else ''
            lineno_str = self.model.item(r, self.COLUMN_LIABILITY_LINENO).text().strip() if self.model.item(r, self.COLUMN_LIABILITY_LINENO) else None
            try:
                lineno = int(lineno_str)
            except ValueError:
                lineno = None
            formula = self.model.item(r, self.COLUMN_LIABILITY_FORMULAR).text().strip() if self.model.item(r, self.COLUMN_LIABILITY_FORMULAR) else ''
            formula = formula if formula else None
            liability_entries.append((name, lineno, formula))
        # 1for
        bste_name = self.list.currentItem().text()
        System.updateBalanceSheetTemplate(bste_name, asset_entries, liability_entries)


    def on_list_currentItemChanged(self, item):
        """"""
        if item and item.text() == '默认':
            self.action_rm.setEnabled(False)
            self.action_rename.setEnabled(False)
            self.action_copy.setEnabled(True)
            self.table.setEnabled(True)
        else:
            self.action_copy.setEnabled(bool(item))
            self.action_rm.setEnabled(bool(item))
            self.action_rename.setEnabled(bool(item))
            self.table.setEnabled(bool(item))
        #
        self.model.clear()
        self.model.setColumnCount(4)
        self.model.setHorizontalHeaderLabels(['资产', '行次', '余额计算公式', '负债和所有者权益', '行次', '余额计算公式'])
        #
        for i, width in enumerate([300, 60, 300, 300, 60, 300]):
            self.table.setColumnWidth(i, width)
        # 1for
        self.model.setRowCount(100)
        if item:
            if bste := next((t for t in System.balanceSheetTemplates() if t.name == item.text()), None):
                asset_entries = [e for e in bste.entries if e.category == '资产']
                liability_entries = [e for e in bste.entries if e.category == '负债和所有者权益（或股东权益）']
                for i, (asset, liability) in enumerate(zip(asset_entries, liability_entries)):
                    self.model.setItem(i, self.COLUMN_ASSET_NAME, QtGui.QStandardItem(asset.item))
                    self.model.setItem(i, self.COLUMN_ASSET_LINENO, QtGui.QStandardItem(str(asset.line_number) if asset.line_number else ''))
                    self.model.setItem(i, self.COLUMN_ASSET_FORMULAR, QtGui.QStandardItem(asset.formula))
                    self.model.setItem(i, self.COLUMN_LIABILITY_NAME, QtGui.QStandardItem(liability.item))
                    self.model.setItem(i, self.COLUMN_LIABILITY_LINENO, QtGui.QStandardItem(str(liability.line_number) if liability.line_number else ''))
                    self.model.setItem(i, self.COLUMN_LIABILITY_FORMULAR, QtGui.QStandardItem(liability.formula))
        # 1if
        # model change will set apply button to enabled state, we must set it back since model is updated by the above code
        self.apply_button.setEnabled(False)

    def on_action_renameTriggered(self):
        item = self.list.currentItem()
        text = ''
        while not text.strip():
            text = item.text()
            text, ok = QtWidgets.QInputDialog.getText(self, '重命名', '名称:', text=text)
            if not ok:
                return

            if not text.strip():
                QtWidgets.QMessageBox.critical(None, "重命名失败", "名称不可为空")

            if text.strip() in [t.name for t in System.balanceSheetTemplates()]:
                QtWidgets.QMessageBox.critical(None, "重命名失败", "名称已存在")
                text = ''
        # 1while
        System.changeBalanceSheetTemplateName(item.text(), text.strip())
        self.updateUI()

    def on_action_copyTriggered(self):
        item = self.list.currentItem()
        new_name = newname(item.text(), [t.name for t in System.balanceSheetTemplates()])
        System.createBalanceSheetTemplate(new_name)
        bste = System.balanceSheetTemplate(item.text())
        asset_entries = [(e.item, e.line_number, e.formula) for e in bste.entries if e.category == '资产']
        liability_entries = [(e.item, e.line_number, e.formula) for e in bste.entries if e.category == '负债和所有者权益（或股东权益）']
        System.updateBalanceSheetTemplate(new_name, asset_entries, liability_entries)
        self.updateUI()

    def on_action_addTriggered(self):
        text = ''
        while not text.strip():
            text, ok = QtWidgets.QInputDialog.getText(self, '添加', '名称:')
            if not ok:
                return

            if not text.strip():
                QtWidgets.QMessageBox.critical(None, "添加失败", "名称不可为空")

            if text.strip() in [t.name for t in System.balanceSheetTemplates()]:
                QtWidgets.QMessageBox.critical(None, "添加失败", "名称已存在")
                text = ''
        # 1while
        System.createBalanceSheetTemplate(text.strip())
        self.updateUI()

    def on_action_removeTriggered(self):
        item = self.list.currentItem()
        System.deleteBalanceSheetTemplate(item.text())
        self.updateUI()
