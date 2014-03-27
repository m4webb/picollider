class Message(object):
    def __init__(self, confidence, mood, contents={}):
        self.confidence = confidence
        self.mood = mood
        self.contents = contents
