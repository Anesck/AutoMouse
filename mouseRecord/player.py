import time, pickle
import pynput.mouse as pm
from threading import Thread

from ._base import Record, Action, ActType


class Player():
    def __init__(self, record_file):
        with open(record_file, "rb") as f:
            self._record = pickle.load(f)
        self._mouse = pm.Controller()
        self._thread = Thread(target=self.play, daemon=True)
        self._stop_flag = False

    @property
    def record(self):
        return self._record

    def setTimeAndRepeat(self, period, repeat, delay_repeat):
        actions = []
        for i, (d, r) in enumerate(delay_repeat):
            actions.append(Action(*self._record.actions[i][:4], d, r))
        self._record = Record(actions, period, repeat)

    def _sleep(self):
        while self.sleep_time != 0 and not self._stop_flag:
            time.sleep(0.17)
            self.sleep_time -= min(0.2, self.sleep_time)

    def play(self):
        repeat = self._record.repeat
        period = self._record.period - self._record.actions[-1].delay
        delays = [b.delay - a.delay for a, b in zip( \
                self._record.actions[:-1], self._record.actions[1:])]
        delays.insert(0, self._record.actions[0].delay)
        while repeat and not self._stop_flag:
            for i, a in enumerate(self._record.actions):
                self.sleep_time = delays[i]
                self._sleep()
                step_repeat = a.repeat
                while step_repeat and not self._stop_flag:
                    if not self._stop_flag:
                        self._mouse.position = (a.x, a.y)
                        self._mouse.move(0, 0)
                        if a.type is ActType.Press:
                            self._mouse.press(a.button)
                        elif a.type is ActType.Release:
                            self._mouse.release(a.button)
                        elif a.type is ActType.SingleClick:
                            self._mouse.click(a.button, 1)
                        elif a.type is ActType.DoubleClick:
                            self._mouse.click(a.button, 2)
                    step_repeat -= 1
            repeat -= 1
            self.sleep_time = period
            self._sleep()
        if not self._stop_flag:
            self._thread = Thread(target=self.play, daemon=True)

    def start(self):
        self._stop_flag = False
        self._thread.start()
        
    def stop(self):
        if self._thread.is_alive():
            self._stop_flag = True
            self._thread.join()
            self._thread = Thread(target=self.play, daemon=True)

    def isRunning(self):
        return self._thread.is_alive()