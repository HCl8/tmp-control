from masterMachine import MasterMachine
import threading


class Controller:
    def __init__(self):
        self.master = MasterMachine('master01')
        self.admins = {}

    def checkThread(self):
        t = threading.Thread(target=self.master.work)
        t.start()
        return t
