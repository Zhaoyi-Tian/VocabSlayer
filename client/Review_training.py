from time import time

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QWidget, QStackedLayout, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import FluentWindow, NavigationItemPosition, PrimaryPushButton, RadioButton, RoundMenu, Action, \
    FluentIcon

from End import Ui_End
from quiz import Ui_quiz
from start_review import Ui_Form
from server.my_test import VocabularyLearningSystem


# 考试流程控制类
class ExamManager:
    def __init__(self):
        self.total_questions = 30  # 总题数
        self.current_index = 0  # 当前题号
        self.correct_count = 0  # 正确计数

    @property
    def progress(self):
        """ 计算当前进度百分比 """
        return int(self.current_index / self.total_questions * 100)

    @property
    def accuracy(self):
        if self.current_index==0:
            return 100
        return int(self.correct_count / self.current_index * 100)
    def reset(self):
        """ 重置考试状态 """
        self.current_index = 0
        self.correct_count = 0
    def move_next(self):
        """ 进入下一题，返回是否完成 """
        self.current_index += 1
        return self.current_index < self.total_questions


# 封装开始界面
class StartWidget(QWidget, Ui_Form):
    start_requested = pyqtSignal()  # 开始考试信号

    def __init__(self, VLS:VocabularyLearningSystem,parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setupUi(self)
        self._init_ui()
        self.VLS = VLS
        self.ComboBox_3.addItems(["English", "Chinese","Japanese"])
        self.ComboBox_3.setPlaceholderText("请选择主语言")
        self.ComboBox_4.addItems(["English", "Chinese","Japanese"])
        self.ComboBox_4.setPlaceholderText("请选择学习语言")
        self.ComboBox_3.currentIndexChanged.connect(lambda i: self.update_mainlanguage(i))
        self.ComboBox_4.currentIndexChanged.connect(lambda i: self.update_studylanguage(i))
        self.level = 2
        self.mainlanguage="Chinese"
        self.studylanguage="English"
        self.PillPushButton.setIcon(FluentIcon.SEND)

    def update_level(self,index):
        self.level = index + 2
    def update_mainlanguage(self,index):
        l=["English", "Chinese","Japanese"]
        self.mainlanguage = l[index]
    def update_studylanguage(self,index):
        l=["English", "Chinese","Japanese"]
        self.studylanguage = l[index]
    def _init_ui(self):
        """ 初始化界面交互 """
        # 设置按钮点击事件
        self.PillPushButton.clicked.connect(self._on_start_clicked)

    def _on_start_clicked(self):
        """ 触发开始考试信号 """
        self.parent.manager.total_questions = self.SpinBox.value()
        self.VLS.choose_level(self.level)
        self.VLS.set_languages(self.mainlanguage,self.studylanguage)
        self.start_requested.emit()


# 封装答题界面
class QuizWidget(QWidget, Ui_quiz):
    next_requested = pyqtSignal()  # 下一题请求信号
    finish_requested = pyqtSignal()  # 完成考试信号

    def __init__(self, VLS:VocabularyLearningSystem,manager: ExamManager, parent=None):
        super().__init__(parent)
        self.VLS = VLS
        self.setupUi(self)
        self.manager = manager
        self.parent = parent
        self._init_ui()

    def _init_ui(self):
        """ 初始化答题界面 """
        # 设置按钮文本
        self.PrimaryPushButton.setText("Next")
        self.PrimaryPushButton.setEnabled(False)
        self.PushButton.setText("Check")
        self.PrimaryPushButton.clicked.connect(self._on_next_clicked)
        self.PushButton.clicked.connect(self._on_check_clicked)
        # 初始化题目显示
        self.currentoption=None
        self.RadioButton.toggled.connect(lambda checked: self.on_radio_toggled(checked, self.RadioButton))
        self.RadioButton_2.toggled.connect(lambda checked: self.on_radio_toggled(checked, self.RadioButton_2))
        self.RadioButton_3.toggled.connect(lambda checked: self.on_radio_toggled(checked, self.RadioButton_3))
        self.RadioButton_4.toggled.connect(lambda checked: self.on_radio_toggled(checked, self.RadioButton_4))
        self.RadioButton.option='A'
        self.RadioButton_2.option = 'B'
        self.RadioButton_3.option='C'
        self.RadioButton_4.option='D'
        menu = RoundMenu(parent=self.SplitToolButton)
        menu.addAction(Action(QIcon("./resource/deepseek.png"), '问问deepseek', triggered=lambda: self.askdeepseek()))
        self.SplitToolButton.setFlyout(menu)
        self.SplitToolButton.setIcon(FluentIcon.HEART)
        self.SplitToolButton.clicked.connect(lambda: self.addtobook())
        self.n=0 #跟踪爱心
        self.ProgressRing.setVal(100)
    @pyqtSlot(bool, RadioButton)
    def on_radio_toggled(self, checked, button):
        if checked:
            self.currentoption=button.option
    def _load_question(self):
        """ 加载当前题目（示例数据） """
        # 此处应替换为实际题目数据加载逻辑
        self.n=0
        self.SplitToolButton.setIcon(FluentIcon.HEART)
        self.BodyLabel.setVisible(False)
        self.SubtitleLabel.setVisible(False)
        self.RadioButton.setChecked(False)
        self.RadioButton_2.setChecked(False)
        self.RadioButton_3.setChecked(False)
        self.RadioButton_4.setChecked(False)
        self.RadioButton.setEnabled(True)
        self.RadioButton_2.setEnabled(True)
        self.RadioButton_3.setEnabled(True)
        self.RadioButton_4.setEnabled(True)
        self.PushButton.setEnabled(True)
        self.PushButton.setText("Check")
        self.PushButton.setStyleSheet("""PushButton, ToolButton, ToggleButton, ToggleToolButton {
    color: black;
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(0, 0, 0, 0.073);
    border-bottom: 1px solid rgba(0, 0, 0, 0.183);
    border-radius: 5px;
    /* font: 14px 'Segoe UI', 'Microsoft YaHei'; */
    padding: 5px 12px 6px 12px;
    outline: none;
}

ToolButton {
    padding: 5px 9px 6px 8px;
}

PushButton[hasIcon=false] {
    padding: 5px 12px 6px 12px;
}

PushButton[hasIcon=true] {
    padding: 5px 12px 6px 36px;
}

DropDownToolButton, PrimaryDropDownToolButton {
    padding: 5px 31px 6px 8px;
}

DropDownPushButton[hasIcon=false],
PrimaryDropDownPushButton[hasIcon=false] {
    padding: 5px 31px 6px 12px;
}

DropDownPushButton[hasIcon=true],
PrimaryDropDownPushButton[hasIcon=true] {
    padding: 5px 31px 6px 36px;
}

PushButton:hover, ToolButton:hover, ToggleButton:hover, ToggleToolButton:hover {
    background: rgba(249, 249, 249, 0.5);
}

PushButton:pressed, ToolButton:pressed, ToggleButton:pressed, ToggleToolButton:pressed {
    color: rgba(0, 0, 0, 0.63);
    background: rgba(249, 249, 249, 0.3);
    border-bottom: 1px solid rgba(0, 0, 0, 0.073);
}

PushButton:disabled, ToolButton:disabled, ToggleButton:disabled, ToggleToolButton:disabled {
    color: rgba(0, 0, 0, 0.36);
    background: rgba(249, 249, 249, 0.3);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}


PrimaryPushButton,
PrimaryToolButton,
ToggleButton:checked,
ToggleToolButton:checked {
    color: white;
    background-color: #009faa;
    border: 1px solid #00a7b3;
    border-bottom: 1px solid #007780;
}

PrimaryPushButton:hover,
PrimaryToolButton:hover,
ToggleButton:checked:hover,
ToggleToolButton:checked:hover {
    background-color: #00a7b3;
    border: 1px solid #2daab3;
    border-bottom: 1px solid #007780;
}

PrimaryPushButton:pressed,
PrimaryToolButton:pressed,
ToggleButton:checked:pressed,
ToggleToolButton:checked:pressed {
    color: rgba(255, 255, 255, 0.63);
    background-color: #3eabb3;
    border: 1px solid #3eabb3;
}

PrimaryPushButton:disabled,
PrimaryToolButton:disabled,
ToggleButton:checked:disabled,
ToggleToolButton:checked:disabled {
    color: rgba(255, 255, 255, 0.9);
    background-color: rgb(205, 205, 205);
    border: 1px solid rgb(205, 205, 205);
}

SplitDropButton,
PrimarySplitDropButton {
    border-left: none;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
}

#splitPushButton,
#splitToolButton,
#primarySplitPushButton,
#primarySplitToolButton {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
}

#splitPushButton:pressed,
#splitToolButton:pressed,
SplitDropButton:pressed {
    border-bottom: 1px solid rgba(0, 0, 0, 0.183);
}

PrimarySplitDropButton:pressed {
    border-bottom: 1px solid #007780;
}

#primarySplitPushButton, #primarySplitToolButton {
    border-right: 1px solid #3eabb3;
}

#primarySplitPushButton:pressed, #primarySplitToolButton:pressed {
    border-bottom: 1px solid #007780;
}

HyperlinkButton {
    /* font: 14px 'Segoe UI', 'Microsoft YaHei'; */
    padding: 6px 12px 6px 12px;
    color: #009faa;
    border: none;
    border-radius: 6px;
    background-color: transparent;
}

HyperlinkButton[hasIcon=false] {
    padding: 6px 12px 6px 12px;
}

HyperlinkButton[hasIcon=true] {
    padding: 6px 12px 6px 36px;
}

HyperlinkButton:hover {
    color: #009faa;
    background-color: rgba(0, 0, 0, 10);
    border: none;
}

HyperlinkButton:pressed {
    color: #009faa;
    background-color: rgba(0, 0, 0, 6);
    border: none;
}

HyperlinkButton:disabled {
    color: rgba(0, 0, 0, 0.43);
    background-color: transparent;
    border: none;
}


RadioButton {
    min-height: 24px;
    max-height: 24px;
    background-color: transparent;
    font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
    color: black;
}

RadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 11px;
    border: 2px solid #999999;
    background-color: rgba(0, 0, 0, 5);
    margin-right: 4px;
}

RadioButton::indicator:hover {
    background-color: rgba(0, 0, 0, 0);
}

RadioButton::indicator:pressed {
    border: 2px solid #bbbbbb;
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 rgb(225, 224, 223),
            stop:1 rgb(225, 224, 223));
}

RadioButton::indicator:checked {
    height: 22px;
    width: 22px;
    border: none;
    border-radius: 11px;
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 #009faa,
            stop:1 #009faa);
}

RadioButton::indicator:checked:hover {
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.6 rgb(255, 255, 255),
            stop:0.7 #009faa,
            stop:1 #009faa);
}

RadioButton::indicator:checked:pressed {
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 #009faa,
            stop:1 #009faa);
}

RadioButton:disabled {
    color: rgba(0, 0, 0, 110);
}

RadioButton::indicator:disabled {
    border: 2px solid #bbbbbb;
    background-color: transparent;
}

RadioButton::indicator:disabled:checked {
    border: none;
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 rgba(0, 0, 0, 0.2169),
            stop:1 rgba(0, 0, 0, 0.2169));
}

TransparentToolButton,
TransparentToggleToolButton,
TransparentDropDownToolButton,
TransparentPushButton,
TransparentDropDownPushButton,
TransparentTogglePushButton {
    background-color: transparent;
    border: none;
    border-radius: 5px;
    margin: 0;
}

TransparentToolButton:hover,
TransparentToggleToolButton:hover,
TransparentDropDownToolButton:hover,
TransparentPushButton:hover,
TransparentDropDownPushButton:hover,
TransparentTogglePushButton:hover {
    background-color: rgba(0, 0, 0, 9);
    border: none;
}

TransparentToolButton:pressed,
TransparentToggleToolButton:pressed,
TransparentDropDownToolButton:pressed,
TransparentPushButton:pressed,
TransparentDropDownPushButton:pressed,
TransparentTogglePushButton:pressed {
    background-color: rgba(0, 0, 0, 6);
    border: none;
}

TransparentToolButton:disabled,
TransparentToggleToolButton:disabled,
TransparentDropDownToolButton:disabled,
TransprentPushButton:disabled,
TransparentDropDownPushButton:disabled,
TransprentTogglePushButton:disabled {
    background-color: transparent;
    border: none;
}


PillPushButton,
PillPushButton:hover,
PillPushButton:pressed,
PillPushButton:disabled,
PillPushButton:checked,
PillPushButton:checked:hover,
PillPushButton:checked:pressed,
PillPushButton:disabled:checked,
PillToolButton,
PillToolButton:hover,
PillToolButton:pressed,
PillToolButton:disabled,
PillToolButton:checked,
PillToolButton:checked:hover,
PillToolButton:checked:pressed,
PillToolButton:disabled:checked {
    background-color: transparent;
    border: none;
}
""")
        self.PrimaryPushButton.setEnabled(False)
        self.start_time = time()
        question, self.options, self.answer, self.word=self.VLS.generate_review_question()
        self.CaptionLabel.setText(question)
        if len(self.options) == 4:
            self.RadioButton.setText(str(self.options['A']))
            self.RadioButton_2.setText(str(self.options['B']))
            self.RadioButton_3.setText(str(self.options['C']))
            self.RadioButton_4.setText(str(self.options['D']))
            self.RadioButton.setVisible(True)
            self.RadioButton_2.setVisible(True)
            self.RadioButton_3.setVisible(True)
            self.RadioButton_4.setVisible(True)
        if len(self.options) == 2:
            self.RadioButton.setText(self.options['A'])
            self.RadioButton_3.setText(self.options['C'])
            self.RadioButton.setVisible(True)
            self.RadioButton_2.setVisible(False)
            self.RadioButton_3.setVisible(True)
            self.RadioButton_4.setVisible(False)

        # 更新进度显示
        self.ProgressBar.setVal(self.manager.progress)
        self.ProgressRing.setVal(self.manager.accuracy)

    def _on_check_clicked(self):
        time_used = time() - self.start_time

        if self.currentoption is None:
            return
        self.RadioButton.setEnabled(False)
        self.RadioButton_2.setEnabled(False)
        self.RadioButton_3.setEnabled(False)
        self.RadioButton_4.setEnabled(False)
        if self.currentoption == self.answer:
            # 正确时样式
            self.PushButton.setText("正确")
            self.PushButton.setStyleSheet("""PushButton, ToolButton, ToggleButton, ToggleToolButton {
    color: black;
    background: rgba(220, 255, 220, 0.7);
    border: 1px solid rgba(0, 100, 0, 0.073);
    border-bottom: 1px solid rgba(0, 100, 0, 0.183);
    border-radius: 5px;
    /* font: 14px 'Segoe UI', 'Microsoft YaHei'; */
    padding: 5px 12px 6px 12px;
    outline: none;
}

ToolButton {
    padding: 5px 9px 6px 8px;
}

PushButton[hasIcon=false] {
    padding: 5px 12px 6px 12px;
}

PushButton[hasIcon=true] {
    padding: 5px 12px 6px 36px;
}

DropDownToolButton, PrimaryDropDownToolButton {
    padding: 5px 31px 6px 8px;
}

DropDownPushButton[hasIcon=false],
PrimaryDropDownPushButton[hasIcon=false] {
    padding: 5px 31px 6px 12px;
}

DropDownPushButton[hasIcon=true],
PrimaryDropDownPushButton[hasIcon=true] {
    padding: 5px 31px 6px 36px;
}

PushButton:hover, ToolButton:hover, ToggleButton:hover, ToggleToolButton:hover {
    background: rgba(200, 255, 200, 0.5);
}

PushButton:pressed, ToolButton:pressed, ToggleButton:pressed, ToggleToolButton:pressed {
    color: rgba(0, 0, 0, 0.63);
    background: rgba(180, 255, 180, 0.3);
    border-bottom: 1px solid rgba(0, 100, 0, 0.073);
}

PushButton:disabled, ToolButton:disabled, ToggleButton:disabled, ToggleToolButton:disabled {
    color: rgba(0, 0, 0, 0.36);
    background: rgba(200, 255, 200, 0.3);
    border: 1px solid rgba(0, 100, 0, 0.06);
    border-bottom: 1px solid rgba(0, 100, 0, 0.06);
}


PrimaryPushButton,
PrimaryToolButton,
ToggleButton:checked,
ToggleToolButton:checked {
    color: white;
    background-color: #2ecc71;
    border: 1px solid #36d378;
    border-bottom: 1px solid #27ae60;
}

PrimaryPushButton:hover,
PrimaryToolButton:hover,
ToggleButton:checked:hover,
ToggleToolButton:checked:hover {
    background-color: #36d378;
    border: 1px solid #40d980;
    border-bottom: 1px solid #27ae60;
}

PrimaryPushButton:pressed,
PrimaryToolButton:pressed,
ToggleButton:checked:pressed,
ToggleToolButton:checked:pressed {
    color: rgba(255, 255, 255, 0.63);
    background-color: #40d980;
    border: 1px solid #40d980;
}

PrimaryPushButton:disabled,
PrimaryToolButton:disabled,
ToggleButton:checked:disabled,
ToggleToolButton:checked:disabled {
    color: rgba(255, 255, 255, 0.9);
    background-color: rgb(205, 205, 205);
    border: 1px solid rgb(205, 205, 205);
}

SplitDropButton,
PrimarySplitDropButton {
    border-left: none;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
}

#splitPushButton,
#splitToolButton,
#primarySplitPushButton,
#primarySplitToolButton {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
}

#splitPushButton:pressed,
#splitToolButton:pressed,
SplitDropButton:pressed {
    border-bottom: 1px solid rgba(0, 100, 0, 0.183);
}

PrimarySplitDropButton:pressed {
    border-bottom: 1px solid #27ae60;
}

#primarySplitPushButton, #primarySplitToolButton {
    border-right: 1px solid #40d980;
}

#primarySplitPushButton:pressed, #primarySplitToolButton:pressed {
    border-bottom: 1px solid #27ae60;
}

HyperlinkButton {
    /* font: 14px 'Segoe UI', 'Microsoft YaHei'; */
    padding: 6px 12px 6px 12px;
    color: #2ecc71;
    border: none;
    border-radius: 6px;
    background-color: transparent;
}

HyperlinkButton[hasIcon=false] {
    padding: 6px 12px 6px 12px;
}

HyperlinkButton[hasIcon=true] {
    padding: 6px 12px 6px 36px;
}

HyperlinkButton:hover {
    color: #2ecc71;
    background-color: rgba(0, 100, 0, 10);
    border: none;
}

HyperlinkButton:pressed {
    color: #2ecc71;
    background-color: rgba(0, 100, 0, 6);
    border: none;
}

HyperlinkButton:disabled {
    color: rgba(0, 0, 0, 0.43);
    background-color: transparent;
    border: none;
}


RadioButton {
    min-height: 24px;
    max-height: 24px;
    background-color: transparent;
    font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
    color: black;
}

RadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 11px;
    border: 2px solid #999999;
    background-color: rgba(0, 100, 0, 5);
    margin-right: 4px;
}

RadioButton::indicator:hover {
    background-color: rgba(0, 100, 0, 0);
}

RadioButton::indicator:pressed {
    border: 2px solid #bbbbbb;
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 rgb(225, 224, 223),
            stop:1 rgb(225, 224, 223));
}

RadioButton::indicator:checked {
    height: 22px;
    width: 22px;
    border: none;
    border-radius: 11px;
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 #2ecc71,
            stop:1 #2ecc71);
}

RadioButton::indicator:checked:hover {
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.6 rgb(255, 255, 255),
            stop:0.7 #2ecc71,
            stop:1 #2ecc71);
}

RadioButton::indicator:checked:pressed {
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 #2ecc71,
            stop:1 #2ecc71);
}

RadioButton:disabled {
    color: rgba(0, 0, 0, 110);
}

RadioButton::indicator:disabled {
    border: 2px solid #bbbbbb;
    background-color: transparent;
}

RadioButton::indicator:disabled:checked {
    border: none;
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 rgba(0, 0, 0, 0.2169),
            stop:1 rgba(0, 0, 0, 0.2169));
}

TransparentToolButton,
TransparentToggleToolButton,
TransparentDropDownToolButton,
TransparentPushButton,
TransparentDropDownPushButton,
TransparentTogglePushButton {
    background-color: transparent;
    border: none;
    border-radius: 5px;
    margin: 0;
}

TransparentToolButton:hover,
TransparentToggleToolButton:hover,
TransparentDropDownToolButton:hover,
TransparentPushButton:hover,
TransparentDropDownPushButton:hover,
TransparentTogglePushButton:hover {
    background-color: rgba(0, 100, 0, 9);
    border: none;
}

TransparentToolButton:pressed,
TransparentToggleToolButton:pressed,
TransparentDropDownToolButton:pressed,
TransparentPushButton:pressed,
TransparentDropDownPushButton:pressed,
TransparentTogglePushButton:pressed {
    background-color: rgba(0, 100, 0, 6);
    border: none;
}

TransparentToolButton:disabled,
TransparentToggleToolButton:disabled,
TransparentDropDownToolButton:disabled,
TransprentPushButton:disabled,
TransparentDropDownPushButton:disabled,
TransprentTogglePushButton:disabled {
    background-color: transparent;
    border: none;
}


PillPushButton,
PillPushButton:hover,
PillPushButton:pressed,
PillPushButton:disabled,
PillPushButton:checked,
PillPushButton:checked:hover,
PillPushButton:checked:pressed,
PillPushButton:disabled:checked,
PillToolButton,
PillToolButton:hover,
PillToolButton:pressed,
PillToolButton:disabled,
PillToolButton:checked,
PillToolButton:checked:hover,
PillToolButton:checked:pressed,
PillToolButton:disabled:checked {
    background-color: transparent;
    border: none;
}""")
        else:
            # 错误时样式
            self.PushButton.setText("错误")
            self.PushButton.setStyleSheet("""PushButton, ToolButton, ToggleButton, ToggleToolButton {
    color: black;
    background: rgba(255, 220, 220, 0.7);
    border: 1px solid rgba(200, 0, 0, 0.073);
    border-bottom: 1px solid rgba(200, 0, 0, 0.183);
    border-radius: 5px;
    /* font: 14px 'Segoe UI', 'Microsoft YaHei'; */
    padding: 5px 12px 6px 12px;
    outline: none;
}

ToolButton {
    padding: 5px 9px 6px 8px;
}

PushButton[hasIcon=false] {
    padding: 5px 12px 6px 12px;
}

PushButton[hasIcon=true] {
    padding: 5px 12px 6px 36px;
}

DropDownToolButton, PrimaryDropDownToolButton {
    padding: 5px 31px 6px 8px;
}

DropDownPushButton[hasIcon=false],
PrimaryDropDownPushButton[hasIcon=false] {
    padding: 5px 31px 6px 12px;
}

DropDownPushButton[hasIcon=true],
PrimaryDropDownPushButton[hasIcon=true] {
    padding: 5px 31px 6px 36px;
}

PushButton:hover, ToolButton:hover, ToggleButton:hover, ToggleToolButton:hover {
    background: rgba(255, 200, 200, 0.5);
}

PushButton:pressed, ToolButton:pressed, ToggleButton:pressed, ToggleToolButton:pressed {
    color: rgba(0, 0, 0, 0.63);
    background: rgba(255, 180, 180, 0.3);
    border-bottom: 1px solid rgba(200, 0, 0, 0.073);
}

PushButton:disabled, ToolButton:disabled, ToggleButton:disabled, ToggleToolButton:disabled {
    color: rgba(0, 0, 0, 0.63);
    background: rgba(255, 200, 200, 0.3);
    border: 1px solid rgba(200, 0, 0, 0.06);
    border-bottom: 1px solid rgba(200, 0, 0, 0.06);
}


PrimaryPushButton,
PrimaryToolButton,
ToggleButton:checked,
ToggleToolButton:checked {
    color: white;
    background-color: #d63333;
    border: 1px solid #e04b4b;
    border-bottom: 1px solid #a32929;
}

PrimaryPushButton:hover,
PrimaryToolButton:hover,
ToggleButton:checked:hover,
ToggleToolButton:checked:hover {
    background-color: #e04b4b;
    border: 1px solid #e56464;
    border-bottom: 1px solid #a32929;
}

PrimaryPushButton:pressed,
PrimaryToolButton:pressed,
ToggleButton:checked:pressed,
ToggleToolButton:checked:pressed {
    color: rgba(255, 255, 255, 0.63);
    background-color: #e56464;
    border: 1px solid #e56464;
}

PrimaryPushButton:disabled,
PrimaryToolButton:disabled,
ToggleButton:checked:disabled,
ToggleToolButton:checked:disabled {
    color: rgba(255, 255, 255, 0.9);
    background-color: rgb(205, 205, 205);
    border: 1px solid rgb(205, 205, 205);
}

SplitDropButton,
PrimarySplitDropButton {
    border-left: none;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
}

#splitPushButton,
#splitToolButton,
#primarySplitPushButton,
#primarySplitToolButton {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
}

#splitPushButton:pressed,
#splitToolButton:pressed,
SplitDropButton:pressed {
    border-bottom: 1px solid rgba(200, 0, 0, 0.183);
}

PrimarySplitDropButton:pressed {
    border-bottom: 1px solid #a32929;
}

#primarySplitPushButton, #primarySplitToolButton {
    border-right: 1px solid #e56464;
}

#primarySplitPushButton:pressed, #primarySplitToolButton:pressed {
    border-bottom: 1px solid #a32929;
}

HyperlinkButton {
    /* font: 14px 'Segoe UI', 'Microsoft YaHei'; */
    padding: 6px 12px 6px 12px;
    color: #d63333;
    border: none;
    border-radius: 6px;
    background-color: transparent;
}

HyperlinkButton[hasIcon=false] {
    padding: 6px 12px 6px 12px;
}

HyperlinkButton[hasIcon=true] {
    padding: 6px 12px 6px 36px;
}

HyperlinkButton:hover {
    color: #d63333;
    background-color: rgba(200, 0, 0, 10);
    border: none;
}

HyperlinkButton:pressed {
    color: #d63333;
    background-color: rgba(200, 0, 0, 6);
    border: none;
}

HyperlinkButton:disabled {
    color: rgba(0, 0, 0, 0.43);
    background-color: transparent;
    border: none;
}


RadioButton {
    min-height: 24px;
    max-height: 24px;
    background-color: transparent;
    font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
    color: black;
}

RadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 11px;
    border: 2px solid #999999;
    background-color: rgba(200, 0, 0, 5);
    margin-right: 4px;
}

RadioButton::indicator:hover {
    background-color: rgba(200, 0, 0, 0);
}

RadioButton::indicator:pressed {
    border: 2px solid #bbbbbb;
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 rgb(225, 224, 223),
            stop:1 rgb(225, 224, 223));
}

RadioButton::indicator:checked {
    height: 22px;
    width: 22px;
    border: none;
    border-radius: 11px;
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 #d63333,
            stop:1 #d63333);
}

RadioButton::indicator:checked:hover {
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.6 rgb(255, 255, 255),
            stop:0.7 #d63333,
            stop:1 #d63333);
}

RadioButton::indicator:checked:pressed {
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 #d63333,
            stop:1 #d63333);
}

RadioButton:disabled {
    color: rgba(0, 0, 0, 110);
}

RadioButton::indicator:disabled {
    border: 2px solid #bbbbbb;
    background-color: transparent;
}

RadioButton::indicator:disabled:checked {
    border: none;
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
            stop:0 rgb(255, 255, 255),
            stop:0.5 rgb(255, 255, 255),
            stop:0.6 rgba(0, 0, 0, 0.2169),
            stop:1 rgba(0, 0, 0, 0.2169));
}

TransparentToolButton,
TransparentToggleToolButton,
TransparentDropDownToolButton,
TransparentPushButton,
TransparentDropDownPushButton,
TransparentTogglePushButton {
    background-color: transparent;
    border: none;
    border-radius: 5px;
    margin: 0;
}

TransparentToolButton:hover,
TransparentToggleToolButton:hover,
TransparentDropDownToolButton:hover,
TransparentPushButton:hover,
TransparentDropDownPushButton:hover,
TransparentTogglePushButton:hover {
    background-color: rgba(200, 0, 0, 9);
    border: none;
}

TransparentToolButton:pressed,
TransparentToggleToolButton:pressed,
TransparentDropDownToolButton:pressed,
TransparentPushButton:pressed,
TransparentDropDownPushButton:pressed,
TransparentTogglePushButton:pressed {
    background-color: rgba(200, 0, 0, 6);
    border: none;
}

TransparentToolButton:disabled,
TransparentToggleToolButton:disabled,
TransparentDropDownToolButton:disabled,
TransprentPushButton:disabled,
TransparentDropDownPushButton:disabled,
TransprentTogglePushButton:disabled {
    background-color: transparent;
    border: none;
}


PillPushButton,
PillPushButton:hover,
PillPushButton:pressed,
PillPushButton:disabled,
PillPushButton:checked,
PillPushButton:checked:hover,
PillPushButton:checked:pressed,
PillPushButton:disabled:checked,
PillToolButton,
PillToolButton:hover,
PillToolButton:pressed,
PillToolButton:disabled,
PillToolButton:checked,
PillToolButton:checked:hover,
PillToolButton:checked:pressed,
PillToolButton:disabled:checked {
    background-color: transparent;
    border: none;
}""")
            self.BodyLabel.setVisible(True)
            self.SubtitleLabel.setText(self.answer)
            self.SubtitleLabel.setVisible(True)

        # 记录答题结果
        if self.currentoption == self.answer:
            self.manager.correct_count += 1
            self.VLS.record.add_ac(time_used)
            self.VLS.handle_correct_review_answer(self.word)
        else:
            self.VLS.record.add_wa(time_used)
            self.VLS.handel_wrong_review_answer(self.word)

        # 切换按钮状态
        self.PrimaryPushButton.setEnabled(True)
        self.PushButton.setEnabled(False)
    def _on_next_clicked(self):
        """ 处理下一题/完成操作 """
        if self.manager.move_next():
            self._load_question()
            self.next_requested.emit()
        else:
            self.finish_requested.emit()
    def addtobook(self):
        if self.n==0:
            self.VLS.add_to_book(self.word)
        if self.n%2==0:
            self.SplitToolButton.setIcon(FluentIcon.HEART.colored(lightColor=QColor('red'), darkColor=QColor('red')))
        else:
            self.SplitToolButton.setIcon(FluentIcon.HEART)
        self.n+=1
    def askdeepseek(self):
        self.parent.parent.switchTo(self.parent.parent.aiInterface)
        self.parent.parent.aiInterface.write_prompt_words(self.parent.start_ui.studylanguage,self.word[self.parent.start_ui.studylanguage])
# 封装结束界面
class EndWidget(QWidget, Ui_End):
    restart_requested = pyqtSignal()  # 重新开始信号

    def __init__(self, VLS,manager: ExamManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent=parent
        self.manager = manager
        self.VLS = VLS
        self._init_ui()


    def _init_ui(self):
        """ 初始化结束界面 """
        # 设置结果展示
        self.LargeTitleLabel.setText("Exam Completed!")
        self.HyperlinkLabel.setText(f"Score: {self.manager.correct_count}/{self.manager.total_questions}")

        # 设置按钮事件
        self.PrimaryPushButton.setText("Restart")
        self.PrimaryPushButton.clicked.connect(self._on_restart_clicked)

        # 显示最终进度
        self.ProgressBar.setVal(100)
        self.ProgressRing.setVal(self.manager.accuracy)


    def update_data(self):
        """ 更新结束页面的数据和显示 """
        # 更新分数显示
        self.HyperlinkLabel.setText(f"{int(self.manager.correct_count/self.manager.total_questions*100)}%")

        # 更新准确率进度环
        accuracy = 100 if self.manager.current_index == 0 else int(
            self.manager.correct_count / self.manager.current_index * 100)
        self.ProgressRing.setVal(accuracy)

        self.HorizontalFlipView.addImages([self.VLS.plot(),self.VLS.show_day_stats()])
        self.HorizontalFlipView.setSpacing(15)
        self.HorizontalFlipView.setBorderRadius(15)
    def _on_restart_clicked(self):
        """ 触发重新开始信号 """
        self.restart_requested.emit()


# 考试系统主容器
class reviewContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化考试管理器和界面
        self.VLS=VocabularyLearningSystem()
        self.manager = ExamManager()
        self._init_ui()
        self.parent=parent
        self._connect_signals()
        self.setObjectName("ExamContainer")

    def _init_ui(self):
        """ 初始化界面布局 """
        self.setLayout(QVBoxLayout())

        # 创建堆叠布局
        self.stack = QStackedLayout()
        self.layout().addLayout(self.stack)

        # 初始化三个界面
        self.start_ui = StartWidget(self.VLS,self)
        self.quiz_ui = QuizWidget(self.VLS,self.manager,self)
        self.end_ui = EndWidget(self.VLS,self.manager,self)

        # 添加界面到堆叠
        self.stack.addWidget(self.start_ui)
        self.stack.addWidget(self.quiz_ui)
        self.stack.addWidget(self.end_ui)

        # 默认显示开始界面
        self.stack.setCurrentIndex(0)

    def _connect_signals(self):
        """ 连接各界面信号 """
        # 开始考试
        self.start_ui.start_requested.connect(
            lambda: self._switch_page(1)
        )
        self.start_ui.start_requested.connect(
            lambda: self.quiz_ui._load_question()
        )

        # 考试完成
        self.quiz_ui.finish_requested.connect(
            lambda: self._switch_page(2)
        )

        # 重新开始
        self.end_ui.restart_requested.connect(self._restart_exam)

    def _switch_page(self, index: int):
        """ 切换界面 """
        self.stack.setCurrentIndex(index)

        # 切换到答题界面时重置题目
        if index == 1:
            self.manager.reset()
            self.quiz_ui._load_question()
        if index == 2:
            self.end_ui.update_data()

    def _restart_exam(self):
        """ 重启考试流程 """
        self.manager.reset()
        self._switch_page(0)