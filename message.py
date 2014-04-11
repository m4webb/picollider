class Message(object):
    def __init__(self, confidence, engine_name, contents={}):
        self.confidence = confidence
        self.engine_name = engine_name
        self.contents = contents
