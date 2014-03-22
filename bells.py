from threading import Thread

import picollider.pisynth as pisynth

class Bell(Thread):
    def __init__(self, client, nominal=680, dhum=16.6, dprime=2.0, dtierce=-10,
                 dquint=40., decay=10):
        super().__init__()
        self.client = client
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
        synth = pisynth.PiSynth(self.client, **args)
        synth.start()
