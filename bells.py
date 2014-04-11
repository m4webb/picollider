import random
import time
from threading import Thread

import picollider.pisynth as pisynth
from picollider.engine import Engine
from picollider.parameters import ConvexCombinationValue

class BellsEngine(Engine):
    def __init__(self, manager):
        super().__init__(manager)
        self.name = "Bells"
        self.nominal = ConvexCombinationValue('nominal', 
                random.random()*400 + 400)
        self.dhum = ConvexCombinationValue('dhum', 
                random.random()*40 - 20)
        self.dprime = ConvexCombinationValue('dprime', 
                random.random()*40 - 20)
        self.dtierce = ConvexCombinationValue('dtierce', 
                random.random()*40 - 20)
        self.dquint = ConvexCombinationValue('dquint', 
                random.random()*40 - 20)
        self.decay = ConvexCombinationValue('decay', 
                random.random()*20 + 7)
        self.parameters.extend([
            self.nominal,
            self.dhum,
            self.dprime,
            self.dtierce,
            self.dquint,
            self.decay
            ])

    def crank(self):
        bell = Bell(self.manager, self.nominal.get(), self.dhum.get(),
                self.dprime.get(), self.dtierce.get(), self.dquint.get(),
                self.decay.get())
        bell.start()
        time.sleep(self.decay.get() + random.random()*16 - 8)

    def perturb(self, magnitude):
        if random.random() < magnitude:
            self.nominal.set(random.random()*400 + 400)
        if random.random() < magnitude:
            self.dhum.set(random.random()*40 - 20)
        if random.random() < magnitude:
            self.dprime.set(random.random()*40 - 20)
        if random.random() < magnitude:
            self.dtierce.set(random.random()*40 - 20)
        if random.random() < magnitude:
            self.dquint.set(random.random()*40 - 20)
        if random.random() < magnitude:
            self.decay.set(random.random()*20 + 7)

class Bell(Thread):
    def __init__(self, manager, nominal=680, dhum=16.6, dprime=2.0, dtierce=-10,
                 dquint=40., decay=10):
        super().__init__()
        self.manager = manager
        self.nominal = nominal
        self.dhum = dhum
        self.dprime = dprime
        self.dtierce = dtierce
        self.dquint = dquint
        self.decay = decay

    def run(self):
        fundamental = self.nominal / 8.
        hum = fundamental*2 + self.dhum
        prime = fundamental*4 + self.dprime 
        tierce = fundamental*5 + self.dtierce
        quint = fundamental*6 + self.dquint

        args = {}
        args['freq0'] = hum
        args['amp0'] = 0.4
        args['freq1'] = prime
        args['amp1'] = 0.4
        args['freq2'] = tierce
        args['amp2'] = 0.4
        args['freq3'] = quint
        args['amp3'] = 0.4
        args['freq4'] = self.nominal
        args['amp4'] = 0.4
        for i in range(5,8):
            args['amp{}'.format(i)] = 0

        args['duration'] = 0.5
        args['env_level0'] = 0
        args['env_level1'] = 1
        args['env_level2'] = 0.4
        args['env_level3'] = 0
        args['env_level4'] = 0
        args['env_time0'] = 0.01
        args['env_time1'] = 0.03
        args['env_time2'] = self.decay
        args['env_time3'] = 0
        args['env_curve0'] = 5
        args['env_curve2'] = -5
        args['env_releaseNode'] = 2
        args['env_loopNode'] = 1
        synth = pisynth.PiSynth(self.manager, **args)
        synth.start()
