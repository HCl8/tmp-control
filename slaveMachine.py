from machine import Machine
from utils import Speed
from save import Log
import time
ENV_TEMP = 26


class SlaveMachine(Machine):
    def __init__(self,
                 id,
                 master,
                 targetTemp=20,
                 nowTemp=25,
                 mode='cool',
                 speed=1):
        super().__init__(id, targetTemp=targetTemp, nowTemp=nowTemp, mode=mode)
        self.master = master
        self.customerId = None
        self.speed = Speed(speed)
        self.isblowing = False
        self.alive = time.time()
        self.count = 0
        Log.slaveLog('create', f'{self.id}')
        self.recode = {}

    def setCustomer(self, customerId):
        self.customerId = customerId
        Log.slaveLog('binding', f'{self.id},{self.customerId}')

    def setTargetTemp(self, temp):
        ENV = 25
        if self.targetTemp != temp:
            if self.mode == 'cool' and temp <= ENV:
                temp = max(18, temp)
            elif self.mode == 'warm' and temp >= ENV:
                temp = min(30, temp)
            else:
                temp = ENV
            Log.slaveLog('setTargetTemp',
                         f'{self.id},{self.targetTemp},{temp}')
            self.targetTemp = temp
        return True
        # self.askBlowing(self)

    def setNowTemp(self, temp):
        if self.nowTemp != temp:
            Log.slaveLog('setNowTemp', f'{self.id},{self.nowTemp},{temp}')
            self.nowTemp = temp
            self.count = 0
            # self.askBlowing(self)

    def setMode(self, mode):
        if self.mode != mode:
            Log.slaveLog('setMode', f'{self.id},{self.mode},{mode}')
            self.mode = mode
            self.cancelBlowing()

    def setSpeed(self, speed):
        if isinstance(speed, int):
            speed = Speed(speed)
        if self.speed != speed:
            Log.slaveLog('setSpeed',
                         f'{self.id},{self.speed.value},{speed.value}')
            self.cancelBlowing()
            self.speed = speed
            self.count = 0

    def askBlowing(self):
        self.master.responseBlowing(self)

    def cancelBlowing(self):
        self.count = 0
        self.isblowing = False
        self.master.unblowing(self)

    def need_change(self):
        if self.working and not self.isblowing and self.connecting:
            # print(self.nowTemp, self.targetTemp)
            # 制冷并且现在温度过高 请求
            if self.mode == 'cool' and self.nowTemp > self.targetTemp:
                self.askBlowing()
            elif self.mode == 'warm' and self.nowTemp < self.targetTemp:
                self.askBlowing()
            else:
                return False
        return True

    def auto(self):
        self.count += 1
        if self.count >= 10:
            self.count == 0
            Log.slaveLog('AUTO', f'{self.id}')
            # 低于室温 升温
            if self.nowTemp < ENV_TEMP:
                self.setNowTemp(self.nowTemp + 1)
            elif self.nowTemp > ENV_TEMP:
                self.setNowTemp(self.nowTemp - 1)

    def blowing(self):
        self.count += 1
        self.recode[self.speed.value] = self.recode.get(self.speed.value,
                                                        0) + 1
        Log.slaveLog('blowing', f'{self.id},{self.speed.value}')
        if self.count >= self.speed.needTime():
            Log.slaveLog('BLOWING', f'{self.id}')
            #
            if self.mode == 'cool':
                self.setNowTemp(self.nowTemp - 1)
            else:
                self.setNowTemp(self.nowTemp + 1)
            self.cancelBlowing()

    def on(self):
        if not self.working:
            Log.slaveLog('on', f'{self.id}')
            self.working = True

    def off(self):
        if self.working:
            Log.slaveLog('off', f'{self.id}')
            self.working = False
        self.cancelBlowing()

    def connect(self):
        if not self.connecting:
            Log.slaveLog('connect', f'{self.id}')
            self.connecting = True

    def disconnect(self):
        if self.connecting:
            Log.slaveLog('disconnect', f'{self.id}')
            self.connecting = False
        self.cancelBlowing()