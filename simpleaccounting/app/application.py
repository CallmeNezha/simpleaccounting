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

import pathlib
from qtpy import QtWidgets, QtGui, QtCore
from simpleaccounting.widgets.login import LoginDialog
from simpleaccounting.widgets.mainwindow import MainWindow
from simpleaccounting import resource # noqa


class Application(QtWidgets.QApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setQuitOnLastWindowClosed(True)
        self.setApplicationName("简单记账")
        self.setupUI()

    def setupUI(self):
        # self.setStyle(QtWidgets.QStyleFactory.create('Windows'))
        self.setWindowIcon(QtGui.QIcon(':/icons/notebook.svg'))
        self.dialog_login = LoginDialog()
        self.dialog_login.sigLoginRequest.connect(self.login)
        self.dialog_login.exec_()

    def login(self):
        self.dialog_login.hide()
        # BulletinBoardDialog().exec_()
        self.main_window = MainWindow()
        self.main_window.show()
        # self.dialog_login.show()