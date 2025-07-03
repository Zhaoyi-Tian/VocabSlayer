from PyQt5.QtGui import QColor
from qfluentwidgets import QConfig, OptionsConfigItem, OptionsValidator, qconfig, ColorSettingCard, FluentIcon, \
    ColorSerializer, ConfigItem, Theme, EnumSerializer


class UserConfig(QConfig):
    User = ConfigItem(
        "User", "name", "让三颗心免于哀伤",
        restart=False
    )

    primaryColor = OptionsConfigItem(
        "MainWindow", "primaryColor", QColor("#4080FF"),
        serializer=ColorSerializer(),
        restart=False
    )

    API=ConfigItem(
        "User", "API", "sk-19a9f7d42f7c493e8098666c1b3a9b85",
        restart=True
    )

    total_num=ConfigItem(
        "User","total_num",default=0,restart=False
    )
