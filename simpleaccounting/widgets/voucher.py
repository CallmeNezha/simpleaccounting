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
from simpleaccounting.tools.dateutil import months_between, last_day_of_month, last_day_of_year
from simpleaccounting.app.system import System


class VoucherWidget(QtWidgets.QWidget):

    signal_voucher_edit_requested = QtCore.Signal(datetime.date)
    signal_mecf_requested = QtCore.Signal(datetime.date)
    signal_yecf_requested = QtCore.Signal(datetime.date)
    signal_exchange_gains_losses_requested = QtCore.Signal(datetime.date)

    def __init__(self):
        super().__init__(None)
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        font = self.font()
        font.setBold(True)
        self.setWindowTitle("凭证管理")
        self.list_month = QtWidgets.QListWidget()
        self.list_month.setMaximumWidth(self.fontMetrics().horizontalAdvance("2019.06") * 2)
        self.list_month.currentItemChanged.connect(self.on_listMonthCurrentChanged)
        self.label_voucher_count = QtWidgets.QLabel("0")
        self.label_voucher_count.setStyleSheet('color: blue;')
        self.label_voucher_count.setFont(font)
        self.label_exchange_gains_losses_voucher_state = QtWidgets.QLabel("无")
        self.label_exchange_gains_losses_voucher_state.setStyleSheet('color: red;')
        self.label_exchange_gains_losses_voucher_state.setFont(font)
        self.label_month_ending_voucher_state = QtWidgets.QLabel("无")
        self.label_month_ending_voucher_state.setStyleSheet('color: red;')
        self.label_month_ending_voucher_state.setFont(font)
        self.label_year_ending_voucher_state = QtWidgets.QLabel("无")
        self.label_year_ending_voucher_state.setStyleSheet('color: red;')
        self.label_year_ending_voucher_state.setFont(font)
        self.gbox = QtWidgets.QGroupBox("本月信息")
        grid = QtWidgets.QGridLayout(self.gbox)
        grid.addWidget(QtWidgets.QLabel("本月记账"), 0, 0)
        grid.addWidget(self.label_voucher_count, 0, 1)
        grid.addWidget(QtWidgets.QLabel("汇兑损益"), 1, 0)
        grid.addWidget(self.label_exchange_gains_losses_voucher_state, 1, 1)
        grid.addWidget(QtWidgets.QLabel("月末结转"), 2, 0)
        grid.addWidget(self.label_month_ending_voucher_state, 2, 1)
        grid.addWidget(QtWidgets.QLabel("年末结转"), 3, 0)
        grid.addWidget(self.label_year_ending_voucher_state, 3, 1)
        grid.setColumnStretch(1, 1000)
        grid.setRowStretch(4, 1000)

        self.btn_voucher_entry = QtWidgets.QPushButton("（1）凭证录入")
        self.btn_voucher_entry.clicked.connect(self.on_btn_entryClicked)
        self.btn_exchange_gains_losses = QtWidgets.QPushButton(" （2）汇兑损益")
        self.btn_exchange_gains_losses.clicked.connect(self.on_btn_exchangeGainsLossesClicked)
        self.btn_month_end_carry_forward_voucher = QtWidgets.QPushButton("（3）月末结转")
        self.btn_month_end_carry_forward_voucher.clicked.connect(self.on_btn_MECFVClicked)
        self.btn_last_year_end_carry_forward_voucher = QtWidgets.QPushButton("（4）年末结转")
        self.btn_last_year_end_carry_forward_voucher.clicked.connect(self.on_btn_YECFVClicked)
        self.btn_forward_month = QtWidgets.QPushButton("进入下月")
        self.btn_forward_month.clicked.connect(self.on_btn_forwardMonthClicked)
        self.btn_view = QtWidgets.QPushButton("【Excel】凭证查看")
        # self.btn_view.clicked.connect(self.on_buttonViewClicked)
        grid.addWidget(self.btn_voucher_entry, 5, 0, 1, 2)
        grid.addWidget(self.btn_exchange_gains_losses, 6, 0, 1, 2)
        grid.addWidget(self.btn_month_end_carry_forward_voucher, 7, 0, 1, 2)
        grid.addWidget(self.btn_last_year_end_carry_forward_voucher, 8, 0, 1, 2)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.btn_forward_month)
        vbox.addStretch(10)
        vbox.addWidget(self.btn_view)
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.list_month)
        hbox.addWidget(self.gbox)
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

    def on_btn_entryClicked(self):
        if item := self.list_month.currentItem():
            date = item.data(QtCore.Qt.ItemDataRole.UserRole)
            self.signal_voucher_edit_requested.emit(date)

    def on_btn_MECFVClicked(self):
        if item := self.list_month.currentItem():
            date = item.data(QtCore.Qt.ItemDataRole.UserRole)
            self.signal_mecf_requested.emit(date)

    def on_btn_YECFVClicked(self):
        if item := self.list_month.currentItem():
            date = item.data(QtCore.Qt.ItemDataRole.UserRole)
            self.signal_yecf_requested.emit(date)

    def on_btn_exchangeGainsLossesClicked(self):
        if item := self.list_month.currentItem():
            date = item.data(QtCore.Qt.ItemDataRole.UserRole)
            self.signal_exchange_gains_losses_requested.emit(date)


    def on_btn_forwardMonthClicked(self):
        if QtWidgets.QMessageBox.Yes == QtWidgets.QMessageBox.question(None, "确认", "是否进入下一个账期"):
            System.forwardToNextMonth()
            self.updateUI()

    def on_listMonthCurrentChanged(self):
        if item := self.list_month.currentItem():
            date: datetime.date = item.data(QtCore.Qt.ItemDataRole.UserRole)
            date_from = datetime.date(year=date.year, month=date.month, day=1)
            date_until = last_day_of_month(date_from)
            self.gbox.setTitle(date.strftime('%Y年%m月'))

            vouchers = System.vouchers(lambda v: v.date >= date_from and v.date <= date_until and v.category == '记账')
            self.label_voucher_count.setText(str(len(vouchers)))

            vouchers = System.vouchers(lambda v: v.date >= date_from and v.date <= date_until and v.category == '汇兑损益结转')
            self.label_exchange_gains_losses_voucher_state.setText(str(len(vouchers)))
            self.label_exchange_gains_losses_voucher_state.setStyleSheet('color: green;' if len(vouchers) > 0 else 'color: red;')

            vouchers = System.vouchers(lambda v: v.date >= date_from and v.date <= date_until and v.category == '月末结转')
            self.label_month_ending_voucher_state.setText(str(len(vouchers)))
            self.label_month_ending_voucher_state.setStyleSheet('color: green;' if len(vouchers) > 0 else 'color: red;')

            vouchers = System.vouchers(lambda v: v.date >= date_from and v.date <= date_until and v.category == '年末结转')
            self.label_year_ending_voucher_state.setText(str(len(vouchers)))
            self.label_year_ending_voucher_state.setStyleSheet('color: green;' if len(vouchers) > 0 else 'color: red;')

            # 年初1月启用年末结转
            self.btn_last_year_end_carry_forward_voucher.setEnabled(date.month == 12)

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
