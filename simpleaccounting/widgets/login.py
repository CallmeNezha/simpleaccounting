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

import glob
import pathlib
import datetime
from qtpy import QtWidgets, QtCore, QtGui

from simpleaccounting.tools.dateutil import month_of_date
from simpleaccounting.widgets.qwidgets import CustomInputDialog, CustomQDialog, CustomQComboBox
from simpleaccounting.app.system import System
from simpleaccounting.app.iniconfig import INIConfig, SIMPLEACCOUNTING_DIR


class RegisterDialog(CustomInputDialog):
    def __init__(self, path: pathlib.Path):
        super().__init__()
        self.setupUI()
        self.path = path

    def setupUI(self):
        self.le_name = QtWidgets.QLineEdit()
        self.le_name.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^[A-Za-z0-9\u4e00-\u9fa5]+$")))
        self.cb_standard = QtWidgets.QComboBox()
        self.cb_standard.addItems(['一般企业会计准则（2018）', '小企业会计准则（2013）'])

        self.de_month = QtWidgets.QDateEdit()
        self.de_month.setDisplayFormat('yyyy.MM')
        self.de_month.setDate(month_of_date(datetime.datetime.now()))
        form = QtWidgets.QFormLayout()
        form.addRow("账套名称", self.le_name)
        form.addRow('会计准则', self.cb_standard)
        form.addRow("起始月份", self.de_month)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(form)
        vbox.addWidget(self.button_box)

    def accept(self):
        name = self.le_name.text().strip()
        #
        if not name:
            QtWidgets.QMessageBox.critical(None, "创建失败", "错误代码A4.1/4：名称不能为空")
            return
        elif (self.path / f"{name}.db").is_file():
            QtWidgets.QMessageBox.critical(None, "创建失败", "错误代码A4.1/5：账套文件已存在")
            return
        #
        month = month_of_date(datetime.date(self.de_month.date().year(), self.de_month.date().month(), 1))
        System.new(self.path / f"{name}.db", self.cb_standard.currentText(), month)
        super().accept()


class LoginDialog(CustomQDialog):

    sigLoginRequest = QtCore.Signal(pathlib.Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        self.lbl_company = QtWidgets.QLabel()
        self.lbl_month_from = QtWidgets.QLabel()
        self.lbl_month_until = QtWidgets.QLabel()
        self.cb_books = CustomQComboBox()
        self.cb_books.currentTextChanged.connect(self.on_cb_booksCurrentTextChanged)
        self.btn_login = QtWidgets.QPushButton('登录')
        self.btn_login.setEnabled(False)
        self.btn_login.clicked.connect(self.on_btn_loginClicked)
        self.btn_register = QtWidgets.QPushButton('注册')
        self.btn_register.clicked.connect(self.on_btn_registerClicked)
        form = QtWidgets.QFormLayout()
        gbox = QtWidgets.QGroupBox('账套信息')
        gbox.setLayout(form)
        form.addRow('公司名称', self.lbl_company)
        form.addRow('起始月份', self.lbl_month_from)
        form.addRow('当前月份', self.lbl_month_until)
        form = QtWidgets.QGridLayout(self)
        form.addWidget(self.cb_books, 0, 0)
        form.addWidget(gbox, 1, 0, 3, 1)
        form.addWidget(self.btn_login, 0, 1)
        form.addWidget(self.btn_register, 1, 1)
        form.setColumnStretch(0, 10)

    def updateUI(self):
        self.cb_books.blockSignals(True)
        self.cb_books.clear()
        for f in glob.glob("*.db", root_dir=SIMPLEACCOUNTING_DIR):
            self.cb_books.addItem(f)
        self.cb_books.blockSignals(False)
        self.on_cb_booksCurrentTextChanged()

    def on_cb_booksCurrentTextChanged(self):
        if self.cb_books.currentText():
            System.bindDatabase(pathlib.Path(SIMPLEACCOUNTING_DIR) / self.cb_books.currentText())
            try:
                meta = System.meta()
                self.lbl_company.setText(meta.company)
                self.lbl_month_from.setText(meta.month_from.strftime("%Y.%m"))
                self.lbl_month_until.setText(meta.month_until.strftime("%Y.%m"))
                self.btn_login.setEnabled(True)
            except Exception as e:
                self.btn_login.setEnabled(False)

    def on_btn_registerClicked(self):
        dialog = RegisterDialog(pathlib.Path(SIMPLEACCOUNTING_DIR))
        dialog.exec_()
        self.updateUI()

    def on_btn_loginClicked(self):
        self.sigLoginRequest.emit(pathlib.Path(SIMPLEACCOUNTING_DIR) / f"{self.cb_books.currentText()}.db")
