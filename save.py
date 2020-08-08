import json
import re
import os
import time


class Log:
    @staticmethod
    def slaveLog(tag, value, file=''):
        if file == '':
            file = f'save/slave/{time.strftime("%Y-%m-%d")}.log'
        with open(file, 'a', encoding='utf-8') as f:
            f.write(f'{time.strftime("%H-%M-%S")}:{tag}:{value}\n')

    @staticmethod
    def masterLog(tag, value, file=''):
        if file == '':
            file = f'save/master/{time.strftime("%Y-%m-%d")}.log'
        with open(file, 'a', encoding='utf-8') as f:
            f.write(f'{time.strftime("%H-%M-%S")}:{tag}:{value}\n')
