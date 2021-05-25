import os, pickle
from enum import IntEnum
from collections import namedtuple


class RecorderState(IntEnum):
    init = 1
    start = 2
    run = 3
    pause = 4
    stop = 5


class ActType(IntEnum):
    Press = 1
    Release = 2
    SingleClick = 3
    DoubleClick = 4


class Record(namedtuple('Record', ['actions', 'period', 'repeat'])):
    __slots__ = ()

    def copy(self):
        return Record(*self)
        
    def save(self, file):
        path, _ = os.path.split(file)
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(file):
            with open(file, "xb") as f:
                pickle.dump(self, f)
        else:
            with open(file, "wb") as f:
                pickle.dump(self, f)


class Action(namedtuple('Action', ['x', 'y', 'button', 'type', 'delay', 'repeat'])):
    __slots__ = ()
    def __str__(self):
        return '{}(x={}, y={}, button={}, delay={}, repeat={})'.format( \
                self.type.name, *self[:2], self.button, *self[4:])