from qtpy import QtWidgets, QtCore, QtGui


class FreezableTableView(QtWidgets.QTableView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        self.setupUI()

    def setupUI(self):
        self.setHorizontalScrollMode(QtWidgets.QTableView.ScrollPerPixel)
        self.setVerticalScrollMode(QtWidgets.QTableView.ScrollPerPixel)
        # --- ftv left
        self.__freeze_to_column = 0
        self.__ftv_left = QtWidgets.QTableView(self)
        self.__ftv_left.hide()
        self.__ftv_left.setModel(self.model())
        self.__ftv_left.setSelectionModel(self.selectionModel())
        self.__ftv_left.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__ftv_left.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.__ftv_left.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.__ftv_left.verticalHeader().hide()
        self.__ftv_left.setStyleSheet('''
            QTableView { border: 0px, 0px, 1px, 0px;
                         background-color: #c4d2e0;
                         selection-background-color: #999;
            }''') # for demo purposes
        self.__ftv_left.setVerticalScrollMode(QtWidgets.QTableView.ScrollPerPixel)
        self.__ftv_left.horizontalHeader().sectionResized.connect(self.updateTableColumnSectionWidth)
        self.verticalScrollBar().valueChanged.connect(self.__ftv_left.verticalScrollBar().setValue)
        self.__ftv_left.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)
        self.viewport().stackUnder(self.__ftv_left)
        # --- ftv top
        self.__freeze_to_row = 0
        self.__ftv_top = QtWidgets.QTableView(self)
        self.__ftv_top.hide()
        self.__ftv_top.setModel(self.model())
        self.__ftv_top.setSelectionModel(self.selectionModel())
        self.__ftv_top.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__ftv_top.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.__ftv_top.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.__ftv_top.setStyleSheet('''
            QTableView { border: 0px, 1px, 0px, 0px;
                         background-color: #c4d2e0;
                         selection-background-color: #999;
            }''') # for demo purposes
        self.__ftv_top.setHorizontalScrollMode(self.ScrollPerPixel)
        self.__ftv_top.horizontalHeader().sectionResized.connect(self.updateTableColumnSectionWidth)
        self.__ftv_top.verticalHeader().sectionResized.connect(self.updateTableRowSectionHeight)
        self.horizontalScrollBar().valueChanged.connect(self.__ftv_top.horizontalScrollBar().setValue)
        self.__ftv_top.horizontalScrollBar().valueChanged.connect(self.horizontalScrollBar().setValue)
        self.viewport().stackUnder(self.__ftv_top)
        # ---
        self.horizontalHeader().sectionResized.connect(self.updateFrozenTableSectionWidth)
        self.verticalHeader().sectionResized.connect(self.updateFrozenTableSectionHeight)

    def freezeToColumn(self, column: int):
        self.__ftv_top.hide()
        self.__freeze_to_column = max(0, column)
        if self.__freeze_to_column > 0:
            self.__ftv_left.show()
        else:
            self.__ftv_left.hide()
        # 1if
        for col in range(self.model().columnCount()):
            if col < self.__freeze_to_column:
                self.__ftv_left.setColumnHidden(col, False)
                self.__ftv_left.setColumnWidth(col, self.columnWidth(col))
            else:
                self.__ftv_left.setColumnHidden(col, True)
        # 1for
        self.updateFrozenTableGeometry()

    def freezeToRow(self, row: int):
        self.__ftv_left.hide()
        self.__freeze_to_row = max(0, row)
        if self.__freeze_to_row > 0:
            self.__ftv_top.show()
        else:
            self.__ftv_top.hide()
        # 1if
        for row in range(self.model().rowCount()):
            if row < self.__freeze_to_row:
                self.__ftv_top.setRowHidden(row, False)
                self.__ftv_top.setRowHeight(row, self.rowHeight(row))
            else:
                self.__ftv_top.setRowHidden(row, True)
        # 1for
        self.updateFrozenTableGeometry()

    def updateFrozenTableSectionWidth(self, logicalIndex, oldSize, newSize):
        self.__ftv_left.setColumnHidden(logicalIndex, newSize == 0)
        self.__ftv_top.setColumnHidden(logicalIndex, newSize == 0)
        self.__ftv_left.setColumnWidth(logicalIndex, newSize)
        self.__ftv_top.setColumnWidth(logicalIndex, newSize)
        self.updateFrozenTableGeometry()

    def updateFrozenTableSectionHeight(self, logicalIndex, oldSize, newSize):
        self.__ftv_left.setRowHidden(logicalIndex, newSize == 0)
        self.__ftv_top.setRowHidden(logicalIndex, newSize == 0)
        self.__ftv_left.setRowHeight(logicalIndex, newSize)
        self.__ftv_top.setRowHeight(logicalIndex, newSize)
        self.updateFrozenTableGeometry()

    def updateTableColumnSectionWidth(self, logicalIndex, oldSize, newSize):
        if self.__ftv_left.isVisible() and logicalIndex < self.__freeze_to_column:
            self.setColumnHidden(logicalIndex, newSize == 0)
            self.setColumnWidth(logicalIndex, newSize)
            self.updateFrozenTableGeometry()
        elif self.__ftv_top.isVisible():
            self.setColumnHidden(logicalIndex, newSize == 0)
            self.setColumnWidth(logicalIndex, newSize)
            self.updateFrozenTableGeometry()

    def updateTableRowSectionHeight(self, logicalIndex, oldSize, newSize):
        if self.__ftv_top.isVisible() and logicalIndex < self.__freeze_to_row:
            self.setRowHidden(logicalIndex, newSize == 0)
            self.setRowHeight(logicalIndex, newSize)
            self.updateFrozenTableGeometry()

    def resizeEvent(self, event):
        super(FreezableTableView, self).resizeEvent(event)
        self.updateFrozenTableGeometry()

    def moveCursor(self, cursorAction, modifiers):
        current = super(FreezableTableView, self).moveCursor(cursorAction, modifiers)
        if (cursorAction == self.MoveLeft and
                self.current.column() > 0 and
                self.visualRect(current).topLeft().x() <
                    self.__ftv_left.columnWidth(0)):
            newValue = (self.horizontalScrollBar().value() +
                        self.visualRect(current).topLeft().x() -
                        self.__ftv_left.columnWidth(0))
            self.horizontalScrollBar().setValue(newValue)
        return current

    def scrollTo(self, index, hint):
        if index.column() > 0:
            super(FreezableTableView, self).scrollTo(index, hint)

    def updateFrozenTableGeometry(self):
        self.__ftv_left.setGeometry(
            self.verticalHeader().width() + self.frameWidth(),
            self.frameWidth(), sum(map(self.columnWidth, range(self.__freeze_to_column))),
            self.viewport().height() + self.horizontalHeader().height()
        )
        self.__ftv_top.setGeometry(
            self.frameWidth(),
            self.frameWidth(), self.viewport().width() + self.verticalHeader().width(),
            self.horizontalHeader().height() + self.frameWidth() + sum(map(self.rowHeight, range(self.__freeze_to_row)))
        )
        self.__ftv_top.verticalHeader().setFixedWidth(self.verticalHeader().width())

    def setSpan(self, row, column, rowSpan, colSpan):
        super().setSpan(row, column, rowSpan, colSpan)
        self.__ftv_top.setSpan(row, column, rowSpan, colSpan)
        self.__ftv_left.setSpan(row, column, rowSpan, colSpan)


def main(args):
    def split_and_strip(s, splitter):
        return [s.strip() for s in line.split(splitter)]

    app = QtWidgets.QApplication(args)
    model = QtGui.QStandardItemModel()
    file = QtCore.QFile(QtCore.QFileInfo(__file__).absolutePath() + '/grades.txt')
    if file.open(QtCore.QFile.ReadOnly):
        line = file.readLine(200).decode('utf-8')
        header = split_and_strip(line, ',')
        model.setHorizontalHeaderLabels(header)
        row = 0
        while file.canReadLine():
            line = file.readLine(200).decode('utf-8')
            if not line.startswith('#') and ',' in line:
                fields = split_and_strip(line, ',')
                for col, field in enumerate(fields):
                    newItem = QtGui.QStandardItem(field)
                    model.setItem(row, col, newItem)
                row += 1
    file.close()
    tableView = FreezableTableView(model)
    tableView.setWindowTitle("Frozen Column Example")
    tableView.resize(560, 680)
    tableView.freezeToRow(2)
    tableView.show()
    return app.exec_()


if __name__ == '__main__':
    import sys
    main(sys.argv)