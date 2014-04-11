import time
import random
from threading import Thread

import picollider.pisynth as pisynth
import picollider.piutils as piutils
import picollider.parameters as parameters
from picollider.message import Message
from picollider.engine import Engine

class BlipperEngineBase(Engine):
    """Constant envelope; wait time, duration, pitch drawn from implementable
    functions."""
    def __init__(self, manager, env_levels = [0, 1, 0.4, 0],
                 env_times = [0.01, 0.03, 0.5], 
                 overtone_amps = [0.1, 0, 0, 0, 0, 0, 0, 0],
                ):
        super().__init__(manager)
        self.env_levels = env_levels
        self.env_times = env_times
        self.overtone_amps = overtone_amps
    def get_wait_time(self):
        raise NotImplementedError
    def get_duration(self):
        raise NotImplementedError
    def get_freq(self):
        raise NotImplementedError
    def crank(self):
        self.play_next_blip()
        time.sleep(self.get_wait_time())
    def play_next_blip(self):
        freq = self.get_freq()
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
        synth = pisynth.PiSynth(self.manager, **args)
        synth.start()

class SimpleBlipperEngine(BlipperEngineBase):
    def __init__(self, manager, wait_times=parameters.SetParameter('wait_times', 
                                                                  {0.1, 0.1, 0.3, 0.5}),
                 durations=parameters.SetParameter('durations', {0.2, 0.4, 0.4, 0.6, 0.9}),
                 freqs=parameters.SetParameter('freqs', {400, 450, 500, 550, 600}),
                 **kwargs):
        super().__init__(manager, **kwargs)
        self.name = 'SimpleBlipper'
        self.wait_times = wait_times
        self.durations = durations
        self.freqs = freqs
        self.wait_times.obj = set((0.5 + random.random()**10*10 for i in range(3)))
        self.durations.obj = set((0.5 + random.random()**10*10 for i in range(3)))
        self.freqs.obj = set((200 + random.random()*1000 for i in range(5)))
        self.parameters = [wait_times, durations, freqs]
    def get_wait_time(self):
        return random.choice(list(self.wait_times.obj))
    def get_duration(self):
        return random.choice(list(self.durations.obj))
    def get_freq(self):
        return random.choice(list(self.freqs.obj))
    def perturb(self, magnitude):
        if random.random() < magnitude:
            old_set = self.wait_times.obj
            for item in old_set.copy():
                if random.random() < magnitude and len(old_set) > 1:
                    old_set.discard(item)
            for i in range(3):
                old_set.add(0.1 + random.random()*3)
            self.wait_times.obj = old_set
        if random.random() < magnitude:
            old_set = self.durations.obj
            for item in old_set.copy():
                if random.random() < magnitude and len(old_set) > 1:
                    old_set.discard(item)
            for i in range(3):
                old_set.add(0.1 + random.random()*3)
            self.durations.obj = old_set
        if random.random() < magnitude:
            old_set = self.freqs.obj
            for item in old_set.copy():
                if random.random() < magnitude and len(old_set) > 1:
                    old_set.discard(item)
            for i in range(3):
                old_set.add(200 + random.random()*1000)
            self.freqs.obj = old_set

class HMMBlipper(BlipperEngineBase):
    def __init__(self, manager, wait_time_A, wait_time_B, wait_time_index,
                 duration_A, duration_B, duration_index, freq_A, freq_B,
                 freq_index, **kwargs):
        super().__init__(manager, **kwargs)
        self.wait_time_A = wait_time_A
        self.wait_time_B = wait_time_B
        self.wait_time_index = wait_time_index
        self.duration_A = duration_A
        self.duration_B = duration_B
        self.duration_index = duration_index
        self.freq_A = freq_A
        self.freq_B = freq_B
        self.freq_index = freq_index
        self.wait_time_state = 0
        self.duration_state = 0
        self.freq_state = 0
    def get_wait_time(self):
        self.wait_time_state = piutils.multinomial_draw(
                               self.wait_time_A[self.wait_time_state])
        wait_time_obs = piutils.multinomial_draw(
                        self.wait_time_B[self.wait_time_state])
        return self.wait_time_index[wait_time_obs]
    def get_duration(self):
        self.duration_state = piutils.multinomial_draw(
                              self.duration_A[self.duration_state])
        duration_obs = piutils.multinomial_draw(
                       self.duration_B[self.duration_state])
        return self.duration_index[duration_obs]
    def get_freq(self):
        self.freq_state = piutils.multinomial_draw(
                          self.freq_A[self.freq_state])
        freq_obs = piutils.multinomial_draw( self.freq_B[self.freq_state])
        return self.freq_index[freq_obs]

hmmb_0_wait_time_A = [
    [0.90, 0.05, 0.05],
    [0.20, 0.80, 0.00],
    [0.20, 0.00, 0.80],
]
hmmb_0_wait_time_B = [
    [0.2, 0.2, 0.2, 0.2, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.1, 0.3, 0.3, 0.3, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.3, 0.3, 0.3],
]
hmmb_0_wait_time_index = [
     0.15, 0.40, 0.30, 0.45, 0.50, 0.10, 0.15, 0.20, 0.95, 1.00, 1.05
]

hmmb_0_duration_A =  [
    [0.90, 0.05, 0.05],
    [0.20, 0.80, 0.00],
    [0.20, 0.00, 0.80],
]
hmmb_0_duration_B = [
    [0.2, 0.2, 0.2, 0.2, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.1, 0.3, 0.3, 0.3, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.3, 0.3, 0.3],
]
hmmb_0_duration_index = [
     0.1, 0.35, 0.4, 0.5, 0.7, 1.5, 2.0, 2.5, 0.15, 0.15, 0.15  
]


hmmb_0_freq_A = [
    [0.90, 0.05, 0.05],
    [0.20, 0.80, 0.00],
    [0.20, 0.00, 0.80],
]
hmmb_0_freq_B = [
    [0.2, 0.2, 0.2, 0.2, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.4, 0.3, 0.3, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4, 0.3, 0.3],
]
hmmb_0_freq_index = [
     400, 450, 500, 550, 600, 200, 250, 300, 800, 850, 900,
]

def canonical_hmmb(manager):
    return HMMBlipper(manager, hmmb_0_wait_time_A, hmmb_0_wait_time_B,
            hmmb_0_wait_time_index, hmmb_0_duration_A, hmmb_0_duration_B,
            hmmb_0_duration_index, hmmb_0_freq_A, hmmb_0_freq_B,
            hmmb_0_freq_index)
