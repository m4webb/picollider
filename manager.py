import time
import threading

from pythonosc import osc_server, dispatcher, osc_message_builder

class SynthManager(threading.Thread):
    def __init__(self, client, address='localhost', fauxport=60000, wait=5.,
                 nids_start=10000, nids_end=40000):
        super().__init__()
        self.client = client
        d = dispatcher.Dispatcher()
        d.map('/n_end', self._node_end)
        d.map('/fail', self._node_fail)
        self._server = osc_server.ThreadingOSCUDPServer((address, fauxport), d)
        del self._server.socket #hack to make server use socket opened by client
        self._server.socket = self.client._sock #hack cont'd
        self._wait = wait
        self._nids = set(range(nids_start, nids_end))
        self._returned_nids = set()
        self._freed_nids = set()
        self._running = False
        self._nid_lock = threading.Lock()

    def _node_end(self, *args):
        with self._nid_lock:
            self._freed_nids.add(args[0])

    def _node_fail(self, *args):
        """Catch nodes that have been freed and missed."""
        print("called _node_fail {}".format(' '.join(args)))
        failed_command = args[0]
        failed_message = args[1].split()
        if failed_command == "/n_set" and failed_message[0] == "Node" and\
           failed_message[2] == "not" and failed_message[3] == "found":
            with self._nid_lock:
                self._freed_nids.discard(int(failed_message[1]))
                self._returned_nids.discard(int(failed_message[1]))

    def _free_nid(self, nid):
        msg = osc_message_builder.OscMessageBuilder(address = '/n_set')
        msg.add_arg(nid)
        msg.add_arg('gate')
        msg.add_arg(0)
        self.client.send(msg.build())

    def run(self):
        server_thread = threading.Thread(target=self._server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        self._running = True
        msg = osc_message_builder.OscMessageBuilder(address = '/notify')
        msg.add_arg(1)
        self.client.send(msg.build())
        while self._running:
            with self._nid_lock:
                returned_and_freed = self._returned_nids.intersection(
                                     self._freed_nids)
                self._nids.update(returned_and_freed)
                self._returned_nids.difference_update(returned_and_freed)
                self._freed_nids.difference_update(returned_and_freed)
                for nid in self._returned_nids:
                    self._free_nid(nid)
                print("self._returned_nids {}".format(self._returned_nids))
            time.sleep(self._wait)
        msg = osc_message_builder.OscMessageBuilder(address = '/notify')
        msg.add_arg(0)
        self.client.send(msg.build())

    def stop(self):
        self._running = False
        
    def borrow_nid(self):
        with self._nid_lock:
            return self._nids.pop()

    def return_nid(self, nid):
        with self._nid_lock:
            self._returned_nids.add(nid)
