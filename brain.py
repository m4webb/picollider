import pickle
import random
import socket
import socketserver
import threading
import time

from pythonosc.udp_client import UDPClient
from pythonosc.osc_message_builder import OscMessageBuilder

import picollider.bells as bells
import picollider.blips as blips
import picollider.flits as flits
import picollider.manager as manager
import picollider.silence as silence 
import picollider.synthdefs as synthdefs


class _MessageHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("Received message")
        message = pickle.loads(self.request[0])
        if message.confidence > self.server.brain.confidence:
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
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self._client = UDPClient(*scsynth_address) 
        self._message_server = _MessageServer(message_address, self)
        self._message_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._recipient_addresses = recipient_addresses
        self._moods = [
                blips.SimpleBlipperMood(self),
                flits.FlitterMood(self),
                silence.SilenceMood(self),
                ]

        self.running = False
        self.parameter_lock = threading.Lock()
        self.manager = manager.SynthManager(self._client,
                nids_start=nids_start, nids_end=nids_end, pan=pan)

        msg = OscMessageBuilder(address='/d_recv') # send synthdefs to scsynth
        msg.add_arg(synthdefs.pisynth1)
        self._client.send(msg.build())
    
    def _send_message(self, message):
        pickled_message = pickle.dumps(message)
        for address in self._recipient_addresses:
            if random.random() < self.influence:
                self._message_client.sendto(pickled_message, address)

    def _new_confidence(self):
        self.confidence = random.random()**2

    def _new_influence(self):
        self.influence = random.random()**2

    def stop(self):
        self.running = False

    def run(self):
        self.confidence = 0.5
        self._new_confidence()
        self.influence = 0.5
        self._new_influence()
        self.manager.start()
        self.current_mood = self._moods.pop(0)
        self.current_mood.enter()
        self._message_server_thread = threading.Thread(
                target=self._message_server.serve_forever)
        self._message_server_thread.daemon = True
        self._message_server_thread.start()
        self.running = True
        while self.running:
            if random.random() < 0.00:
                new_mood = random.choice(self._moods)
                self._moods.remove(new_mood)
                self.current_mood.leave()
                new_mood.enter()
                self._moods.append(self.current_mood)
                self.current_mood = new_mood
                print("New mood!")
            if random.random() < 0.10:
                print("Perturbed")
                self.current_mood.perturb(self.influence)
            if random.random() < 0.05 and random.random() < self.influence:
                print("Sending message")
                self._send_message(self.current_mood.create_message())
            if random.random() < 0.05:
                print("New confidence")
                self._new_confidence()
            if random.random() < 0.05:
                print("New influence")
                self._new_influence()
            time.sleep(1.0)
        self.current_mood.leave()
        self.manager.stop()
