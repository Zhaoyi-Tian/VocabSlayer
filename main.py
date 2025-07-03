import os
import shutil
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QApplication, QDialog
from qfluentwidgets import NavigationItemPosition, FluentWindow, SubtitleLabel, setFont, setThemeColor
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow.utils import getSystemAccentColor

from main_window import Window,LoginDialog
from startup_screen import Splash_Screen
if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)  # 启用高DPI缩放
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)  # 使用高DPI图标
    if sys.platform in ["win32", "darwin"]:
        setThemeColor(getSystemAccentColor(), save=False)
    Splash_Screen()
    login_dialog = LoginDialog()
    if login_dialog.exec_()==QDialog.Accepted:
        username = login_dialog.ui.LineEdit_2.text().strip()
        mainWindow = Window(username)
        mainWindow.show()
    app.exec()
