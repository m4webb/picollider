import time

from threading import Thread
from pythonosc import udp_client
from pythonosc import osc_message_builder

class PiSynth(Thread):
    def __init__(self,    
                 manager,
                 duration=2,
                 hold=False,
                 freq0=400,
                 freq1=500,
                 freq2=600, 
                 freq3=700, 
                 freq4=800, 
                 freq5=900, 
                 freq6=1000,
                 freq7=1100, 
                 amp0=0.05, 
                 amp1=0.05, 
                 amp2=0.04, 
                 amp3=0.04, 
                 amp4=0.03, 
                 amp5=0.02,
                 amp6=0.01, 
                 amp7=0.01, 
                 env_level0=0, 
                 env_level1=1, 
                 env_level2=0.9,
                 env_level3=0.5, 
                 env_level4=0, 
                 env_time0=0.2,  
                 env_time1=0.2, 
                 env_time2=0.2,
                 env_time3=0.2, 
                 env_curve0=0, 
                 env_curve1=0, 
                 env_curve2=0, 
                 env_curve3=0,
                 env_releaseNode=3, 
                 env_loopNode=2, 
                 gate=1, 
                 doneAction=2,
                 **kwargs
                 ):
        super().__init__(**kwargs)
        self.manager = manager
        self.duration = duration
        self.hold = hold
        self.arg_dict = {}
        self.arg_dict['freq0'] = freq0
        self.arg_dict['freq1'] = freq1
        self.arg_dict['freq2'] = freq2
        self.arg_dict['freq3'] = freq3
        self.arg_dict['freq4'] = freq4
        self.arg_dict['freq5'] = freq5
        self.arg_dict['freq6'] = freq6
        self.arg_dict['freq7'] = freq7
        self.arg_dict['amp0'] = amp0
        self.arg_dict['amp1'] = amp1
        self.arg_dict['amp2'] = amp2
        self.arg_dict['amp3'] = amp3
        self.arg_dict['amp4'] = amp4
        self.arg_dict['amp5'] = amp5
        self.arg_dict['amp6'] = amp6
        self.arg_dict['amp7'] = amp7
        self.arg_dict['env_level0'] = env_level0
        self.arg_dict['env_level1'] = env_level1
        self.arg_dict['env_level2'] = env_level2
        self.arg_dict['env_level3'] = env_level3
        self.arg_dict['env_level4'] = env_level4
        self.arg_dict['env_time0'] = env_time0
        self.arg_dict['env_time1'] = env_time1
        self.arg_dict['env_time2'] = env_time2
        self.arg_dict['env_time3'] = env_time3
        self.arg_dict['env_curve0'] = env_curve0
        self.arg_dict['env_curve1'] = env_curve1
        self.arg_dict['env_curve2'] = env_curve2
        self.arg_dict['env_curve3'] = env_curve3
        self.arg_dict['env_releaseNode'] = env_releaseNode
        self.arg_dict['env_loopNode'] = env_loopNode
        self.arg_dict['gate'] = gate
        self.arg_dict['pan'] = self.manager.pan
        self.arg_dict['doneAction'] = doneAction

    def run(self):
        nid = self.manager.borrow_nid()
        msg = osc_message_builder.OscMessageBuilder(address = '/s_new')
        msg.add_arg('pisynth1')
        msg.add_arg(nid)
        msg.add_arg(1)
        msg.add_arg(0)
        for key in self.arg_dict:
            msg.add_arg(key)
            msg.add_arg(self.arg_dict[key])
        msg_build = msg.build()
        self.manager.client.send(msg_build)
        time.sleep(self.duration)
        while self.hold:
            time.sleep(self.duration)
        msg = osc_message_builder.OscMessageBuilder(address = '/n_set')
        msg.add_arg(nid)
        msg.add_arg('gate')
        msg.add_arg(0)
        msg_build = msg.build()
        self.manager.client.send(msg_build)
        time.sleep(self.arg_dict['env_time0'] + self.arg_dict['env_time1'] +
                self.arg_dict['env_time2'] + self.arg_dict['env_time3'])
        self.manager.return_nid(nid)

def play_sine(client, freq=440, amp=0.5, duration=0.3):
    args = {}
    args['freq0'] = freq
    args['amp0'] = amp
    for i in range(1,8):
        args['amp{}'.format(i)] = 0
    args['duration'] = duration
    args['env_level0'] = 0 
    args['env_level1'] = 1 
    args['env_level2'] = 0.4
    args['env_level3'] = 0
    args['env_level4'] = 0 
    args['env_time0'] = 0.01  
    args['env_time1'] = 0.03
    args['env_time2'] = 0.5
    args['env_time3'] = 0
    args['env_releaseNode'] = 2
    args['env_loopNode'] = 1
    synth = PiSynth(client, **args)
    synth.start()
