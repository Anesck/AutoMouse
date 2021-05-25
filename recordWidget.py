from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
        QTextEdit, QLineEdit, QFileDialog, QGridLayout, QMessageBox
from PyQt5.QtGui import QTextCursor

from mouseRecord import Recorder
from time import ctime


class RecordWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.record_path = './record/mouse_record.pkl'
        self.recorder = Recorder()
        self.layout = QGridLayout(self)
        self.setClickInfo()
        self.setButtons()
        self.setSaveInfo()

    def setClickInfo(self):
        self.click_info = QTextEdit()
        self.click_info.setReadOnly(True)
        self.click_info.setPlaceholderText(  \
                '1. 点击 <开始录制> 后，再点其他任意处，' \
                + '即可通过 <空格(Space)> 来控制 <继续/暂停> 录制，全局有效；\r\n' \
                + '2. 必须先点击 <结束录制>，再关闭窗口，否则会留有后台程序。\r\n')
        self.layout.addWidget(self.click_info, 1, 1, 5, 9)

    def _setButtons(self, text, clicked_func, pos):
        btn = QPushButton(text)
        btn.clicked.connect(clicked_func)
        self.layout.addWidget(btn, *pos)
        return btn

    def setButtons(self):
        self._setButtons('选择路径', \
                self.savePathButtonClicked, (6, 1))
        self._setButtons('保存 Actions', \
                lambda: self._saveButtonClicked( \
                    self.recorder.record), (6, 6))
        self._setButtons('保存 Clicks', \
                lambda: self._saveButtonClicked( \
                    self.recorder.clicks_record), (6, 7))
        self.record_btn = self._setButtons('开始录制', \
                self.recordButtonClicked, (6, 8))
        self._setButtons('结束录制', \
                self.recordOverButtonClicked, (6, 9))

    def setSaveInfo(self):
        self.save_info = QLineEdit()
        self.save_info.setPlaceholderText('默认保存为：' + self.record_path)
        self.layout.addWidget(self.save_info, 6, 2, 1, 4)

    def recordButtonClicked(self):
        if self.record_btn.text() == '开始录制':
            self.record_btn.setText('重新录制')
        else:
            self.click_info.clear()
            self.recorder.stop()
            self.recorder = Recorder()

        if not self.recorder.isStarted():
            self.recorder.start()
            self.click_info.append('录制开始时间：{}\rActions 记录：'\
                    .format(ctime(self.recorder._start_time)))
            self.__recordLoop()

    def recordOverButtonClicked(self):
        if self.recorder.isStarted() and not self.recorder.isStopped():
            self.recorder.stop()
            self.click_info.append('录制结束时间: {}\r'.\
                    format(ctime(self.recorder._stop_time)))
            self.click_info.append('对应的 Clicks 记录：')
            self.clicks, subSteps = self.recorder.toClicks()
            for step in range(len(self.clicks)):
                self.click_info.append('step <{}>: {}, subSteps: {}'\
                        .format(step, self.clicks[step], subSteps[step]))

    def savePathButtonClicked(self):
        path, _ = QFileDialog.getOpenFileName()
        if path != '':
            self.record_path = path
            self.save_info.setText(self.record_path)

    def _saveButtonClicked(self, record):
        if self.recorder.isStopped() and record is not None:
            record.save(self.record_path)
            QMessageBox.question(self, '保存成功', \
                    '保存成功', QMessageBox.Ok)
        else:
            QMessageBox.question(self, '保存失败', \
                    '请先完成录制', QMessageBox.Ok)

    def __clearLastLine(self):
        self.click_info.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        cursor = self.click_info.textCursor()
        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()

    def __recordLoop(self):
        step = 0
        pause_info_flag = False
        while not self.recorder.isStopped():
            QApplication.processEvents()
            if self.recorder.isRunning():
                if pause_info_flag:
                    pause_info_flag = False
                    self.__clearLastLine()
                if len(self.recorder.actions) > step:
                    self.click_info.append('step <{}>: {}'.\
                            format(step, self.recorder.actions[step]))
                    step += 1
            elif self.recorder.isPaused() and not pause_info_flag:
                pause_info_flag = True
                self.click_info.append('录制暂停中...（按空格键继续录制）')