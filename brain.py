import random

from pythonosc import udp_client

import blips
import flits
import bells

class Message(object):
    def __init__(self, confidence, mood, contents={}):
        self.confidence = confidence
        self.mood = mood
        self.contents = contents

class Brain(object):
    def __init__(self, server_location='127.0.0.1', server_port=50000):
        self.client = udp_client.UDPClient(server_location, server_port)

    def main(self):
        pass

class WalkingParameter(object):
    def __init__(self, low, high, viscosity):
        self.low = float(low)
        self.high = float(high)
        self.viscosity = float(viscosity)
        self.span = self.high - self.low
        self.normedval = 0.5
        self.dx = 0.0

    def __repr__(self):
        return "<WalkingParameter {}>".format(str(self.get()))

    def __str__(self):
        return str(self.get())

    def __iadd__(self, val):
        domainval = self._normed_to_domain(self.normedval) + val
        self.normedval = self._domain_to_normed(domainval)
        self._check_bounds()
        return self

    def __isub__(self, val):
        domainval = self._normed_to_domain(self.normedval) - val
        self.normedval = self._domain_to_normed(domainval)
        self._check_bounds()
        return self

    def _check_bounds(self):
        self.normedval = min(1, max(0, self.normedval))

    def _normed_to_domain(self, val):
        return self.low + val*self.span

    def _domain_to_normed(self, val):
        return (val - self.low)/self.span

    def get(self):
        return self._normed_to_domain(self.normedval)

    def set(self, val):
        self.normedval = self._domain_to_normed(val)
        self._check_bounds()

    def walk(self):
        self.dx += self.viscosity - random.random()*self.viscosity*2.0
        if self.dx < -5.0*self.viscosity:
            self.dx = -5.0*self.viscosity
        elif self.dx > 5.0*self.viscosity:
            self.dx = 5.0*self.viscosity
        self.normedval += self.dx
        if self.normedval > 1.0:
            self.normedval = 1.0
            self.dx = -1.0*self.viscosity
        elif self.normedval < 0.0:
            self.normedval = 0.0
            self.dx = 1.0*self.viscosity
