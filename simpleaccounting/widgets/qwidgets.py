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

from qtpy import QtWidgets, QtCore, QtGui


class CustomQDialog(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint |
                            QtCore.Qt.WindowCloseButtonHint |
                            QtCore.Qt.CustomizeWindowHint)
        self.setModal(True)


class CustomInputDialog(CustomQDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 创建按钮框
        self.button_box = QtWidgets.QDialogButtonBox(self)
        # 添加标准按钮
        self.button_box.addButton(QtWidgets.QDialogButtonBox.Ok)  # 添加“确定”按钮
        self.button_box.addButton(QtWidgets.QDialogButtonBox.Cancel)  # 添加“取消”按钮
        # 连接按钮的点击信号
        self.button_box.accepted.connect(self.accept)  # 点击“确定”时接受对话框
        self.button_box.rejected.connect(self.reject)  # 点击“取消”时拒绝对话框


class CustomQComboBox(QtWidgets.QComboBox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumHeight(int(self.fontMetrics().height() * 2.0))


class HorizontalSpacer(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)