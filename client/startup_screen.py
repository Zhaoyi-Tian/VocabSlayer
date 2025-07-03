# coding:utf-8

from PyQt5.QtCore import QSize, QEventLoop, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import SplashScreen
from qframelesswindow import FramelessWindow, StandardTitleBar

# coding:utf-8
from qfluentwidgets import SplashScreen
from qframelesswindow import FramelessWindow, StandardTitleBar


class Splash_Screen(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setFixedSize(700, 600)
        self.setWindowTitle('PyQt-Fluent-Widgets')
        self.setWindowIcon(QIcon('./resource/logo.png'))

        # 1. 创建启动页面
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(256, 256))
        self.show()
        self.center()
        # 2. 创建子界面
        self.createSubInterface()
        # 3. 隐藏启动页面
        self.splashScreen.close()
        self.close()
    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(2000, loop.quit)
        loop.exec()
    def center(self):
        """将窗口居中显示的方法"""
        # 获取屏幕的几何信息（分辨率）
        screen_geometry = QApplication.desktop().screenGeometry()
        # 获取窗口的几何信息
        window_geometry = self.frameGeometry()
        # 计算居中位置：屏幕中心减去窗口一半大小
        window_geometry.moveCenter(screen_geometry.center())
        # 将窗口移动到计算好的位置
        self.move(window_geometry.topLeft())

