#!/usr/bin/env python3

from port import Port
from component import Component

import scheduler

class Display(Component):
    def __init__(self):
        self.in_ports = {'in': Port('in', str)}
        self.out_ports = {'out': Port('out', str)}

        super().__init__()

        @self.on_data('in')
        def test(data):
            print(data)
            if self.out_ports['out'].is_attached():
                self.send('out', data)

class Network:
    """ The network """

    def __init__(self):
        port = Port('out')
        d1 = Display()
        d2 = Display()

        port.attach(d1.in_ports['in'])
        d1.out_ports['out'].attach(d2.in_ports['in'])

        self.scheduler = scheduler.Scheduler()
        self.scheduler.new(init_data(port, 'hello'))

    def run(self):
        self.scheduler.mainloop()

def init_data(port, data):
    yield from port.send(data)

def send_data(node, port, data):
    yield from node.out_ports[port].send(data)
