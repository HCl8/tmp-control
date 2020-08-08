from utils import Speed
from save import Log


class Machine:
    def __init__(self, id, targetTemp=20, nowTemp=30, mode='cool'):
        self.id = id
        self.targetTemp = targetTemp
        self.nowTemp = nowTemp
        self.mode = mode
        self.working = False
        self.connecting = True
        self.fps = 1

    def __str__(self):
        return f'Machine{self.id}'

    def on(self):
        self.working = True

    def off(self):
        self.working = False
