

from qtpy import QtWidgets, QtGui
from simplefinance.app.application import Application

if __name__ == "__main__":
    # Initialize the application
    app = Application([])
    app.createBook()
    app.exec_()