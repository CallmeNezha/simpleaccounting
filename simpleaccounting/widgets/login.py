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
        super().__init__(None)
        self.setupUI()
        self.path = path

    def setupUI(self):
        self.le_name = QtWidgets.QLineEdit()
        self.le_name.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^[A-Za-z0-9\u4e00-\u9fa5]+$")))
        self.de_month = QtWidgets.QDateEdit()
        self.de_month.setDisplayFormat('yyyy.MM')
        now = datetime.datetime.now()
        self.de_month.setDate(QtCore.QDate(now.year, now.month, 1))
        form = QtWidgets.QFormLayout()
        form.addRow("账套名称", self.le_name)
        form.addRow("起始月份", self.de_month)
        # 将按钮框添加到布局中
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.button_box)

    def accept(self):
        name = self.le_name.text()
        if name.strip() == "":
            QtWidgets.QMessageBox.critical(None, "创建失败", "错误代码A4.1/4：名称不能为空")
            return
        elif (self.path / f"{name}.db").is_file():
            QtWidgets.QMessageBox.critical(None, "创建失败", "错误代码A4.1/5：账套文件已存在")
            return
        #
        month = month_of_date(datetime.date(self.de_month.date().year(), self.de_month.date().month(), 1))
        System.new(self.path / f"{name}.db", month)
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
        self.cb = CustomQComboBox()
        self.cb.currentTextChanged.connect(self.on_currentTextChanged)
        self.btn_login = QtWidgets.QPushButton('登录')
        self.btn_login.setEnabled(False)
        self.btn_login.clicked.connect(self.on_buttonLoginClicked)
        self.btn_register = QtWidgets.QPushButton('注册')
        self.btn_register.clicked.connect(self.on_buttonRegisterClicked)
        layout = QtWidgets.QFormLayout()
        gbox = QtWidgets.QGroupBox('账套信息')
        gbox.setLayout(layout)
        layout.addRow('公司名称', self.lbl_company)
        layout.addRow('起始月份', self.lbl_month_from)
        layout.addRow('当前月份', self.lbl_month_until)
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.cb, 0, 0)
        layout.addWidget(gbox, 1, 0, 3, 1)
        layout.addWidget(self.btn_login, 0, 1)
        layout.addWidget(self.btn_register, 1, 1)
        layout.setColumnStretch(0, 10)

    def updateUI(self):
        self.cb.blockSignals(True)
        self.cb.clear()
        for f in glob.glob("*.db", root_dir=SIMPLEACCOUNTING_DIR):
            self.cb.addItem(f)
        self.cb.blockSignals(False)
        self.on_currentTextChanged()

    def on_currentTextChanged(self):
        if self.cb.currentText():
            System.bindDatabase(pathlib.Path(SIMPLEACCOUNTING_DIR) / self.cb.currentText())
            try:
                meta = System.meta()
                self.lbl_company.setText(meta.company)
                self.lbl_month_from.setText(meta.month_from.strftime("%Y.%m"))
                self.lbl_month_until.setText(meta.month_until.strftime("%Y.%m"))
                self.btn_login.setEnabled(True)
            except Exception:
                self.btn_login.setEnabled(False)

    def on_buttonRegisterClicked(self):
        dialog = RegisterDialog(pathlib.Path(SIMPLEACCOUNTING_DIR))
        dialog.exec_()
        self.updateUI()

    def on_buttonLoginClicked(self):
        self.sigLoginRequest.emit(pathlib.Path(SIMPLEACCOUNTING_DIR) / f"{self.cb.currentText()}.db")
