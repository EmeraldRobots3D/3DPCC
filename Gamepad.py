from inputs import get_gamepad
from inputs import devices
from threading import Thread
import time
from enum import Enum, IntEnum
import math

MAX_BUTTONS = 20
MAX_AXIS = 10
MAX_HATS = 5

DEFAULT_DEADZONE = .15 # Worked well for Xbox One Elite Controller

MAX_TRIG_VAL = math.pow(2, 8)
MAX_JOY_VAL = math.pow(2, 15)


class EventType(Enum):
    BUTTON = 0,
    AXIS = 1,
    HAT = 2


class EventPos(Enum):
    UP = 0,
    DOWN = 1,
    LEFT = 2,
    RIGHT = 3,
    AXIS_MOVE = 4


class Button(IntEnum):
    A = 0
    B = 1
    X = 2
    Y = 3
    TL = 4
    TR = 5
    start = 6
    select = 7
    thumbL = 8
    thumbR = 9



