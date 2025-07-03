from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import CardWidget, IconWidget, BodyLabel, CaptionLabel, PushButton, TransparentToolButton, \
    FluentIcon


class AppCard(CardWidget):
    def __init__(self, icon, title, content, parent=None):
        super().__init__(parent)

        # 创建子组件
        self.iconWidget = IconWidget(icon)  # 图标组件
        self.titleLabel = BodyLabel(title, self)  # 标题标签（较大字体）
        self.contentLabel = CaptionLabel(content, self)  # 内容标签（较小字体）
        self.openButton = PushButton('前往', self)  # 主操作按钮

        # 创建布局管理器
        self.hBoxLayout = QHBoxLayout(self)  # 主水平布局（控制整体结构）
        self.vBoxLayout = QVBoxLayout()  # 垂直布局（用于文字区域）

        # === 样式设置 ===
        self.setFixedHeight(73)  # 固定卡片高度
        self.iconWidget.setFixedSize(48, 48)  # 固定图标尺寸
        self.contentLabel.setTextColor("#606060", "#d2d2d2")  # 设置内容文本颜色（亮/暗模式）
        self.openButton.setFixedWidth(80)  # 固定按钮宽度

        # === 布局参数 ===
        # 主布局：设置内边距和间距
        self.hBoxLayout.setContentsMargins(11, 11, 11, 11)  # 左,上,右,下 内边距
        self.hBoxLayout.setSpacing(15)  # 组件间距

        # 文字区域布局：无内边距
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)  # 文字间无额外间距

        # === 组件布局 ===
        # 添加图标到主布局
        self.hBoxLayout.addWidget(self.iconWidget)

        # 文字区域布局：添加标题和内容标签
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)  # 垂直居中对齐
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)  # 整个文字区域垂直居中
        self.hBoxLayout.addLayout(self.vBoxLayout)  # 将文字区域加入主布局

        # 添加弹性空间将右侧按钮推到最右边
        self.hBoxLayout.addStretch(1)

        # 添加按钮到主布局右侧
        self.hBoxLayout.addWidget(self.openButton, 0, Qt.AlignRight)
