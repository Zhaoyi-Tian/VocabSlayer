from typing import Union

from PyQt5 import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, SettingCard, FluentIconBase, PushSettingCard, \
    qconfig, PrimaryPushSettingCard


class CustomMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self,initial_url="", parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('设置API')
        self.urlLineEdit = LineEdit()

        self.urlLineEdit.setText(initial_url)
        self.urlLineEdit.setPlaceholderText('输入AI所需要的API（仅支持deepseek),重启后生效')
        self.urlLineEdit.setClearButtonEnabled(True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)


class StrSettingCard(PushSettingCard):
    """ Setting card with color picker """

    strChanged = pyqtSignal(str)

    def __init__(self, text,configItem, icon: Union[str, QIcon, FluentIconBase],
                 title: str, content: str = None, parent=None, enableAlpha=False):

        super().__init__(text,icon, title, content, parent)
        self.parent = parent
        self.button.setFixedSize(95, 30)
        self.configItem = configItem
        self.button.clicked.connect(self.showDialog)


    def showDialog(self):
        dialog = CustomMessageBox(initial_url=self.configItem.value, parent=self.parent)
        if dialog.exec():  # 用户点击确认
            new_url = dialog.urlLineEdit.text()
            qconfig.set(self.configItem,new_url) # 更新配置项
