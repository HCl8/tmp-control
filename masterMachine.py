from machine import Machine
from utils import Speed
from save import Log
from slaveMachine import SlaveMachine
import time


class MasterMachine(Machine):
    def __init__(self, id, targetTemp=20, nowTemp=30, mode='cool'):
        super().__init__(id)
        self.slaves = {}
        self.connecting = True
        self.queue = []
        self.mode = mode
        self.alive = True
        Log.masterLog('createMaster', f'{self.id}')

    def __str__(self):
        return f'MasterMachine:{self.id}'

    def createSlave(self,roomid):
        """创建一个Slave，返回Slave
        """
        # slaveIds = self.slaves.keys()
        # i = 1
        # # slaveId = str(i - 1 + 1)
        # slaveId = chr(i - 1 + ord('A'))
        # while slaveId in slaveIds:
        #     i += 1
        #     # slaveId = str(i - 1 + 1)
        #     slaveid = chr(i - 1 + ord('A'))
        if roomid in self.slaves:
            return
        slave = SlaveMachine(roomid, self, self.targetTemp, self.nowTemp,
                             self.mode)
        self.slaves[roomid] = slave
        Log.masterLog('createSlave', f'{slave.id}')
        return slave

    def getSlave(self, customerId, slaveId=None):
        """如果slaveId为空 返回匹配的slave或空
            否则 认证正常返回slave 否则空
            都是string
        """
        if slaveId is None:
            for slave in self.slaves.values:
                if slave.customerId == customerId:
                    return slave
            else:
                return None
        slave = self.slaves.get(slaveId)
        if slave:
            if slave.customerId is None:
                slave.setCustomer(customerId)
                return slave
            elif slave.customerId == customerId:
                return slave
        return None

    def delSlave(self, slaveId):
        Log.masterLog('del', f'slaveId')
        self.slaves.pop(slaveId)

    def blowing(self, slave):
        Log.masterLog('blowing', f'{slave.id},{slave.speed.value}')
        slave.blowing()

    def unblowing(self, slave):
        if slave in self.queue:
            Log.masterLog('rmfq', f'{slave.id},{slave.nowTemp},{slave.targetTemp}')
            self.queue.remove(slave)
            slave.isblowing = False

    def responseBlowing(self, slave):
        slave.isblowing = True
        if slave not in self.queue:
            Log.masterLog('aptq', f'{slave.id},{slave.nowTemp},{slave.targetTemp}')
            self.queue.append(slave)
        self.queue.sort(
            key=lambda x: (x.speed.value, x.count / x.speed.needTime()))

    def work(self):
        while True:
            ti = time.time()
            for slave in self.slaves.values():
                if ti - slave.alive > 2:
                    slave.disconnect()
                else:
                    slave.connect()
                slave.need_change()
                if not slave.isblowing:
                    slave.auto()
            if self.working:
                for slave in self.queue[:3]:
                    self.blowing(slave)
            time.sleep(self.fps)

    def setMode(self,mode):
        self.mode = mode
        for slave in self.slaves.values():
            slave.setMode(mode)
            slave.setTargetTemp(25)

    def on(self):
        if not self.working:
            Log.masterLog('on', f'{self.id}')
            self.working = True

    def off(self):
        if self.working:
            Log.masterLog('off', f'{self.id}')
            self.working = False

    def connect(self):
        if not self.connecting:
            Log.masterLog('connect', f'{self.id}')
            self.connecting = True

    def disconnect(self):
        if self.connecting:
            Log.masterLog('disconnect', f'{self.id}')
            self.connecting = False
        for i in self.queue:
            self.unblowing(i)
        Log.masterLog('rmrf', f'{self.id}')
