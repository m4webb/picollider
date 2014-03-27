"""
This example demonstrates some of the basic operations of the picollider
system.
"""



"""
Before using this tutorial, make sure that you have access to a running
instance of the SuperCollider server (scsynth).
"""
SCSYNTH_ADDRESS = 'localhost'
SCSYNTH_PORT = 57110



"""
pythonosc is a third part library used to send OSC messages to the
SuperCollider server. OSC (Open Sound Control) is a message format for
communication among computers, etc., that is in some ways an update of MIDI.

For more about OSC, see

    http://opensoundcontrol.org/spec-1_0

For the SuperCollider spec on what messages the server responds to, see

    http://doc.sccode.org/Reference/Server-Command-Reference.html
"""
from pythonosc import udp_client, osc_message_builder

"""
Make a client to the scsynth server, through which we can send OSC messages.
"""
client = udp_client.UDPClient(SCSYNTH_ADDRESS, SCSYNTH_PORT)



"""
This is a helper-module containing the bytecode of compiled synthdefs. A
synthdef is specially formatted bytecode, specific to SuperCollider, that gives
the server a specificiation for a class of synths. These synths may have
parameters that are given upon instance creation. See

    http://doc.sccode.org/Classes/SynthDef.html
    http://doc.sccode.org/Reference/Synth-Definition-File-Format.html

As of now, picollider only uses a single synthdef, pisynth1. This is a
general-purpose synth with many parameters.
"""
import picollider.synthdefs

"""
Send the synthdef to the server.

Using osc_message_builder, a message is initialized with an address and given
parameters. Once ready, it can be built and sent through a client.
"""
msg = osc_message_builder.OscMessageBuilder(address = '/d_recv')
msg.add_arg(picollider.synthdefs.pisynth1)
client.send(msg.build())



"""
Though we will not use this module directly, it contains an important class,
PiSynth. This class is the Python interface to the pisynth1 synthdef previously
loaded. It holds all the parameters, and is able to send messages to the server
to start and stop a synth instance.
"""
import picollider.pisynth



"""
A picollider.manager.SynthManager manages the lifecycle of synth instances. Of
most concern is the management of node IDs, numbers that the server uses to
keep track of synth instances. Each synth instance must have a unique node ID.
The manager maintains a set of available IDs, lends them to PiSynth instances,
and listens to the server to ensure the release of used node IDs.
"""
import picollider.manager
manager = picollider.manager.SynthManager(client)

"""
picollider has a number of different sound engines, many of which are still
being developed. A later tutorial will explore how these work, but here we
instantiate one as an example.
"""
import picollider.flits
flitter = picollider.flits.Flitter(manager)



"""
Start it up!
"""
if __name__ == "__main__":
    manager.start()
    flitter.start()
    input("Press enter to stop ")
    flitter.stop()
    manager.stop()
