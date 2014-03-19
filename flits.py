import time
import random
from threading import Thread

import pisynth
import brain

def cc(first, second, weight):
    """Return the convex combination (weight)*first + (1 - weight)*second"""
    return weight*first + (1 - weight)*second

class FlitterMood(object):
    def __init__(self, client, message=None):
        self.client = client
        self.flitter = Flitter(self.client)
        if message and message.mood == 'Flitter':
            for key in message.contents:
                if key == 'freq':
                    self.flitter.freq.set(message.contents[key])
                else:
                    setattr(self.flitter, key, message.contents[key])

    def read_message(self, message):
        if message.mood != 'Flitter':
            return
        weight = message.confidence
        for key in message.contents:
            if key in ('freq',):
                new_val = cc(message.contents[key], self.flitter.freq.get(), weight)
                self.flitter.freq.set(new_val)
            elif key in ('overtone_amps, overtone_ds'):
                list_to_change = getattr(self.flitter, key)
                message_list = message.contents[key]
                for i in range(len(list_to_change)):
                    new_val = cc(message_list[i], list_to_change[i], weight)
                    list_to_change[i] = new_val
            elif key in ('wait', 'density', 'decay'):
                new_val = cc(message.contents[key], getattr(self.flitter, key),
                             weight) 
                setattr(self.flitter, key, new_val)

    def create_message(self, confidence, influence):
        pass

    def enter(self):
        self.flitter.start()

    def leave(self):
        self.flitter.stop()

       
class Flitter(Thread):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.wait = 0.1
        self.freq = brain.WalkingParameter(100, 1000, 0.001) 
        self.density = 0.8
        self.overtone_amps = [0.1, 0, 0, 0, 0, 0, 0, 0]
        self.overtone_ds = [0, 0, 0, 0, 0, 0, 0, 0]
        self.decay = 0.05
        self.running = False

    def __repr__(self):
        return "\n".join(["{:20} {}".format(attr, repr(getattr(self, attr))) for 
            attr in ('wait', 'freq', 'density', 'overtone_amps', 'overtone_ds',
            'decay', 'running')])

    def run(self):
        self.running = True
        while self.running:

            """
            self.dwait += 0.005 - random.random()*0.01
            if self.dwait < -.1:
                self.dwait = 0
            if self.dwait > .1:
                self.dwait = 0
            self.wait += self.dwait
            if self.wait < 0.01:
                self.wait = 0.01
                self.dwait = 0.01
            if self.wait > 0.7:
                self.wait = 0.7
                self.dwait = -0.01
            """

            """
            self.dfreq += 0.5 - random.random()*1
            if self.dfreq < -3:
                self.dfreq = -2
            if self.dfreq > 3:
                self.dfreq = 2
            self.freq += self.dfreq
            if self.freq < 100:
                self.freq = 100
                self.dfreq = 2
            if self.freq > 1000:
                self.freq = 1000
                self.dfreq = -2
            """

            if random.random() < self.density:
                self.play_next_flit()
            time.sleep(self.wait)

    def stop(self):
        self.running = False

    def play_next_flit(self):
        freq = self.freq.get() + 50 - random.random()*100
        self.freq.walk()
        args = {}
        for i in range(8):
            args['freq{}'.format(i)] = freq*(i + 1) + self.overtone_ds[i]
            args['amp{}'.format(i)] = self.overtone_amps[i]
        args['duration'] = 0.05
        args['env_level0'] = 0
        args['env_level1'] = 1
        args['env_level2'] = 0.4
        args['env_level3'] = 0
        args['env_level4'] = 0
        args['env_time0'] = 0.01
        args['env_time1'] = 0.01
        args['env_time2'] = self.decay
        args['env_time3'] = 0
        args['env_releaseNode'] = 2
        args['env_loopNode'] = 1
        synth = pisynth.PiSynth(self.client, **args)
        synth.start()
