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


