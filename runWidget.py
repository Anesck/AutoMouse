from PyQt5.QtWidgets import QApplication, QWidget, QScrollArea, QLabel, \
        QGridLayout, QPushButton, QMessageBox, QFileDialog, QLineEdit
from PyQt5.QtCore import Qt

from mouseRecord import Player


class ConfigWidget(QWidget):
    def __init__(self, file, record):
        super().__init__()
        grid = QGridLayout()
        grid.addWidget(QLabel('文件名: ' + file.split('/')[-1]), 1, 1)
        grid.addWidget(QLabel('循环周期: '), 1, 2)
        grid.addWidget(self._lineEdit('period', 90, '00:00:00.000', \
                self._timeStr(record.period)), 1, 3)
        grid.addWidget(QLabel('循环次数: '), 1, 4)
        grid.addWidget(self._lineEdit('repeat', 60, '0000000', str(record.repeat)), 1, 5)
        for i, a in enumerate(record.actions):
            line = i + 2
            grid.addWidget(QLabel('step <{}>: '.format(i) + \
                    str(a).split(', delay')[0] + ')'), line, 1)
            grid.addWidget(QLabel('执行前延迟: '), line, 2)
            grid.addWidget(self._lineEdit('delay' + str(i), 90, \
                    '00:00:00.000', self._timeStr(a.delay)), line, 3)
            grid.addWidget(QLabel('重复次数: '), line, 4)
            grid.addWidget(self._lineEdit('repeat' + str(i), 60, \
                    '0000000', str(a.repeat)), line, 5)
        self.setLayout(grid)

    def _lineEdit(self, name, width, mask, text):
        edit = QLineEdit()
        edit.setObjectName(name)
        edit.setMaximumWidth(width)
        edit.setInputMask(mask)
        edit.setText(text)
        return edit

    def _timeStr(self, delay):
        h = int(delay // 3600)
        remain = delay - h * 3600
        m = int(remain // 60)
        remain = remain - m * 60
        s = int(remain)
        ms = int((remain - s) * 1e3)
        return '{:0>2d}:{:0>2d}:{:0>2d}.{:0<3d}'.format(h, m, s, ms)


class RunWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout(self)
        self.setButton()
        self.setConfigArea()

    def _setButton(self, text, width, clicked_func, pos):
        btn = QPushButton(text)
        btn.setMinimumWidth(width)
        btn.clicked.connect(clicked_func)
        self.layout.addWidget(btn, *pos)
        return btn

    def setButton(self):
        self._setButton('打开记录文件', 120, \
                self.openButtonClicked, (6, 2))
        self._setButton('重置已修改选项', 120, \
                lambda: self.config_area.setWidget( \
                    ConfigWidget(self.file, self.record_copy)) \
                    if hasattr(self, 'record_copy') else \
                    QMessageBox.question(self, '重置出错', \
                        '请先打开记录文件', QMessageBox.Ok), (6, 3))
        self._setButton('记录文件另存为', 120, \
                self.saveAsButtonClicked, (6, 4))
        self.run_btn = self._setButton('运行', 120, \
                self.runButtonClicked, (6, 5))
            
    def setConfigArea(self):
        self.config_area = QScrollArea()
        self.config_area.setAlignment(Qt.AlignCenter)
        self.config_area.setWidget(QLabel('请先打开记录文件, 关闭前请先停止运行'))
        self.layout.addWidget(self.config_area, 1, 1, 5, 6)

    def _timeNum(self, time_str):
        return sum(float(a) * b for a, b in \
                zip(time_str.split(':'), [3600, 60, 1]))

    def _updateRecordByConfig(self):
        period = self._timeNum(self.config_area.findChild(QLineEdit, 'period').text())
        repeat = int(self.config_area. findChild(QLineEdit, 'repeat').text())
        delay_repeat = []
        for i in range(len(self.player.record.actions)):
            d = self._timeNum(self.config_area.findChild(QLineEdit, 'delay' + str(i)).text())
            r = int(self.config_area.findChild(QLineEdit, 'repeat' + str(i)).text())
            delay_repeat.append((d, r))
        self.player.setTimeAndRepeat(period, repeat, delay_repeat)

    def runButtonClicked(self):
        if hasattr(self, 'record_copy'):
            if self.run_btn.text() == '运行':
                self.run_btn.setText('停止运行')
                self._updateRecordByConfig()
                self.player.start()
                while self.player.isRunning():
                    QApplication.processEvents()
                if self.run_btn.text() == '停止运行':
                    QMessageBox.question(self, '运行完毕', \
                            '运行完毕', QMessageBox.Ok)
                    self.run_btn.setText('运行')
            else:
                self.player.stop()
                self.run_btn.setText('运行')
        else:
            QMessageBox.question(self, '运行出错', \
                '请先打开记录文件', QMessageBox.Ok)

    def saveAsButtonClicked(self):
        if hasattr(self, 'record_copy'):
            file, _ = QFileDialog.getOpenFileName()
            if file != '':
                self._updateRecordByConfig()
                self.player.record.save(file)
                QMessageBox.question(self, '保存成功', \
                    '保存成功', QMessageBox.Ok)
        else:
            QMessageBox.question(self, '保存出错', \
                '请先打开记录文件', QMessageBox.Ok)

    def openButtonClicked(self):
        self.file, _ = QFileDialog.getOpenFileName()
        if self.file != '':
            self.player = Player(self.file)
            self.record_copy = self.player.record.copy()
            self.config_area.setWidget(ConfigWidget(\
                    self.file, self.player.record))