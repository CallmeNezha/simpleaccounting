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

import abc
import weakref
import typing
from qtpy import QtWidgets, QtCore, QtGui
from simpleaccounting.tools import stringscores

VALID_ACCENT_CHARS = "ÁÉÍOÚáéíúóàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛäëïöüÄËÏÖÜñÑ"
VALID_FINDER_CHARS = r"[A-Za-z\s{0}0-9]".format(VALID_ACCENT_CHARS)


class CNSearchLineEdit(QtWidgets.QLineEdit):
    """QLineEdit for filtering listed elements in the parent widget."""
    sigKeyUpPressed = QtCore.Signal()
    sigKeyDownPressed = QtCore.Signal()
    sigKeyEnterReturnPressed = QtCore.Signal()
    sigTextChanged = QtCore.Signal(str)

    def __init__(self, parent=None, regexBase=VALID_FINDER_CHARS):
        super(CNSearchLineEdit, self).__init__(parent)
        # Widget setup
        if regexBase:
            regex = QtCore.QRegExp(regexBase + "{100}")
            self.setValidator(QtGui.QRegExpValidator(regex))
        else:
            pass
        # !fi
        self.textChanged.connect(self.sigTextChanged)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        if key == QtCore.Qt.Key_Up:
            self.sigKeyUpPressed.emit()
        elif key == QtCore.Qt.Key_Down:
            self.sigKeyDownPressed.emit()
        elif key in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.sigKeyEnterReturnPressed.emit()
        else:
            super(CNSearchLineEdit, self).keyPressEvent(event)


class CNCascadingListsWidgetItem(QtWidgets.QListWidgetItem):
    """CascadingListWidgetItem"""
    def __init__(self,
                 text: str,
                 icon: QtGui.QIcon=None,
                 parent: 'CNCascadingListsWidgetItem' =None,
                 typed=QtWidgets.QListWidgetItem.ItemType.UserType):
        """"""
        super().__init__(None, typed)
        self._text = text
        self._icon = icon or QtGui.QIcon()
        self._children = []
        self._parentItem = parent
        if self._parentItem:
            parent.addChild(self)

    def parent(self):
        return self._parentItem

    def setParent(self, item: typing.Optional['CNCascadingListsWidgetItem']):
        self._parentItem = item
        self._parentItem.addChild(self)

    def addChild(self, item: 'CNCascadingListsWidgetItem'):
        if item not in self._children:
            self._children.append(item)
            item.setParent(self)

    def removeChild(self, item: 'CNCascadingListsWidgetItem'):
        if item in self._children:
            self._children.remove(item)
            item.setParent(None)

    def children(self) -> typing.List['CNCascadingListsWidgetItem']:
        return self._children.copy()

    def text(self) -> str:
        return self._text

    def setText(self, text: str):
        self._text = text

    def icon(self) -> QtGui.QIcon:
        return self._icon

    def setIcon(self, icon: QtGui.QIcon):
        self._icon = icon


