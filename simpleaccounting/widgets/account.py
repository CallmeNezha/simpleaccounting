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

from qtpy import QtWidgets, QtCore, QtGui
from simpleaccounting.widgets.qwidgets import CustomInputDialog, CustomQDialog, HorizontalSpacer
from simpleaccounting.app.system import System, IllegalOperation, EntryNotFound


class AccountCreateDialog(CustomInputDialog):

    def __init__(self, on_accept=lambda b: ...):
        super().__init__()
        self.setupUI()
        self.on_accept = on_accept

    def setupUI(self):
        self.setWindowTitle("创建科目")
        self.lineedit_code = QtWidgets.QLineEdit()
        self.lineedit_name = QtWidgets.QLineEdit()
        form = QtWidgets.QFormLayout()
        form.addRow("科目代码", self.lineedit_code)
        form.addRow("科目名称", self.lineedit_name)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(form)
        vbox.addWidget(self.button_box)

    def accept(self):
        code = self.lineedit_code.text().strip()
        name = self.lineedit_name.text().strip()
        if not code:
            QtWidgets.QMessageBox.critical(None, "创建失败", "错误：代码项不可为空")
            return
        if not name:
            QtWidgets.QMessageBox.critical(None, "创建失败", "错误：名称项不可为空")
            return
        if self.on_accept((code, name)):
            super().accept()


class AccountActivateDialog(CustomInputDialog):

    def __init__(self, name: str, code:str, on_accept=lambda b: ...):
        super().__init__()
        self.setupUI()
        for currency in System.currencies():
            self.combobox.addItem(currency.name)
        # !for
        self.setWindowTitle(f"启用科目: {name}({code})")
        self.on_accept = on_accept

    def setupUI(self):
        self.setWindowTitle("启用科目")
        self.combobox = QtWidgets.QComboBox()
        form = QtWidgets.QFormLayout()
        form.addRow("币种", self.combobox)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(QtWidgets.QLabel("启用操作不可撤销，科目不可删除"))
        vbox.addLayout(form)
        vbox.addWidget(self.button_box)

    def accept(self):
        currency = self.combobox.currentText()
        if self.on_accept(currency):
            super().accept()


