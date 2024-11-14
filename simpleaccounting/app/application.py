
import pathlib
from qtpy import QtWidgets, QtGui, QtCore
from simpleaccounting.widgets.login import LoginDialog
from simpleaccounting.widgets.bulletinboard import BulletinBoardDialog
from simpleaccounting import resource # noqa


class Application(QtWidgets.QApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(QtWidgets.QStyleFactory.create('Windows'))
        self.setQuitOnLastWindowClosed(True)
        self.setApplicationName("简单记账")
        self.setWindowIcon(QtGui.QIcon(':/icons/notebook.svg'))
        self.dialog_login = LoginDialog()
        self.dialog_login.sigLoginRequest.connect(self.login)
        self.dialog_login.exec_()

    def login(self, filename: pathlib.Path):
        self.dialog_login.hide()
        BulletinBoardDialog().exec_()
        self.dialog_login.show()