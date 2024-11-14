
import os
from qtpy import QtWidgets, QtGui
from simpleaccounting.app.application import Application

if __name__ == "__main__":
    # Initialize the application
    os.environ['QT_SCALE_FACTOR'] = ''
    app = Application([])
    app.exec_()