class AccountDialog(CustomQDialog):

    def __init__(self):
        super().__init__()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        """"""
        self.setWindowTitle("科目管理")

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.header().setStretchLastSection(True)
        self.tree.currentItemChanged.connect(self.on_select)

        self.action_create = QtWidgets.QAction("创建")
        self.action_create.triggered.connect(self.on_add)
        self.action_create.setEnabled(False)

        self.action_delete = QtWidgets.QAction("删除")
        self.action_delete.triggered.connect(self.on_delete)
        self.action_delete.setEnabled(False)

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.addWidget(HorizontalSpacer())
        self.toolbar.addAction(self.action_create)
        self.toolbar.addAction(self.action_delete)
        #
        self.widget_branch_property = QtWidgets.QWidget()

        form_branch_property = QtWidgets.QFormLayout(self.widget_branch_property)
        self.label_branch_code = QtWidgets.QLabel()
        self.label_branch_name = QtWidgets.QLabel()
        self.label_branch_major_category = QtWidgets.QLabel()
        self.label_branch_sub_category = QtWidgets.QLabel()
        self.label_branch_balance_direction = QtWidgets.QLabel()
        form_branch_property.addRow("大类", self.label_branch_major_category)
        form_branch_property.addRow("类别", self.label_branch_sub_category)
        form_branch_property.addRow("代码", self.label_branch_code)
        form_branch_property.addRow("名称", self.label_branch_name)
        form_branch_property.addRow("余额方向", self.label_branch_balance_direction)
        #
        self.widget_leaf_property = QtWidgets.QWidget()
        form_leaf_property = QtWidgets.QFormLayout(self.widget_leaf_property)
        self.label_leaf_code = QtWidgets.QLabel()
        self.label_leaf_name = QtWidgets.QLabel()
        self.label_leaf_major_category = QtWidgets.QLabel()
        self.label_leaf_sub_category = QtWidgets.QLabel()
        self.label_leaf_balance_direction = QtWidgets.QLabel()
        self.button_leaf_activate = QtWidgets.QPushButton("启用")
        self.button_leaf_activate.clicked.connect(self.on_activate)
        self.button_leaf_activate.setEnabled(False)
        form_leaf_property.addRow("大类", self.label_leaf_major_category)
        form_leaf_property.addRow("类别", self.label_leaf_sub_category)
        form_leaf_property.addRow("代码", self.label_leaf_code)
        form_leaf_property.addRow("名称", self.label_leaf_name)
        form_leaf_property.addRow("余额方向", self.label_leaf_balance_direction)
        form_leaf_property.addRow("", self.button_leaf_activate)
        #
        self.widget_activated_leaf_property = QtWidgets.QWidget()
        form_activated_leaf_property = QtWidgets.QFormLayout(self.widget_activated_leaf_property)
        self.label_activated_leaf_code = QtWidgets.QLabel()
        self.label_activated_leaf_name = QtWidgets.QLabel()
        self.label_activated_leaf_major_category = QtWidgets.QLabel()
        self.label_activated_leaf_sub_category = QtWidgets.QLabel()
        self.label_activated_leaf_balance_direction = QtWidgets.QLabel()
        self.label_activated_leaf_currency = QtWidgets.QLabel()
        form_activated_leaf_property.addRow("大类", self.label_activated_leaf_major_category)
        form_activated_leaf_property.addRow("类别", self.label_activated_leaf_sub_category)
        form_activated_leaf_property.addRow("代码", self.label_activated_leaf_code)
        form_activated_leaf_property.addRow("名称", self.label_activated_leaf_name)
        form_activated_leaf_property.addRow("余额方向", self.label_activated_leaf_balance_direction)
        form_activated_leaf_property.addRow("币种", self.label_activated_leaf_currency)

        self.stacked = QtWidgets.QStackedWidget()
        self.widget_empty = QtWidgets.QWidget()
        self.stacked.addWidget(self.widget_empty)
        self.stacked.addWidget(self.widget_branch_property)
        self.stacked.addWidget(self.widget_leaf_property)
        self.stacked.addWidget(self.widget_activated_leaf_property)

        vbox = QtWidgets.QVBoxLayout(self)
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.tree)
        splitter.addWidget(self.stacked)
        vbox.addWidget(self.toolbar)
        vbox.addWidget(splitter)

    def updateUI(self):
        """"""
        items = {}
        self.tree.setHeaderLabels(["代码", "名称"])

        for account in System.accounts():
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, account.code)
            item.setText(1, account.name)
            item.setData(0, QtCore.Qt.UserRole, account)
            items[account.code] = item

        for code, item in items.items():
            account = item.data(0, QtCore.Qt.UserRole)
            if account.parent:
                items[account.parent.code].addChild(item)
            else:
                self.tree.addTopLevelItem(item)

    def on_select(self, current, previous):
        """"""
        self.action_create.setEnabled(False)
        self.action_delete.setEnabled(False)

        if current is None:
            self.stacked.setCurrentWidget(self.widget_empty)

        account = current.data(0, QtCore.Qt.UserRole)

        if account.children:
            self.stacked.setCurrentWidget(self.widget_branch_property)
            self.label_branch_code.setText(account.code)
            self.label_branch_name.setText(account.name)
            self.label_branch_major_category.setText(account.major_category)
            self.label_branch_sub_category.setText(account.sub_category)
            self.label_branch_balance_direction.setText(account.direction)
            self.action_create.setEnabled(True)
        else:
            currency = account.currency
            if not currency:
                self.stacked.setCurrentWidget(self.widget_leaf_property)
                self.label_leaf_code.setText(account.code)
                self.label_leaf_name.setText(account.name)
                self.label_leaf_balance_direction.setText(account.direction)
                self.label_leaf_major_category.setText(account.major_category)
                self.label_leaf_sub_category.setText(account.sub_category)
                self.button_leaf_activate.setEnabled(True)
                self.action_create.setEnabled(True)
                self.action_delete.setEnabled(account.custom)
            else:
                self.stacked.setCurrentWidget(self.widget_activated_leaf_property)
                self.label_activated_leaf_code.setText(account.code)
                self.label_activated_leaf_name.setText(account.name)
                self.label_activated_leaf_balance_direction.setText(account.direction)
                self.label_activated_leaf_major_category.setText(account.major_category)
                self.label_activated_leaf_sub_category.setText(account.sub_category)
                self.label_activated_leaf_currency.setText(currency.name)
                self.action_create.setEnabled(False)
                self.action_delete.setEnabled(False)

    def on_add(self):
        """"""
        item = self.tree.currentItem()
        if not item:
            return

        def add(data) -> bool:

            code, name = data
            code_parent = '.'.join(code.split('.')[:-1])

            try:
                System.createAccount(
                    code_parent,
                    code,
                    name
                )
            except IllegalOperation as e:
                if e.args[0] == 'A1.2.1.2/1':
                    QtWidgets.QMessageBox.critical(None, "创建失败",
                                                   "错误代码 A1.2.1.2/1："
                                                   "会计科目代码由多位数字组成。编码结构采用层级分隔符 '.' 来表示科目的层级关系。"
                                                   "每个层级的编码长度和具体内容根据科目设置的层级深度和详细度而定。")
                elif e.args[0] == 'A1.2.1/2':
                    QtWidgets.QMessageBox.critical(None, "创建失败",
                                                   "错误代码 A1.2.1/2："
                                                   "一级科目除规定的标准科目外，不可新增。")
                elif e.args[0] == 'A1.2.1/4':
                    QtWidgets.QMessageBox.critical(None, "创建失败",
                                                   "错误代码 A1.2.1/8："
                                                   "会计科目应具有唯一的科目名称。")
                elif e.args[0] == 'A1.1/2':
                    QtWidgets.QMessageBox.critical(None, "创建失败",
                                                   "错误代码 A1.1/2："
                                                   "科目应具有唯一的科目代码。")
                return False

            item_parent = self.tree.currentItem()
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, code)
            item.setText(1, name)
            item.setData(0, QtCore.Qt.UserRole, System.account(code))
            item_parent.addChild(item)
            self.tree.setCurrentItem(item)
            return True

        dialog = AccountCreateDialog(add)
        account = item.data(0, QtCore.Qt.UserRole)
        dialog.lineedit_code.setText(account.code + '.')
        dialog.exec_()

    def on_delete(self):
        """"""
        item = self.tree.currentItem()
        if not item:
            return

        account = item.data(0, QtCore.Qt.UserRole)
        try:
            System.deleteAccount(account.code)
        except EntryNotFound as e:
            QtWidgets.QMessageBox.critical(
                None,
                "删除失败",
                f"错误：项\"{e}\"未找到。"
            )
            return
        except IllegalOperation as e:
            if e.args[0] == 'A1.2.1/5':
                QtWidgets.QMessageBox.critical(
                    None,
                    "刪除失敗",
                    "錯誤代碼 A1.2.1/5：使用中的末级科目不可删除。"
                )
            elif e.args[1] == 'A1.1/5':
                QtWidgets.QMessageBox.critical(
                    None,
                    "刪除失敗",
                    "錯誤代碼 A1.1/5：标准科目表中规定的科目不可删除。"
                )
            elif e.args[2] == 'A1.2.1/6':
                QtWidgets.QMessageBox.critical(
                    None,
                    "刪除失敗",
                    "錯誤代碼 A1.2.1/6：分类科目不可删除。"
                )
            return

        parent = item.parent()
        parent.removeChild(item)
        self.on_select(parent, None)
    #
    def on_activate(self):
        """"""
        item = self.tree.currentItem()
        if not item:
            return

        account = item.data(0, QtCore.Qt.UserRole)
        if account.currency:
            return

        def activate(currency: str):
            item = self.tree.currentItem()
            if not item:
                return False
            # !if
            account = item.data(0, QtCore.Qt.UserRole)
            System.setAccountCurrency(account.code, currency)
            self.on_select(item, item)
            return True

        dialog = AccountActivateDialog(account.name, account.code, activate)
        dialog.exec_()



