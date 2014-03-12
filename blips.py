import time
import random
from threading import Thread

import pisynth

class BlipperBase(Thread):
    """Constant envelope; wait time, duration, pitch drawn from implementable
    functions."""
    def __init__(self, client, env_levels = [0, 1, 0.4, 0],
                 env_times = [0.01, 0.03, 0.5], 
                 overtone_amps = [0.1, 0, 0, 0, 0, 0, 0, 0],
                ):
        super().__init__()
        self.client = client
        self.env_levels = env_levels
        self.env_times = env_times
        self.overtone_amps = overtone_amps
        self.running = False
    def get_wait_time(self):
        raise NotImplementedError
    def get_duration(self):
        raise NotImplementedError
    def get_fund_freq(self):
        raise NotImplementedError
    def run(self):
        self.running = True
        while self.running:
            self.play_next_blip()
            time.sleep(self.get_wait_time())
    def stop(self):
        self.running = False
    def play_next_blip(self):
        freq = self.get_fund_freq()
        args = {}
        for i in range(8):
            args['freq{}'.format(i)] = freq*(i + 1)
            args['amp{}'.format(i)] = self.overtone_amps[i]
        args['duration'] = self.get_duration()
        args['env_level0'] = self.env_levels[0]
        args['env_level1'] = self.env_levels[1]
        args['env_level2'] = self.env_levels[2]
        args['env_level3'] = self.env_levels[3]
        args['env_level4'] = 0
        args['env_time0'] = self.env_times[0]
        args['env_time1'] = self.env_times[1]
        args['env_time2'] = self.env_times[2]
        args['env_time3'] = 0
        args['env_releaseNode'] = 2
        args['env_loopNode'] = 1
        synth = pisynth.PiSynth(self.client, **args)
        synth.start()

class SimplerBlipper(BlipperBase):
    def __init__(self, client, wait_times=[0.1, 0.1, 0.3, 0.5],
                 durations=[0.2, 0.4, 0.4, 0.6, 0.9],
                 freqs=[400, 450, 500, 550, 600],
                 **kwargs):
        super().__init__(client, **kwargs)
        self.wait_times = wait_times
        self.durations = durations
        self.freqs = freqs
    def get_wait_time(self):
        return random.choice(self.wait_times)
    def get_duration(self):
        return random.choice(self.durations)
    def get_fund_freq(self):
        return random.choice(self.freqs)
