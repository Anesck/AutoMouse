from ._base import Action, ActType


def isCoordClose(x1, y1, x2, y2, x_diff_max=5, y_diff_max=5):
    return abs(x1 - x2) <= x_diff_max and abs(y1 - y2) <= y_diff_max


def isSingleClick(a1, a2):
    return a1.type is ActType.Press and \
            a2.type is ActType.Release and \
            isCoordClose(*a1[:2], *a2[:2]) \
            and a1.button is a2.button


def isDoubleClick(a1, a2, a3, a4, threshold):
    return isSingleClick(a1, a2) and \
            isSingleClick(a3, a4) and \
            isCoordClose(*a2[:2], *a3[:2]) and \
            a1.button is a3.button and \
            a3.delay - a2.delay <= threshold


def toSingleClick(press, release):
    return Action(int((press.x + release.x) / 2), \
            int((press.y + release.y) / 2), press.button, \
            ActType.SingleClick, press.delay, 1)


def toDoubleClick(press1, release1, press2, release2):
    return Action(int((release1.x + press2.x) / 2), \
            int((release1.y + press2.y) / 2), release1.button, \
            ActType.DoubleClick, press1.delay, 1)


def toClicks(actions, double_click_time_threshold=0.15):
    clicks = []
    clicks_info = []
    step = 0
    while step < len(actions):
        if step < len(actions) - 3 and isDoubleClick( \
                *actions[step:step+4], double_click_time_threshold):
            clicks.append(toDoubleClick(*actions[step:step+4]))
            clicks_info.append((step, step+1, step+2, step+3))
            step += 4
        elif step < len(actions) - 1 and isSingleClick(*actions[step:step+2]):
            clicks.append(toSingleClick(*actions[step:step+2]))
            clicks_info.append((step, step+1))
            step += 2
        else:
            step += 1
    return clicks, clicks_info