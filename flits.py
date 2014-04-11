import time
import random
from threading import Thread

import picollider.pisynth as pisynth
import picollider.parameters as parameters
from picollider.engine import Engine

class FlitterEngine(Engine):
    def __init__(self, manager):
        super().__init__(manager)
        self.name = 'Flitter'
        self.wait = parameters.ConvexCombinationValue('wait', 0.1)
        self.freq = parameters.WalkingParameter('freq', 100, 1000, 0.001) 
        self.density = parameters.ConvexCombinationValue('density', 0.8)
        self.overtone_amps = parameters.StickyList('overtone_amps', 
                             [0.1, 0, 0, 0, 0, 0, 0, 0])
        self.overtone_ds = parameters.ConvexCombinationList('overtone_ds', 
                           [0, 0, 0, 0, 0, 0, 0, 0])
        self.decay = parameters.ConvexCombinationValue('decay', 0.05)
        self.parameters.extend([self.wait, self.freq, self.density,
                self.overtone_amps, self.overtone_ds, self.decay])

    def crank(self):
        if random.random() < self.density.get():
            self.play_next_flit()
        time.sleep(self.wait.get())

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
        args['env_time2'] = self.decay.get()
        args['env_time3'] = 0
        args['env_releaseNode'] = 2
        args['env_loopNode'] = 1
        synth = pisynth.PiSynth(self.manager, **args)
        synth.start()

    def perturb(self, magnitude):
        if random.random() < magnitude:
            self.wait.set(random.choice((0.2, 0.1, 0.08, 0.05)))
        if random.random() < magnitude:
            self.freq.normedval = random.random()
        if random.random() < magnitude:
            self.density.set(random.random())
        for i in range(len(self.overtone_amps)):
            if random.random() < magnitude:
                self.overtone_amps[i] = random.choice((0.1, 0.08, 0.06,
                                                0.04, 0.0, 0.0, 0.0))/(1. + i)
            if random.random() < magnitude:
                if random.random() < 0.5:
                    self.overtone_ds[i] = 50 - 100*random.random()
                else:
                    self.overtone_ds[i] = 0
        if random.random() < magnitude:
            self.decay.set(random.choice((0.15, 0.1, 0.08, 0.05, 0.02)))
