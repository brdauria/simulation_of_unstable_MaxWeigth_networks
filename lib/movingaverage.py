from numpy import *


class MovingAverage:

    def __init__(self, lag):
        self.data = zeros(lag)
        self.index = 0
        self.lag = lag
        self.average = 0

    def push(self, n):
        self.average += (n - self.data[self.index]) / self.lag
        self.data[self.index] = n

        self.index += 1
        if self.index == self.lag:
            self.index = 0

        return self.average

    def get(self):
        return self.average
