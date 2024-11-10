
import pathlib
from qtpy import QtWidgets, QtGui
import datetime

from simplefinance.app.system import System


class Application(QtWidgets.QApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(QtWidgets.QStyleFactory.create('Windows'))
        self.setQuitOnLastWindowClosed(True)
        self.setApplicationName("简单记账")
        self.setWindowIcon(QtGui.QIcon(':/icons/notebook.svg'))

    def createBook(self):
        System.new(pathlib.Path('C:/Users/78362/devel/xlwings/simplefinance/科技.sqlite'), datetime.date(2024, 5, 1))

