import pickle
import random
import socket
import socketserver
import threading
import time

from pythonosc.udp_client import UDPClient
from pythonosc.osc_message_builder import OscMessageBuilder

#import picollider.bells as bells
#import picollider.silence as silence 
import picollider.manager as manager
import picollider.synthdefs as synthdefs
from picollider.mood import Mood
from picollider.blips import SimpleBlipperEngine
from picollider.flits import FlitterEngine


class _MessageHandler(socketserver.BaseRequestHandler):
    def handle(self):
        message = pickle.loads(self.request[0])
        if message.confidence + random.random()**10 > \
                self.server.brain.personality_confidence + \
                (1 - random.random()**10):
            print("Received message")
            self.server.brain.current_mood.read_message(message)


class _MessageServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    def __init__(self, address, brain):
        super().__init__(address, _MessageHandler)
        self.brain = brain


class Brain(threading.Thread):
    def __init__(self, 
                 scsynth_address=('127.0.0.1', 50000),
                 message_address=('192.168.2.1', 50001),
                 recipient_addresses=(
                     ('192.168.2.2', 50001),
                     ('192.168.2.3', 50001), 
                 ),
                 nids_start=10000,
                 nids_end=40000,
                 pan=0,
                 personality_assertiveness=0.10,
                 personality_moodiness=0.02,
                 personality_confidence=0.05,
                 personality_irritability=0.10,
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self._client = UDPClient(*scsynth_address) 
        self._message_server = _MessageServer(message_address, self)
        self._message_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._recipient_addresses = recipient_addresses
        self._moods = [
                Mood(self, SimpleBlipperEngine),
                Mood(self, FlitterEngine),
                #silence.SilenceMood(self),
                ]

        self.running = False
        self.parameter_lock = threading.Lock()
        self.manager = manager.SynthManager(self._client,
                nids_start=nids_start, nids_end=nids_end, pan=pan)

        msg = OscMessageBuilder(address='/d_recv') # send synthdefs to scsynth
        msg.add_arg(synthdefs.pisynth1)
        self._client.send(msg.build())

        self.personality_assertiveness = personality_assertiveness
        self.personality_moodiness = personality_moodiness
        self.personality_confidence = personality_confidence
        self.personality_irritability = personality_irritability
    
    def _send_message(self, message):
        pickled_message = pickle.dumps(message)
        for address in self._recipient_addresses:
            self._message_client.sendto(pickled_message, address)

    def stop(self):
        self.running = False

    def run(self):
        self.manager.start()
        self.current_mood = self._moods.pop(0)
        self.current_mood.enter()
        self._message_server_thread = threading.Thread(
                target=self._message_server.serve_forever)
        self._message_server_thread.daemon = True
        self._message_server_thread.start()
        self.running = True
        while self.running:
            if random.random() < self.personality_moodiness:
                new_mood = random.choice(self._moods)
                self._moods.remove(new_mood)
                self.current_mood.leave()
                new_mood.enter()
                self._moods.append(self.current_mood)
                self.current_mood = new_mood
                print("New mood!")
            if random.random() < self.personality_irritability:
                print("Perturbed")
                self.current_mood.engine.perturb(self.personality_irritability)
            if random.random() < self.personality_assertiveness:
                print("Sending message")
                self._send_message(self.current_mood.create_message())
            time.sleep(1.0)
        self.current_mood.leave()
        self.manager.stop()
