import random

#import blips
#import flits
#import bells

class Parameter(object):
    def __init__(self, low, high, viscosity):
        self.low = float(low)
        self.high = float(high)
        self.viscosity = float(viscosity)
        self.span = self.high - self.low
        self.normedval = 0.5
        self.dx = 0.0

    def __repr__(self):
        return repr(self.get())

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
        if self.dx < -3.0*self.viscosity:
            self.dx = -3.0*self.viscosity
        elif self.dx > 3.0*self.viscosity:
            self.dx = 3.0*self.viscosity
        self.normedval += self.dx
        if self.normedval > 1.0:
            self.normedval = 1.0
            self.dx = -0.5*self.viscosity
        elif self.normedval < 0.0:
            self.normedval = 0.0
            self.dx = 0.5*self.viscosity

    def get_walk(self):
        val = self.get()
        self.walk()
        return val, self.dx

class Brain(object):
    pass
