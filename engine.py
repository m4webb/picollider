from threading import Thread

class Engine(Thread):
    def __init__(self, manager):
        super().__init__()
        self.daemon = True
        self.manager = manager
        self.name = None
        self.parameters = []
        self.running = False

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__) + \
                "\n".join(["{:20} {}".format(attr, repr(getattr(self, attr)))
                for attr in self.parameters])

    def run(self):
        self.running = True
        while self.running:
            self.crank()

    def stop(self):
        self.running = False

    def crank(self):
        raise NotImplementedError

    def perturb(self):
        raise NotImplementedError
