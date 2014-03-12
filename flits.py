import time
import random
from threading import Thread

import pisynth

class Flitter(Thread):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.wait = 0.1
        self.dwait = 0
        self.freq = 333.
        self.dfreq = 0
        self.density = 0.5
        self.ddensity = 0
        self.overtone_amps = [0.1, 0, 0, 0, 0, 0, 0, 0]
        self.overtone_ds = [0, 0, 0, 0, 0, 0, 0, 0]
        self.env_times = [0.01, 0.01, 0.05]
        self.running = False

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

            if random.random() < self.density:
                self.play_next_flit()
            time.sleep(self.wait)

    def stop(self):
        self.running = False

    def play_next_flit(self):
        freq = self.freq + 50 - random.random()*100
        args = {}
        for i in range(8):
            args['freq{}'.format(i)] = freq*(i + 1) + self.overtone_ds[i]
            args['amp{}'.format(i)] = self.overtone_amps[i]
        args['duration'] = 0.01
        args['env_level0'] = 0
        args['env_level1'] = 1
        args['env_level2'] = 0.4
        args['env_level3'] = 0
        args['env_level4'] = 0
        args['env_time0'] = self.env_times[0]
        args['env_time1'] = self.env_times[1]
        args['env_time2'] = self.env_times[2]
        args['env_time3'] = 0
        args['env_releaseNode'] = 2
        args['env_loopNode'] = 1
        synth = pisynth.PiSynth(self.client, **args)
        synth.start()
