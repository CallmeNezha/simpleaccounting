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

from qtpy import QtWidgets, QtGui, QtCore
from simpleaccounting.widgets.qwidgets import CustomQDialog
from simpleaccounting.tools.dateutil import months_between, last_day_of_month
from simpleaccounting.app.system import System
from simpleaccounting.widgets.voucheredit import VoucherEditDialog



class VoucherDialog(CustomQDialog):

    def __init__(self):
        super().__init__(None)
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        self.setWindowTitle("凭证管理")
        #
        self.list_month = QtWidgets.QListWidget()
        self.list_month.setMaximumWidth(self.fontMetrics().horizontalAdvance("2019.06") * 2)
        self.list_month.currentItemChanged.connect(self.on_listMonthCurrentChanged)
        font = self.font()
        font.setBold(True)
        self.label_voucher_count = QtWidgets.QLabel("0")
        self.label_voucher_count.setStyleSheet('color: blue;')
        self.label_voucher_count.setFont(font)
        self.label_month_ending_voucher_state = QtWidgets.QLabel("无")
        self.label_month_ending_voucher_state.setStyleSheet('color: red;')
        self.label_month_ending_voucher_state.setFont(font)
        self.label_month_ending_balance = QtWidgets.QLabel("不平衡")
        self.label_month_ending_balance.setStyleSheet('color: red;')
        self.label_month_ending_balance.setFont(font)

        gbox = QtWidgets.QGroupBox("本月信息")
        form = QtWidgets.QFormLayout(gbox)
        form.addRow("凭证数", self.label_voucher_count)
        form.addRow("结转凭证", self.label_month_ending_voucher_state)
        form.addRow("结转试算", self.label_month_ending_balance)

        self.button_entry = QtWidgets.QPushButton("（一）凭证录入")
        self.button_entry.clicked.connect(self.on_buttonEntryClicked)

        self.button_closing_voucher = QtWidgets.QPushButton("（二）结转凭证")
        # self.button_closing_voucher.clicked.connect(self.on_buttonClosingBalanceClicked)

        self.button_closing_balance = QtWidgets.QPushButton("（三）进入下月")
        # self.button_closing_balance.clicked.connect(self.on_buttonClosingClicked)

        self.button_view = QtWidgets.QPushButton("【Excel】凭证查看")
        # self.button_view.clicked.connect(self.on_buttonViewClicked)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.button_entry)
        vbox.addWidget(self.button_closing_voucher)
        vbox.addWidget(self.button_closing_balance)
        vbox.addStretch(10)
        vbox.addWidget(self.button_view)

        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.list_month)
        hbox.addWidget(gbox)
        hbox.addLayout(vbox)

    def updateUI(self):
        self.list_month.blockSignals(True)
        self.list_month.clear()
        meta = System.meta()
        for i in range(months_between(meta.month_from, meta.month_until) + 1):
            year = meta.month_from.year + (meta.month_from.month + i - 1) // 12
            month = (meta.month_from.month + i - 1) % 12 + 1
            date = datetime.date(year, month, 1)
            item = QtWidgets.QListWidgetItem(date.strftime("%Y.%m"))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, date)
            item.setForeground(QtGui.QColor('#AAAAAA'))
            self.list_month.insertItem(0, item)
            # !for
        self.list_month.blockSignals(False)
        self.list_month.setCurrentRow(0)
        self.list_month.currentItem().setForeground(QtGui.QColor('#0000FF'))
        self.on_listMonthCurrentChanged()

    def on_buttonEntryClicked(self):
        item = self.list_month.currentItem()
        if not item:
            return

        date = item.data(QtCore.Qt.UserRole)
        dialog = VoucherEditDialog(date)
        dialog.resize(1200, 600)
        dialog.exec_()
        self.on_listMonthCurrentChanged()

    # def on_buttonViewClicked(self):
    #
    #     def balances(account, date):
    #         if not has_sub_accounts(AccountCode(account.code)):
    #             balance = account.ending_balances.select(date=date).first()
    #             return (balance.currency_amount, balance.local_currency_amount) if balance else (0.0, 0.0)
    #         else:
    #             accounts = sub_accounts(AccountCode(account.code))
    #             currency_amount = 0.0
    #             local_currency_amount = 0.0
    #             for acc in accounts:
    #                 a, b = balances(FFDB.db.Account.get(code=str(acc)), date)
    #                 currency_amount += a
    #                 local_currency_amount += b
    #             return currency_amount, local_currency_amount
    #
    #     item = self.list_month.currentItem()
    #     if not item:
    #         return
    #
    #     QtWidgets.QMessageBox.information(None, "提示", "即将打开Excel软件进行数据导出，请勿关闭Excel直到计算完成。")
    #
    #     from simplefinance.tools.excel import make_workbook
    #
    #     wb = make_workbook()
    #
    #     date = item.data(QtCore.Qt.ItemDataRole.UserRole)
    #     with FFDB.db_session:
    #         date_from = datetime.date(date.year, date.month, 1)
    #         date_until = last_day_of_month(date_from.year, date_from.month)
    #
    #         # -----------------------------
    #         catalog = wb.sheets['目录']
    #         catalog['D4'].value = str(FFDB.db.MetaData.select().first().book_name)
    #         catalog['D5'].value = date.strftime("%Y年%m月")
    #         catalog['D6'].value = last_day_of_month(date.year, date.month).strftime("%Y年%m月%d日")
    #
    #         # -----------------------------
    #         sheet_entries = wb.sheets['凭证录入']
    #         def general_account(account):
    #             pp = account.parent
    #             while pp.parent is not None:
    #                 pp = pp.parent
    #             return pp
    #
    #         vouchers = FFDB.db.Voucher.select(lambda v: v.date >= date_from and v.date <= date_until)
    #         table_vouchers = []
    #         for v in vouchers:
    #             for entry in v.debit_entries:
    #                 table_vouchers.append(
    #                     ['记',
    #                      v.number.split('/')[-1],
    #                      v.date.strftime("%m"),
    #                      v.date.strftime("%d"),
    #                      entry.brief,
    #                      entry.account.name if entry.account.parent is None else general_account(entry.account).name,
    #                      entry.account.name if entry.account.parent is not None else '',
    #                      str(FloatWithPrecision(entry.amount * entry.exchange_rate)),
    #                      ''
    #                     ]
    #                 )
    #
    #             for entry in v.credit_entries:
    #                 table_vouchers.append(
    #                     ['记',
    #                      v.number.split('/')[-1],
    #                      v.date.strftime("%m"),
    #                      v.date.strftime("%d"),
    #                      entry.brief,
    #                      entry.account.name if entry.account.parent is None else general_account(entry.account).name,
    #                      entry.account.name if entry.account.parent is not None else '',
    #                      '',
    #                      str(FloatWithPrecision(entry.amount * entry.exchange_rate))
    #                      ]
    #                 )
    #
    #         sheet_entries.range('A6').value = table_vouchers
    #
    #         # --------------
    #         sheet_remains = wb.sheets['科目余额表']
    #         row = 6
    #         debit_remains, credit_remains = account_ending_balance_local(date_from, date_until)
    #         table_remains = []
    #         bold_rows = []
    #         fold_ranges = defaultdict(list)
    #         for account in FFDB.db.Account.select().sort_by(FFDB.db.Account.code):
    #             balance = account.ending_balances.select(date=last_day_of_previous_month(date)).first()
    #             if balance:
    #                 endingBalance = FloatWithPrecision(balance.local_currency_amount).value
    #             else:
    #                 _, endingBalance = balances(account, last_day_of_previous_month(date))
    #
    #             table_remains.append(
    #                 [account.code,
    #                  account.name,
    #                  endingBalance,
    #                  FloatWithPrecision(debit_remains[AccountCode(account.code)]).value,
    #                  FloatWithPrecision(credit_remains[AccountCode(account.code)]).value,
    #                  account.direction
    #                  ]
    #             )
    #             code = AccountCode(account.code)
    #             if code.parent() is None:
    #                 row_s = row + len(table_remains) - 1
    #                 bold_rows.append(row_s)
    #                 fold_ranges[AccountCode(account.code)].append(row_s)
    #             else:
    #                 row_s = row + len(table_remains) - 1
    #                 while code.parent() is not None:
    #                     code = code.parent()
    #                 fold_ranges[code].append(row_s)
    #
    #         sheet_remains.range(f'A{row}').value = table_remains
    #
    #         sheet_remains[f'D{row+len(table_remains)}'].value = FloatWithPrecision(sum([r[3] for r in table_remains if '.' not in r[0]])).value
    #         sheet_remains[f'E{row+len(table_remains)}'].value = FloatWithPrecision(sum([r[4] for r in table_remains if '.' not in r[0]])).value
    #
    #         sheet_remains['K4'].value = sheet_remains[f'D{row+len(table_remains)}'].value
    #         sheet_remains['L4'].value = sheet_remains[f'E{row+len(table_remains)}'].value
    #
    #         for r in bold_rows:
    #             sheet_remains.range(f'{r}:{r}').font.bold = True
    #         #
    #         for k, r in fold_ranges.items():
    #             if len(r) > 1:
    #                 sheet_remains[f'{min(r)+1}:{max(r)}'].api.Rows.Group()
    #                 sheet_remains[f'{min(r) + 1}:{max(r)}'].api.Rows.Hidden = True
    #
    #     QtWidgets.QMessageBox.information(None, "提示", "Excel数据导出完成。")

    def on_listMonthCurrentChanged(self):
        #
        item = self.list_month.currentItem()
        if not item:
            return
        date: datetime.date = item.data(QtCore.Qt.ItemDataRole.UserRole)
        date_from = datetime.date(year=date.year, month=date.month, day=1)
        date_until = last_day_of_month(date_from)

        vouchers = System.vouchers(lambda v: v.date >= date_from and v.date <= date_until and v.category == '记账')
        self.label_voucher_count.setText(str(len(vouchers)))

        vouchers = System.vouchers(lambda v: v.date >= date_from and v.date <= date_until and v.category == '月末结转')
        self.label_month_ending_voucher_state.setText(str(len(vouchers)))
        self.label_month_ending_voucher_state.setStyleSheet('color: green;' if len(vouchers) > 0 else 'color: red;')
        # !with

        # ...
        # self.label_month_ending_balance.setText("平衡" if balanced else "不平衡")
        # self.label_month_ending_balance.setStyleSheet('color: green;' if balanced else 'color: red;')

        # with FFDB.db_session:
        #     date_until = FFDB.db.MetaData.select().first().date_until
        #     accounting = date_until.year == date.year and date_until.month == date.month
        #     self.button_entry.setEnabled(accounting)
        #     self.button_closing_voucher.setEnabled(accounting)
        #     self.button_closing_balance.setEnabled(accounting)

    # def on_buttonClosingBalanceClicked(self):
    #     item = self.list_month.currentItem()
    #     if not item:
    #         return
    #
    #     date = item.data(QtCore.Qt.ItemDataRole.UserRole)
    #     dialog = VoucherMonthClosingEntryDialog(date)
    #     dialog.resize(1200, 600)
    #     dialog.exec_()
    #     self.on_listMonthCurrentChanged()
    #
    # def on_buttonClosingClicked(self):
    #     if self.label_month_ending_balance.text() == '平衡':
    #         ret = QtWidgets.QMessageBox.question(None, "确认", "确认进入下一个会计周期？本月凭证将全部锁定。")
    #         if ret == QtWidgets.QMessageBox.StandardButton.Yes:
    #             item = self.list_month.currentItem()
    #             if not item:
    #                 return
    #             date: datetime.date = item.data(QtCore.Qt.ItemDataRole.UserRole)
    #             month_end_closing(date.year, date.month)
    #             self.updateUI()
    #     else:
    #         QtWidgets.QMessageBox.critical(None, "错误", "结转试算不平衡，无法进入下一个会计周期。")