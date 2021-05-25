import time
import pynput.mouse as pm
import pynput.keyboard as pk

from ._base import *
from ._recognition import toClicks


class Recorder():
    def __init__(self):
        mouse_on_click = lambda x, y, button, pressed: \
                self._mouse_on_click(x, y, button, pressed)
        keyboard_on_release = lambda key: self._keyboard_on_release(key)
        self._mouse_listener = pm.Listener(on_click=mouse_on_click)
        self._keyboard_listener = pk.Listener(on_release=keyboard_on_release)
        self._mouse_listener.setDaemon(True)
        self._keyboard_listener.setDaemon(True)
        self._record_flag = RecorderState.init
        self._actions = []

    @property
    def actions(self):
        return self._actions

    @property
    def record(self):
        return Record(self._actions, self._stop_time - \
                self._start_time, 1) if self.isStopped() else None

    @property
    def clicks_record(self):
        return Record(self.toClicks()[0], self._stop_time - \
                self._start_time, 1) if self.isStopped() else None

    def toClicks(self):
        return toClicks(self._actions)

    def start(self):
        self._keyboard_listener.start()
        self._mouse_listener.start()
        self._start_time = time.time()
        self._record_flag = RecorderState.pause

    def run(self):
        self._record_flag = RecorderState.run

    def pause(self):
        self._record_flag = RecorderState.pause

    def stop(self):
        self._mouse_listener.stop()
        self._keyboard_listener.stop()
        self._stop_time = time.time()
        self._record_flag = RecorderState.stop

    def isStarted(self):
        return self._record_flag is not RecorderState.init

    def isRunning(self):
        return self._record_flag is RecorderState.run

    def isPaused(self):
        return self._record_flag is RecorderState.pause

    def isStopped(self):
        return self._record_flag is RecorderState.stop

    def _mouse_on_click(self, x, y, button, pressed):
        if self.isRunning():
            if pressed:
                self._actions.append(Action(x, y, button, ActType.Press, \
                        round(time.time()-self._start_time, 3), 1))
            else:
                self._actions.append(Action(x, y, button, ActType.Release, \
                        round(time.time()-self._start_time, 3), 1))

    def _keyboard_on_release(self, key):
        if key is pk.Key.space:
            if self.isPaused():
                self._record_flag = RecorderState.run
            elif self.isRunning():
                self._record_flag = RecorderState.pause