class CNCascadingListsWidget(QtWidgets.QWidget):

    sigItemClicked = QtCore.Signal(QtWidgets.QListWidgetItem)
    """Emitted when item is clicked"""
    sigItemDoubleClicked = QtCore.Signal(QtWidgets.QListWidgetItem)
    """Emitted when item is double clicked"""

    def __init__(self, parent=None, regexBase=None):
        super().__init__(parent)
        self._rootItem = CNCascadingListsWidgetItem("")
        self._currentRootItem = weakref.ref(self._rootItem)
        # search bar
        self.searchbar = CNSearchLineEdit(self, regexBase)
        self.searchbar.textEdited.connect(self.search)
        self.searchbar.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.PreventContextMenu)
        self.searchbar.setPlaceholderText("搜索...")
        self.searchbar.setClearButtonEnabled(True)
        self.searchbar.setStyleSheet('QLineEdit { border-width: 1px; border-radius: 0; }')
        # toolbar
        self.backwardTb = QtWidgets.QToolButton(self)
        self.backwardTb.setIcon(QtGui.QIcon())
        self.backwardTb.setFixedSize(24, 16)
        self.backwardTb.setStyleSheet('QToolButton { border: none; background: transparent; }')
        self.backwardTb.clicked.connect(self.backward)
        self.forwardTb = QtWidgets.QToolButton(self)
        self.forwardTb.setIcon(QtGui.QIcon())
        self.forwardTb.setFixedSize(24, 16)
        self.forwardTb.setStyleSheet('QToolButton { border: none; background: transparent; }')
        self.forwardTb.setDisabled(True)
        self.toolbar = QtWidgets.QToolBar(self)
        self.toolbar.setStyleSheet('QToolBar{ border-width: 0px 1px 0px 1px; '
                                   'border-radius: 0; background: transparent; }')
        self.titleLabel = QtWidgets.QLabel(self)
        self.titleLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.toolbar.addWidget(self.backwardTb)
        self.toolbar.addWidget(self.titleLabel)
        self.toolbar.addWidget(self.forwardTb)
        self.toolbar.setFixedHeight(self.titleLabel.height())
        # list widget
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setDragEnabled(True)
        self.listWidget.setDragDropMode(QtWidgets.QListWidget.DragDropMode.DragOnly)
        self.listWidget.setStyleSheet('QListWidget { border-width: 1px; border-radius: 0;}')
        self.listWidget.itemClicked.connect(self.sigItemClicked)
        self.listWidget.itemDoubleClicked.connect(self.sigItemDoubleClicked)
        self.listWidget.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.listWidget.setSelectionMode(QtWidgets.QListWidget.SingleSelection)
        self.listWidget.setSelectionBehavior(QtWidgets.QListWidget.SelectionBehavior.SelectItems)
        self.listWidget.startDrag = self.startDrag
        # layout widget
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.searchbar)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.listWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # widget geometry changing
        self._pressed = False
        self._lastPosition = self.pos()

        # install event filter
        self.titleLabel.installEventFilter(self)
        self.searchbar.installEventFilter(self)
        self.listWidget.installEventFilter(self)

    def show(self):
        """Override show method to set user frequently used edit focused"""
        self.searchbar.setFocus()
        super().show()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._pressed:
            self.move(self.mapToParent(event.pos() - self._lastPosition))

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if obj is self.titleLabel and event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if not self._pressed:
                self._lastPosition = self.titleLabel.mapTo(self, event.pos())
            self._pressed = True
            return True
        if obj is self.titleLabel and event.type() == QtCore.QEvent.Type.MouseButtonRelease:
            self._pressed = False
            return True

        if event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key_Down:
                self.listWidget.setCurrentRow((self.listWidget.currentRow() + 1) % self.listWidget.count())
            elif event.key() == QtCore.Qt.Key_Up:
                self.listWidget.setCurrentRow((self.listWidget.currentRow() - 1) % self.listWidget.count())
            elif event.key() == QtCore.Qt.Key_Return:
                self.onItemDoubleClicked()
            elif event.key() == QtCore.Qt.Key_Left:
                self.backward()
            elif event.key() == QtCore.Qt.Key_Right:
                self.onItemDoubleClicked()
        return False

    @abc.abstractmethod
    def startDrag(self, supportActions):
        pass

    def search(self, partialItemText: str):
        """"""
        if not partialItemText:
            self.setCurrentRoot(self._rootItem)
            return
        else:
            self.backwardTb.setIcon(QtGui.QIcon())
            self.backwardTb.setDisabled(True)
            self.titleLabel.setText(f'搜索 {partialItemText!r}')
        rets = stringscores.findMatchingChoices(
            partialItemText,
            list(self.items.keys()),
            template='<b>{0}</b>',
            valid_only=True,
            sort=True
        )
        matchedItems = []
        labels = []
        for name, named, _ in rets:
            matchedItems.append(self.items[name])
            labels.append(named)
        self.refresh(matchedItems, labels)

    def setRoot(self, root: CNCascadingListsWidgetItem):
        self._rootItem = root
        self.setCurrentRoot(self._rootItem)
        self.items = {}

        def recursiveGet(item: CNCascadingListsWidgetItem):
            if not item.children():
                self.items[item.text()] = item
            for child in item.children():
                recursiveGet(child)

        #
        recursiveGet(self._rootItem)

    def setCurrentRoot(self, root: CNCascadingListsWidgetItem):
        self._currentRootItem = weakref.ref(root)
        self.titleLabel.setText(self._currentRootItem().text())
        if self._currentRootItem().parent():
            self.backwardTb.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowBack))
            self.backwardTb.setEnabled(True)
        else:
            self.backwardTb.setIcon(QtGui.QIcon())
            self.backwardTb.setDisabled(True)
        # !if
        self.refresh(self._currentRootItem().children())

    def refresh(self, items: typing.List[CNCascadingListsWidgetItem], labels: typing.List[str] = None):

        # clear items, we don't use  :meth:`clear` because it will delete item's object in list
        # we don't want to delete them we just want to remove them.
        while self.listWidget.count():
            self.listWidget.takeItem(0)

        if labels is None:
            labels = [item.text() for item in items]

        for item, label in zip(items, labels):

            QtWidgets.QApplication.instance().processEvents()
            self.listWidget.addItem(item)
            icon = QtWidgets.QLabel()
            icon.setPixmap(item.icon().pixmap(16, 16))
            icon.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
            label = QtWidgets.QLabel(label)
            label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

            widget = QtWidgets.QWidget()
            widget.setStyleSheet('background: transparent;')
            layout = QtWidgets.QHBoxLayout(widget)
            layout.setContentsMargins(4, 0, 4, 0)
            layout.setSpacing(4)
            layout.addWidget(icon)
            layout.addWidget(label)
            layout.addStretch()
            if item.children():
                tb = QtWidgets.QToolButton()
                tb.setFixedSize(16, 16)
                tb.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowForward))
                tb.setStyleSheet('border: none; background: transparent;')
                tb.clicked.connect(lambda f, t=item: self.setCurrentRoot(t))
                layout.addWidget(tb)
            self.listWidget.setItemWidget(item, widget)


    def backward(self):
        if not self._currentRootItem().parent():
            return

        lastRootItem = self._currentRootItem()
        self.setCurrentRoot(lastRootItem.parent())
        self.listWidget.setCurrentItem(lastRootItem)

    def onItemDoubleClicked(self):
        if not self.listWidget.currentItem():
            return
        item: CNCascadingListsWidgetItem = self.listWidget.currentItem()  # noqa
        if item.children():
            self.setCurrentRoot(item)

    def selectedItems(self) -> typing.List[CNCascadingListsWidgetItem]:
        return self.listWidget.selectedItems() # noqa


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)

    fuzzyFinder = CNCascadingListsWidget()
    fuzzyFinder.titleLabel.setText("example")
    fuzzyFinder.show()

    icon = fuzzyFinder.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_TitleBarMenuButton)
    root = CNCascadingListsWidgetItem("Root")
    child1 = CNCascadingListsWidgetItem("Child 1", icon, parent=root)
    child1child = CNCascadingListsWidgetItem("Child 1's child", icon, parent=child1)
    child2 = CNCascadingListsWidgetItem("Child 2", parent=root)

    fuzzyFinder.setRoot(root)

    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
