import random
import socket
import socketserver
import pickle
import threading
import time

from pythonosc import udp_client

import picollider.manager as manager
import picollider.blips as blips
import picollider.flits as flits
import picollider.bells as bells

class _MessageHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("Received message")
        message = pickle.loads(self.request[0])
        if message.confidence > self.server.brain.confidence:
            self.server.brain.current_mood.read_message(message)

class MessageServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    def __init__(self, address, brain):
        super().__init__(address, _MessageHandler)
        self.brain = brain

class Brain(object):
    def __init__(self, scsynth_server='127.0.0.1', scsynth_port=50000,
                 message_server='192.168.2.1', 
                 message_recipients=('192.168.2.2', '192.168.2.3'), 
                 message_port=50001):
        self.client = udp_client.UDPClient(scsynth_server, scsynth_port) 
        self.manager = manager.SynthManager(self.client)
        self.message_port = message_port
        self.message_server = MessageServer((message_server, self.message_port),
                                            self)
        self.message_recipients = message_recipients
        self.message_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.parameter_lock = threading.Lock()
        self.moods = [flits.FlitterMood(self)]
    
    def send_message(self, message):
        pickled_message = pickle.dumps(message)
        for recipient in self.message_recipients:
            if random.random() < self.influence:
                self.message_client.sendto(pickled_message, (recipient,
                                           self.message_port))

    def new_confidence(self):
        self.confidence = random.random()**2

    def new_influence(self):
        self.influence = random.random()**2

    def main(self):
        self.confidence = 0.5
        self.new_confidence()
        self.influence = 0.5
        self.new_influence()
        self.manager.start()
        self.current_mood = self.moods[0]
        self.current_mood.enter()
        self.message_server_thread = threading.Thread(target=
                                     self.message_server.serve_forever)
        self.message_server_thread.start()
        while True:
            if random.random() < 0.02:
                print("Perturbed")
                self.current_mood.perturb(self.influence)
            if random.random() < 0.1 and random.random() < self.influence:
                print("Sending message")
                self.send_message(self.current_mood.create_message())
            if random.random() < 0.05:
                print("New confidence")
                self.new_confidence()
            if random.random() < 0.05:
                print("New influence")
                self.new_influence()
            time.sleep(1.0)
