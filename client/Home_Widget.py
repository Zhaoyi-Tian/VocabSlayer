
from datetime import datetime, date,timedelta

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from qfluentwidgets import FluentIcon, ConfigItem, qconfig
from server.my_test import VocabularyLearningSystem
from home import Ui_home_widget
from appcard import AppCard
class HomeWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__()

        self.parent = parent
        self.configitem = self.parent.cfg.total_num
        self.ui = Ui_home_widget()
        self.ui.setupUi(self)
        self.card1=AppCard(
            FluentIcon.CHECKBOX,
            "常规训练",
            "选择难度从题库中抽题训练",
            self
        )
        self.card2 = AppCard(
            FluentIcon.LABEL,
            "复习训练",
            "从已做过的题中抽题训练",
            self
        )
        '''
        self.card3 = AppCard(
            FluentIcon.EXPRESSIVE_INPUT_ENTRY,
            "ai训练",
            "将错题单提供给ai,生成个性化题单",
            self
        )
        '''
        self.card4 = AppCard(
            QIcon("./resource/deepseek.png"),
            "deepseek",
            "和ai探讨问题",
            self
        )
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 10, 20, 20)
        content_layout.setSpacing(15)
        content_layout.addWidget(self.card1)
        content_layout.addWidget(self.card2)
        #content_layout.addWidget(self.card3)
        content_layout.addWidget(self.card4)
        self.ui.SmoothScrollArea.setWidget(content_widget)
        self.ui.SmoothScrollArea.setWidgetResizable(True)
        self.VLS=VocabularyLearningSystem()
        self.ui.HorizontalFlipView.addImage(self.VLS.show_day_stats())
        self.ui.HorizontalFlipView.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.HorizontalFlipView.setItemSize(QSize(561, 270))
        self.ui.HorizontalFlipView.setFixedSize(QSize(561, 270))
        self.card1.clicked.connect(lambda:self.parent.switchTo(self.parent.exam1Interface))
        self.card2.clicked.connect(lambda: self.parent.switchTo(self.parent.exam2Interface))
        #self.card3.clicked.connect(lambda: self.parent.switchTo(self.parent.exam3Interface))
        self.card4.clicked.connect(lambda: self.parent.switchTo(self.parent.aiInterface))
        self.card1.openButton.clicked.connect(lambda:self.parent.switchTo(self.parent.exam1Interface))
        self.card2.openButton.clicked.connect(lambda: self.parent.switchTo(self.parent.exam2Interface))
        #self.card3.openButton.clicked.connect(lambda: self.parent.switchTo(self.parent.exam3Interface))
        self.card4.openButton.clicked.connect(lambda: self.parent.switchTo(self.parent.aiInterface))
        # 获取今天的日期
        self.today = date.today()
        self.todayn=self.today.strftime('%Y年%m月%d日')
        # 获取星期几（0-6，0表示周一）
        self.weekday_num = self.today.weekday()
        # 获取中文星期几
        weekday_chinese = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][self.weekday_num]
        self.ui.StrongBodyLabel_2.setText(f"今天是{self.todayn},{weekday_chinese}")
        self.ui.ToolButton.clicked.connect(self.flush)
        self.ui.ToolButton.setIcon(FluentIcon.UPDATE)
        self.ui.ProgressBar.setValue(int(self.configitem.value/3000*100))
        self.ui.StrongBodyLabel.setText(f"{int(self.configitem.value)}/3000")
        self.ratio=1
        if str(self.VLS.dates[-1]) == str(self.today):
            self.lastflash = self.VLS.total[-1]
        else:
            self.lastflash=0
        self.flush()
    def flush(self):
        self.VLS=VocabularyLearningSystem()
        self.ui.HorizontalFlipView.clear()
        self.ui.HorizontalFlipView.addImage(self.VLS.show_day_stats())
        self.ui.SubtitleLabel.setText(f"您已连续练习{self.count_consecutive_days(self.VLS.dates)}天")
        self.ratio = 1 + self.count_consecutive_days(self.VLS.dates) * 0.1
        if str(self.VLS.dates[-1])==str(self.today):
            self.ui.HyperlinkLabel_2.setText(f"{self.VLS.total[-1]}")
            self.configitem.value +=self.VLS.total[-1]-self.lastflash
            self.lastflash = self.VLS.total[-1]
        else:
            self.ui.HyperlinkLabel_2.setText("0个")
        self.ui.HyperlinkLabel.setText(f"x{self.ratio}")

        self.ui.ProgressBar.setValue(int(self.configitem.value/3000*100))
        self.ui.StrongBodyLabel.setText(f"{int(self.configitem.value)}/3000")
        qconfig.save()
    def count_consecutive_days(self,date_list):
        # 1. 日期排序（确保升序）
        sorted_dates = sorted(date_list,reverse=True)

        # 2. 转换为datetime对象并检查连续性
        prev_date = None
        consecutive_days = 0

        for date_str in sorted_dates:
            curr_date = datetime.strptime(date_str, "%Y-%m-%d")

            # 处理第一个日期
            if prev_date is None:
                prev_date = curr_date
                consecutive_days = 1
                continue

            # 计算日期间隔
            delta = curr_date - prev_date
            if delta == timedelta(days=1):
                # 日期连续，天数+1
                consecutive_days += 1
                prev_date = curr_date
            else:
                # 日期不连续，返回当前连续天数
                return consecutive_days

        return consecutive_days
