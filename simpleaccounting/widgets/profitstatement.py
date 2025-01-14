
from qtpy import QtWidgets


class ProfitStatement(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setupUI()
        self.updateUI()

    def setupUI(self):
        self.de_from = QtWidgets.QDateEdit()
        self.de_to = QtWidgets.QDateEdit()

        self.tbar = QtWidgets.QToolBar()
        self.action_template_edit = ...

    def updateUI(self):
        ...
