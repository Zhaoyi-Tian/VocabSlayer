from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QTableWidgetItem

from data_view import Ui_Form
from server.my_test import VocabularyLearningSystem


class dataWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.VLS=VocabularyLearningSystem()
        self.data=self.VLS.show_data()
        self.data_book=self.VLS.show_book()
        # 启用边框并设置圆角
        self.ui.TableWidget.setBorderVisible(True)
        self.ui.TableWidget.setBorderRadius(8)
        self.ui.TableWidget.setRowCount(len(self.data))
        self.ui.TableWidget.setWordWrap(False)
        self.ui.TableWidget.setColumnCount(4)
        self.ui.TableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        for i, songInfo in enumerate(self.data):
            for j in range(4):
                self.ui.TableWidget.setItem(i, j, QTableWidgetItem(songInfo[j]))

        # 设置水平表头并隐藏垂直表头
        self.ui.TableWidget.setHorizontalHeaderLabels(['Chinese', 'English', 'Japanese', 'Level'])
        self.ui.TableWidget.verticalHeader().hide()

        if self.data_book!="收藏本为空！":
            self.ui.TableWidget_2.setBorderVisible(True)
            self.ui.TableWidget_2.setBorderRadius(8)
            self.ui.TableWidget_2.setRowCount(len(self.data_book))
            self.ui.TableWidget_2.setWordWrap(False)
            self.ui.TableWidget_2.setColumnCount(4)
            self.ui.TableWidget_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            for i1, songInfo in enumerate(self.data_book):
                for j1 in range(4):
                    self.ui.TableWidget_2.setItem(i1, j1, QTableWidgetItem(str(songInfo[j1])))

            # 设置水平表头并隐藏垂直表头
            self.ui.TableWidget_2.setHorizontalHeaderLabels(['Chinese', 'English', 'Japanese', 'Level'])
            self.ui.TableWidget_2.verticalHeader().hide()