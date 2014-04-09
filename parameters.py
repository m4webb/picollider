import random

class Parameter(object):
    def __init__(self, name):
        self.name = name
    def respond_to_message(self, message):
        raise NotImplementedError
    def prepare_message(self, message):
        raise NotImplementedError
    def initialize_from_message(self, message):
        raise NotImplementedError
    def get(self):
        raise NotImplementedError

class SingleObjectParameter(Parameter):
    def __init__(self, name, obj):
        super().__init__(name)
        self.obj = obj 
    def prepare_message(self, message):
        message.contents[self.name] = self.obj
    def initialize_from_message(self, message):
        if self.name in message.contents:
            self.obj = message.contents[self.name]
    def get(self):
        return self.obj
    def set(self, obj):
        self.obj = obj
    def __repr__(self):
        return "<{} '{}' {}>".format(self.__class__.__name__, self.name, 
                                   self.obj)
    def __str__(self):
        return str(self.obj)

class SetParameter(SingleObjectParameter):
    def respond_to_message(self, message):
        if self.name in message.contents:
            probability = message.confidence
            for item in message.contents[self.name] - self.obj:
                if random.random() < probability:
                    self.obj.add(item)
            for item in self.obj - message.contents[self.name]:
                if random.random() < probability:
                    self.obj.remove(item)
    def initialize_from_message(self, message):
        if self.name in message.contents:
            self.obj = message.contents[self.name]

class ListParameter(SingleObjectParameter):
    def __getitem__(self, index):
        return self.obj[index]
    def __setitem__(self, index, val):
        self.obj[index] = val
    def __len__(self):
        return len(self.obj)

class ConvexCombinationList(ListParameter):
    def respond_to_message(self, message):
        if self.name in message.contents:
            weight = message.confidence
            for i in range(len(self.obj)):
                self.obj[i] = weight*message.contents[self.name][i] +\
                              (1. - weight)*self.obj[i]

class StickyList(ListParameter):
    def respond_to_message(self, message):
        if self.name in message.contents:
            probability = message.confidence
            for i in range(len(self.obj)):
                if random.random() < probability:
                    self.obj[i] = message.contents[self.name][i]

class ConvexCombinationValue(SingleObjectParameter):
    def respond_to_message(self, message):
        if self.name in message.contents:
            weight = message.confidence
            self.obj = weight*message.contents[self.name] +\
                       (1. - weight)*self.obj

class StickyValue(SingleObjectParameter):
    def respond_to_message(self, message):
        if self.name in message.contents:
            probability = message.confidence
            if random.random() < probability:
                self.obj = message.contents[self.name]

class WalkingParameter(Parameter):
    def __init__(self, name, low, high, viscosity):
        self.name = name
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

    def respond_to_message(self, message):
        if self.name in message.contents:
            weight = message.confidence
            self.set(weight*message.contents[self.name] +\
                     (1. - weight)*self.get())

    def prepare_message(self, message):
        message.contents[self.name] = self.get()

    def initialize_from_message(self, message):
        if self.name in message.contents:
            self.set(message.contents[self.name])

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
