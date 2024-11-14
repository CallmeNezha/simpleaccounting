import glob
import pathlib
import datetime
from qtpy import QtWidgets, QtCore, QtGui
from simpleaccounting.widgets.qwidgets import CustomInputDialog, CustomQDialog, CustomQComboBox
from simpleaccounting.app.system import System
from simpleaccounting.app.iniconfig import INIConfig, SIMPLEACCOUNTING_DIR


class RegisterDialog(CustomInputDialog):
    def __init__(self, path: pathlib.Path):
        super().__init__(None)
        self.setupUI()
        self.path = path

    def setupUI(self):
        self.lineedit = QtWidgets.QLineEdit()
        self.lineedit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^[A-Za-z0-9\u4e00-\u9fa5]+$")))
        #
        self.dateedit = QtWidgets.QDateEdit()
        self.dateedit.setDisplayFormat('yyyy.MM')
        #
        now = datetime.datetime.now()
        self.dateedit.setDate(QtCore.QDate(now.year, now.month, 1))
        #
        form = QtWidgets.QFormLayout()
        form.addRow("账套名称", self.lineedit)
        form.addRow("起始日期", self.dateedit)
        # 将按钮框添加到布局中
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.button_box)

    def accept(self):
        name = self.lineedit.text()
        if name.strip() == "":
            QtWidgets.QMessageBox.critical(None, "创建失败", "错误代码A4.1/4：名称不能为空")
            return
        elif (self.path / f"{name}.db").is_file():
            QtWidgets.QMessageBox.critical(None, "创建失败", "错误代码A4.1/5：账套文件已存在")
            return
        #
        date = datetime.date(self.dateedit.date().year(), self.dateedit.date().month(), 1)
        System.new(self.path / f"{name}.db", date)
        super().accept()


class LoginDialog(CustomQDialog):

    sigLoginRequest = QtCore.Signal(pathlib.Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.updateUI()

    def setupUI(self):

        self.label_company = QtWidgets.QLabel()
        self.label_date_from = QtWidgets.QLabel()
        self.label_date_until = QtWidgets.QLabel()

        self.combobox = CustomQComboBox()
        self.combobox.currentTextChanged.connect(self.on_currentTextChanged)

        self.button_login = QtWidgets.QPushButton('登录')
        self.button_login.setEnabled(False)
        self.button_login.clicked.connect(self.on_buttonLoginClicked)

        self.button_register = QtWidgets.QPushButton('注册')
        self.button_register.clicked.connect(self.on_buttonRegisterClicked)

        layout = QtWidgets.QFormLayout()
        gbox = QtWidgets.QGroupBox('账套信息')
        gbox.setLayout(layout)
        layout.addRow('公司名称', self.label_company)
        layout.addRow('起始日期', self.label_date_from)
        layout.addRow('当前日期', self.label_date_until)

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.combobox, 0, 0)
        layout.addWidget(gbox, 1, 0, 3, 1)
        layout.addWidget(self.button_login, 0, 1)
        layout.addWidget(self.button_register, 1, 1)
        layout.setColumnStretch(0, 10)

        self.resize(600, -1)

    def updateUI(self):
        self.combobox.blockSignals(True)
        self.combobox.clear()
        for f in glob.glob("*.db", root_dir=SIMPLEACCOUNTING_DIR):
            self.combobox.addItem(f)
        self.combobox.blockSignals(False)
        self.on_currentTextChanged()

    def on_currentTextChanged(self):
        if self.combobox.currentText():
            System.bindDatabase(pathlib.Path(SIMPLEACCOUNTING_DIR) / self.combobox.currentText())
            try:
                meta = System.meta()
                self.label_company.setText(meta.company)
                self.label_date_from.setText(meta.date_from.strftime("%Y.%m"))
                self.label_date_until.setText(meta.date_until.strftime("%Y.%m"))
                self.button_login.setEnabled(True)
            except Exception:
                self.button_login.setEnabled(False)

    def on_buttonRegisterClicked(self):
        dialog = RegisterDialog(pathlib.Path(SIMPLEACCOUNTING_DIR))
        dialog.exec_()

    def on_buttonLoginClicked(self):
        self.sigLoginRequest.emit(pathlib.Path(SIMPLEACCOUNTING_DIR) / f"{self.combobox.currentText()}.db")
