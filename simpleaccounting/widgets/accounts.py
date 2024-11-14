from qtpy import QtWidgets, QtCore, QtGui
from simpleaccounting.widgets.qwidgets import CustomInputDialog, CustomQDialog, HorizontalSpacer
from simpleaccounting.app.system import System


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
            QtWidgets.QMessageBox.critical(None, "创建失败", "代码项不可为空")
            return

        if not name:
            QtWidgets.QMessageBox.critical(None, "创建失败", "名称项不可为空")
            return

        if self.on_accept((code, name)):
            super().accept()

#
# class AccountActivateDialog(QtWidgets.QDialog):
#
#     def __init__(self, on_accept=lambda b: ...):
#         super().__init__()
#         self.setupUI()
#         self.on_accept = on_accept
#
#
#     def setupUI(self):
#         self.setWindowTitle("启用科目")
#         self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint |
#                             QtCore.Qt.WindowCloseButtonHint |
#                             QtCore.Qt.CustomizeWindowHint)
#         self.setModal(True)
#
#         self.combobox_currency = QtWidgets.QComboBox()
#
#         # 创建按钮框
#         bbox = QtWidgets.QDialogButtonBox(self)
#         bbox.addButton(QtWidgets.QDialogButtonBox.Ok)  # 添加“确定”按钮
#         bbox.addButton(QtWidgets.QDialogButtonBox.Cancel)  # 添加“取消”按钮
#         bbox.accepted.connect(self.accept)  # 点击“确定”时接受对话框
#         bbox.rejected.connect(self.reject)  # 点击“取消”时拒绝对话框
#
#         form = QtWidgets.QFormLayout()
#         form.addRow("币种", self.combobox_currency)
#
#         vbox = QtWidgets.QVBoxLayout(self)
#         vbox.addWidget(QtWidgets.QLabel("启用操作不可撤销，科目不可删除"))
#         vbox.addLayout(form)
#         vbox.addWidget(bbox)
#
#         self.updateUI()
#
#     def updateUI(self):
#         with FFDB.db_session:
#             for currency in FFDB.db.Currency.select():
#                 self.combobox_currency.addItem(currency.name)
#
#     def accept(self):
#         currency = self.combobox_currency.currentText()
#         if self.on_accept(currency):
#             super().accept()


