import picollider.message as message

class SilenceMood(object):
    def __init__(self, brain):
        self.brain = brain
        self.mood_name = "Silence"

    def read_message(self, message):
        pass

    def create_message(self):
        message = message.Message(self.brain.personality_confidence, self.mood_name)
        return message

    def enter(self, message=None):
        pass

    def leave(self):
        pass

    def perturb(self, magnitude):
        pass
