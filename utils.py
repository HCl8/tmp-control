from enum import Enum


class Speed(Enum):

    LOW = 1
    MIDDLE = 2
    HIGH = 3

    @classmethod
    def up(cls, speed):
        if speed is cls.HIGH:
            return speed
        else:
            return cls(speed.value + 1)

    @classmethod
    def down(cls, speed):
        if speed is cls.LOW:
            return speed
        else:
            return cls(speed.value - 1)

    def needTime(self):
        return {1: 25, 2: 20, 3: 15}[self.value]