class AccountDialog(CustomQDialog):

    def __init__(self):
        super().__init__()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        self.setWindowTitle("科目管理")

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.header().setStretchLastSection(True)
        # self.tree.currentItemChanged.connect(self.on_select)

        self.action_create = QtWidgets.QAction("创建")
        # self.action_create.triggered.connect(self.on_add)
        self.action_create.setEnabled(False)

        self.action_delete = QtWidgets.QAction("删除")
        # self.action_delete.triggered.connect(self.on_delete)
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
        self.label_branch_type = QtWidgets.QLabel()
        self.label_branch_category = QtWidgets.QLabel()
        self.label_branch_balance_direction = QtWidgets.QLabel()
        form_branch_property.addRow("大类", self.label_branch_type)
        form_branch_property.addRow("类别", self.label_branch_category)
        form_branch_property.addRow("代码", self.label_branch_code)
        form_branch_property.addRow("名称", self.label_branch_name)
        form_branch_property.addRow("余额方向", self.label_branch_balance_direction)
        #
        self.widget_leaf_property = QtWidgets.QWidget()
        form_leaf_property = QtWidgets.QFormLayout(self.widget_leaf_property)
        self.label_leaf_code = QtWidgets.QLabel()
        self.label_leaf_name = QtWidgets.QLabel()
        self.label_leaf_type = QtWidgets.QLabel()
        self.label_leaf_category = QtWidgets.QLabel()
        self.label_leaf_balance_direction = QtWidgets.QLabel()
        self.button_leaf_activate = QtWidgets.QPushButton("启用")
        # self.button_leaf_activate.clicked.connect(self.on_activate)
        self.button_leaf_activate.setEnabled(False)
        form_leaf_property.addRow("大类", self.label_leaf_type)
        form_leaf_property.addRow("类别", self.label_leaf_category)
        form_leaf_property.addRow("代码", self.label_leaf_code)
        form_leaf_property.addRow("名称", self.label_leaf_name)
        form_leaf_property.addRow("余额方向", self.label_leaf_balance_direction)
        form_leaf_property.addRow("", self.button_leaf_activate)
        #
        self.widget_activated_leaf_property = QtWidgets.QWidget()
        form_activated_leaf_property = QtWidgets.QFormLayout(self.widget_activated_leaf_property)
        self.label_activated_leaf_code = QtWidgets.QLabel()
        self.label_activated_leaf_name = QtWidgets.QLabel()
        self.label_activated_leaf_type = QtWidgets.QLabel()
        self.label_activated_leaf_category = QtWidgets.QLabel()
        self.label_activated_leaf_balance_direction = QtWidgets.QLabel()
        self.label_activated_leaf_currency = QtWidgets.QLabel()
        self.label_activated_leaf_ending_balance_currency = QtWidgets.QLabel()
        self.label_activated_leaf_ending_balance_local_currency = QtWidgets.QLabel()
        self.label_activated_leaf_ending_balance_date = QtWidgets.QLabel()
        form_activated_leaf_property.addRow("大类", self.label_activated_leaf_type)
        form_activated_leaf_property.addRow("类别", self.label_activated_leaf_category)
        form_activated_leaf_property.addRow("代码", self.label_activated_leaf_code)
        form_activated_leaf_property.addRow("名称", self.label_activated_leaf_name)
        form_activated_leaf_property.addRow("余额方向", self.label_activated_leaf_balance_direction)
        form_activated_leaf_property.addRow("币种", self.label_activated_leaf_currency)
        form_activated_leaf_property.addRow("币种余额", self.label_activated_leaf_ending_balance_currency)
        form_activated_leaf_property.addRow("本位币余额", self.label_activated_leaf_ending_balance_local_currency)
        form_activated_leaf_property.addRow("余额日期", self.label_activated_leaf_ending_balance_date)

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

    # def add(self, data) -> bool:
    #     code, name, category = data
    #     item_parent = self.tree.currentItem()
    #
    #     with FFDB.db_session:
    #         if FFDB.db.Account.get(code=str(code)):
    #             QtWidgets.QMessageBox.critical(None, "增加失败", "科目代码已存在")
    #             return False
    #
    #         if FFDB.db.Account.get(name=name):
    #             QtWidgets.QMessageBox.critical(None, "增加失败", "科目名称已存在")
    #             return False
    #
    #         parent_code: AccountCode = item_parent.data(0, QtCore.Qt.UserRole)
    #         account_parent = FFDB.db.Account.get(code=str(parent_code))
    #
    #         if account_parent.activated:
    #             QtWidgets.QMessageBox.critical(None, "增加失败", "无法在已启用的科目下增加细分科目")
    #             return False
    #
    #         if not AccountCode(account_parent.code).isChild(code):
    #             QtWidgets.QMessageBox.critical(None, "增加失败", "科目代码前缀必须跟从父科目")
    #             return False
    #
    #         if not FFDB.db.AccountCategory.get(name=category):
    #             FFDB.db.AccountCategory(name=category)
    #
    #         FFDB.db.Account(
    #             code=str(code),
    #             name=name,
    #             type=account_parent.type,
    #             category=FFDB.db.AccountCategory.get(name=category),
    #             direction=account_parent.direction,
    #             parent=account_parent
    #         )
    #
    #         FFDB.db.EndingBalance(
    #             account=FFDB.db.Account.get(code=str(code)),
    #             currency_amount=0.0,
    #             local_currency_amount=0.0,
    #             date=last_day_of_previous_month(FFDB.db.MetaData.select().first().date_until)
    #         )
    #
    #         item = QtWidgets.QTreeWidgetItem()
    #         item.setText(0, str(code))
    #         item.setText(1, name)
    #         item.setData(0, QtCore.Qt.UserRole, code)
    #         item_parent.addChild(item)
    #         self.tree.setCurrentItem(item)
    #         return True
    #
    # def on_select(self, current, previous):
    #     self.action_create.setEnabled(False)
    #     self.action_delete.setEnabled(False)
    #
    #     item = current
    #     if item and item.childCount():
    #         self.stacked.setCurrentWidget(self.widget_branch_property)
    #         with FFDB.db_session:
    #             code: AccountCode = item.data(0, QtCore.Qt.UserRole)
    #             account = FFDB.db.Account.get(code=str(code))
    #             self.label_branch_code.setText(account.code)
    #             self.label_branch_name.setText(account.name)
    #             self.label_branch_balance_direction.setText(account.direction)
    #             self.label_branch_type.setText(account.type)
    #             self.label_branch_category.setText(account.category.name)
    #
    #         self.action_create.setEnabled(True)
    #
    #     elif item:
    #         with FFDB.db_session:
    #             code: AccountCode = item.data(0, QtCore.Qt.UserRole)
    #             account = FFDB.db.Account.get(code=str(code))
    #
    #             if not account.activated:
    #                 self.stacked.setCurrentWidget(self.widget_leaf_property)
    #                 self.label_leaf_code.setText(account.code)
    #                 self.label_leaf_name.setText(account.name)
    #                 self.label_leaf_balance_direction.setText(account.direction)
    #                 self.label_leaf_type.setText(account.type)
    #                 self.label_leaf_category.setText(account.category.name)
    #                 self.button_leaf_activate.setEnabled(not account.activated)
    #                 self.action_create.setEnabled(True)
    #                 self.action_delete.setEnabled(account.custom)
    #             else:
    #                 last_ending_balance = FFDB.db.EndingBalance.select(account=account).order_by(FFDB.db.EndingBalance.date.desc()).first()
    #                 self.stacked.setCurrentWidget(self.widget_activated_leaf_property)
    #                 self.label_activated_leaf_code.setText(account.code)
    #                 self.label_activated_leaf_name.setText(account.name)
    #                 self.label_activated_leaf_balance_direction.setText(account.direction)
    #                 self.label_activated_leaf_type.setText(account.type)
    #                 self.label_activated_leaf_category.setText(account.category.name)
    #                 self.label_activated_leaf_currency.setText(account.currency.name)
    #                 self.label_activated_leaf_ending_balance_currency.setText(str(FloatWithPrecision(last_ending_balance.currency_amount)))
    #                 self.label_activated_leaf_ending_balance_local_currency.setText(str(FloatWithPrecision(last_ending_balance.local_currency_amount)))
    #                 self.label_activated_leaf_ending_balance_date.setText(last_ending_balance.date.strftime("%Y.%m.%d"))
    #                 self.action_create.setEnabled(False)
    #                 self.action_delete.setEnabled(False)
    #     else:
    #         self.stacked.setCurrentWidget(self.widget_empty)
    #
    # def on_add(self):
    #     item = self.tree.currentItem()
    #     if not item:
    #         return
    #
    #     dialog = AccountCreateDialog(self.add)
    #     code = item.data(0, QtCore.Qt.UserRole)
    #     dialog.lineedit_code.setText(str(code) + '.')
    #     dialog.exec_()
    #
    # def on_delete(self):
    #     item = self.tree.currentItem()
    #     if not item:
    #         return
    #
    #     if item.childCount():
    #         QtWidgets.QMessageBox.critical(None, "删除失败", "无法删除具有细分科目的分类科目")
    #         return
    #
    #     with FFDB.db_session:
    #         account = FFDB.db.Account.get(code=str(item.data(0, QtCore.Qt.UserRole)))
    #         if not account:
    #             QtWidgets.QMessageBox.critical(None, "删除失败", "科目不存在")
    #             return
    #
    #         if account.activated:
    #             QtWidgets.QMessageBox.critical(None, "删除失败", "无法删除已启用科目")
    #             return
    #
    #         account.delete()
    #         parent = item.parent()
    #         parent.removeChild(item)
    #         self.on_select(parent, None)
    #
    # def on_activate(self):
    #     item = self.tree.currentItem()
    #     if not item:
    #         return
    #
    #     with FFDB.db_session:
    #         account = FFDB.db.Account.get(code=str(item.data(0, QtCore.Qt.UserRole)))
    #         if account.activated:
    #             return
    #
    #         dialog = AccountActivateDialog(self.activate)
    #         dialog.exec_()
    #
    # def activate(self, currency: str):
    #     item = self.tree.currentItem()
    #
    #     if not item:
    #         return False
    #
    #     with FFDB.db_session:
    #         account = FFDB.db.Account.get(code=str(item.data(0, QtCore.Qt.UserRole)))
    #         account.activated = True
    #         account.currency = FFDB.db.Currency.get(name=currency)
    #
    #         FFDB.db.EndingBalance(account=account,
    #                               currency_amount=0.0,
    #                               local_currency_amount=0.0,
    #                               date=last_day_of_previous_month(FFDB.db.MetaData.select().first().date_until)
    #                               )
    #
    #     #
    #     self.on_select(item, item)
    #     return True

