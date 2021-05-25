import sys
from collections import namedtuple
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, \
        QHBoxLayout, QStackedWidget, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QSize

from runWidget import RunWidget
from recordWidget import RecordWidget


def QListWidget_qss():
    return  '''
                QListWidget{
                    outline: 0px;
                }

                QListWidget {
                    min-width: 30px;
                    max-width: 50px;
                    color: Black;
                    background: #CCCCCC;
                }

                QListWidget::Item:selected {
                    background: #888888;
                    border-left: 5px solid red;
                }
                HistoryPanel:hover {
                    background: rgb(52, 52, 52);
                }
            '''


class MainCentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        tab_bar = self.getTabBar(('录制', '运行'))
        tab_page = self.getTabPage()
        tab_bar.currentRowChanged.connect(tab_page.setCurrentIndex)
        hbox = QHBoxLayout(spacing=0)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(tab_bar)
        hbox.addWidget(tab_page)
        self.setLayout(hbox)
        
    def getTabBar(self, names):
        tab_bar = QListWidget()
        tab_bar.setStyleSheet(QListWidget_qss())
        tab_bar.setFrameShape(QListWidget.NoFrame)
        tab_bar.setItemAlignment(Qt.AlignCenter)
        tab_bar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for name in names:
            item = QListWidgetItem(name)
            item.setTextAlignment(Qt.AlignCenter)
            item.setSizeHint(QSize(50, 50))
            tab_bar.addItem(item)
        tab_bar.setCurrentRow(0)
        return tab_bar

    def getTabPage(self):
        tab_page = QStackedWidget()
        tab_page.addWidget(RecordWidget())
        tab_page.addWidget(RunWidget())
        return tab_page


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(50, 50, 900, 300)
        self.setWindowTitle('AutoMouse')
        self.setCentralWidget(MainCentralWidget())
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())