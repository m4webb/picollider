import random
from threading import Thread

from picollider.message import Message

class Mood(object):
    def __init__(self, brain, engine_factory):
        self.brain = brain
        self.engine_factory = engine_factory
        self.engine_running = False
        self.engine = None

    def read_message(self, message):
        self.brain.parameter_lock.acquire()
        if message.engine_name != self.engine.name:
            return
        for parameter in self.engine.parameters:
            if random.random() < message.confidence:
                parameter.respond_to_message(message)
        self.brain.parameter_lock.release()

    def create_message(self):
        message = Message(self.brain.personality_confidence, self.engine.name)
        for parameter in self.engine.parameters:
            if random.random() < self.brain.personality_assertiveness:
                parameter.prepare_message(message)
        return message

    def enter(self, message=None):
        if self.engine_running:
            return
        self.engine = self.engine_factory(self.brain.manager)
        if message and message.engine_name == self.engine.name:
            for parameter in self.engine.parameters:
                parameter.initialize_message(message)
        self.engine.start()
        self.engine_running = True

    def leave(self):
        if not self.engine_running:
            pass
        self.engine.stop()
        self.engine_running = False
        self.engine = None

    def perturb(self, magnitude):
        raise NotImplementedError
