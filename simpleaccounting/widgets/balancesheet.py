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
        entries = self.template()
        for i, (left, right) in enumerate(zip(entries['资产'], entries['负债和所有者权益（或股东权益）'])):
            for j in range(COLUMN_COUNT):
                item = QtWidgets.QTableWidgetItem("")
                item.setTextAlignment(QtCore.Qt.AlignRight)
                self.table.setItem(i, j, item)
                if j == COLUMN_ASSET:
                    item.setText(left)
                    item.setTextAlignment(QtCore.Qt.AlignLeft)
                elif j == COLUMN_DEBT:
                    item.setText(right)
                    item.setTextAlignment(QtCore.Qt.AlignLeft)
            # 1for
        # 1for
        self.table.resizeRowsToContents()

    def template(self) -> dict[str, list]:
        entries = {
            "资产": [
                "流动资产:",
                "货币资金",
                "交易性金融资产",
                "衍生金融资产",
                "应收票据",
                "应收账款",
                "应收款项融资",
                "预付款项",
                "其他应收款",
                "存货",
                "合同资产",
                "持有待售资产",
                "一年内到期的非流动资产",
                "其他流动资产",
                "流动资产合计",
                "非流动资产:",
                "债权投资",
                "其他债权投资",
                "长期应收款",
                "长期股权投资",
                "其他权益工具投资",
                "其他非流动金融资产",
                "投资性房地产",
                "固定资产",
                "在建工程",
                "生产性生物资产",
                "油气资产",
                "使用权资产",
                "无形资产",
                "开发支出",
                "商誉",
                "长期待摊费用",
                "递延所得税资产",
                "其他非流动资产",
                "非流动资产合计",
                "",
                "",
                "",
                "",
                "资产总计"
            ],
            "负债和所有者权益（或股东权益）": [
                "流动负债:",
                "短期借款",
                "交易性金融负债",
                "衍生金融负债",
                "应付票据",
                "应付账款",
                "预收款项",
                "合同负债",
                "应付职工薪酬",
                "应交税费",
                "其他应付款",
                "持有待售负债",
                "一年内到期的非流动负债",
                "其他流动负债",
                "流动负债合计",
                "非流动负债:",
                "长期借款",
                "应付债券",
                "其中：优先股",
                "永续债",
                "租赁负债",
                "长期应付款",
                "预计负债",
                "递延收益",
                "递延所得税负债",
                "其他非流动负债",
                "非流动负债合计",
                "负债合计",
                "所有者权益（或股东权益）:",
                "实收资本（或股本）",
                "其他权益工具"
                "其中：优先股",
                "永续债",
                "资本公积",
                "减：库存股",
                "其他综合收益",
                "专项储备",
                "盈余公积",
                "未分配利润",
                "所有者权益（或股东权益）合计",
                "负债和所有者权益（或股东权益）总计"
            ]
        }
        #
        return entries

    def on_action_editTemplateTriggered(self):
        ...

    def on_action_pullTriggered(self):
        """"""
        date = qdate_to_date(self.de_until.date())
        self.setWindowTitle(f"{date.strftime('%Y年度')}资产负债表")
        entries = self.template()
        for i, (left, right) in enumerate(zip(entries['资产'], entries['负债和所有者权益（或股东权益）'])):
            beginning, ending = self.balance(left, date)
            if beginning is not None and ending is not None:
                self.table.item(i, COLUMN_ASSET_LAST_YEAR_ENDING_BALANCE).setText(str(beginning))
                self.table.item(i, COLUMN_ASSET_ENDING_BALANCE).setText(str(ending))
            beginning, ending = self.balance(left, date)
            if beginning is not None and ending is not None:
                self.table.item(i, COLUMN_ASSET_LAST_YEAR_ENDING_BALANCE).setText(str(beginning))
                self.table.item(i, COLUMN_ASSET_ENDING_BALANCE).setText(str(ending))


    def balance(self, term: str, date_until: datetime.date):
        """"""
        last_year = last_day_of_previous_year(date_until)
        if term == '货币资金':
            beginning_balance = FloatWithPrecision(0.0)
            ending_balance = FloatWithPrecision(0.0)
            for name in ['库存现金', '银行存款', '备用金', '其他货币资金']:
                _, local_amount = System.endingBalanceByName(name, last_year)
                beginning_balance += local_amount
                _, local_amount = System.endingBalanceByName(name, date_until)
                ending_balance += local_amount
            return beginning_balance, ending_balance
        elif term == '交易性金融资产':
            return None, None
        else:
            return None, None

