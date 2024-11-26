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
from simpleaccounting.tools.dateutil import last_day_of_month
from simpleaccounting.widgets.qwidgets import CustomQDialog, HorizontalSpacer


class EndingBalanceDialog(CustomQDialog):

    def __init__(self):
        super().__init__()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["代码", "科目"])
        #
        self.de_end = QtWidgets.QDateEdit(last_day_of_month(System.meta().month_until))
        #
        container = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout(container)
        hbox.addWidget(QtWidgets.QLabel("截止日期"))
        hbox.addWidget(self.de_end)
        self.action_pull = QtWidgets.QAction(QtGui.QIcon(":/icons/persistenceEntity.svg"), "拉取", self)
        #
        self.tbar = QtWidgets.QToolBar()
        self.tbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.tbar.addWidget(HorizontalSpacer())
        self.tbar.addWidget(container)
        self.tbar.addSeparator()
        self.tbar.addAction(self.action_pull)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tbar)
        layout.addWidget(self.tree)

    def updateUI(self):
        items = {}
        for a in System.accounts():
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, a.code)
            item.setText(1, a.name)
            item.setData(0, QtCore.Qt.UserRole, a)
            items[a.code] = item

        for code, item in items.items():
            account = System.account(code)
            if account.parent:
                items[account.parent.code].addChild(item)
            else:
                self.tree.addTopLevelItem(item)
        #
