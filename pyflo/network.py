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

    def __init__(self, graph):
        # In the graph we talk about nodes and edges.
        # The corresponding names are processes and connections.
        self.processes = {}
        self.connections = set()
        self.initializers = set()
        self.graph = graph

        self.scheduler = scheduler.Scheduler()

        for node in self.graph.nodes.values():
            self.add_node(node)

        for ports in self.graph.edges.values():
            for edge in ports.values():
                self.add_edge(edge)

        for port in self.graph.initializers.values():
            for initializer in port.values():
                self.add_initializer(initializer)

    def add_node(self, node):
        name = node['name']
        component = node['component']

        if name not in self.processes:
            self.processes[name] = component()

    def get_node(self, name):
        return self.processes[name]

    def add_edge(self, edge):
        out_node_name = edge['from']['node']
        out_node = self.get_node(out_node_name)
        out_port_name = edge['from']['port']
        out_port = out_node.out_ports[out_port_name] 

        in_node_name = edge['to']['node']
        in_node = self.get_node(in_node_name)
        in_port_name = edge['to']['port']
        in_port = in_node.in_ports[in_port_name]

        out_port.attach(in_port)

        self.connections.add((out_port, in_port))

    def add_initializer(self, initializer):
        data = initializer['from']['data']
        node_name = initializer['to']['node']
        node = self.get_node(node_name)
        port_name = initializer['to']['port']
        port = node.in_ports[port_name]

        self.initializers.add((port, data))

    #def remove_node(self, node):

        ''''port = Port('out')
        d1 = Display()
        d2 = Display()

        port.attach(d1.in_ports['in'])
        d1.out_ports['out'].attach(d2.in_ports['in'])

        self.scheduler = scheduler.Scheduler()
        self.scheduler.new(init_data(port, 'hello'))'''

    def run(self):
        for port, data in self.initializers:
            self.scheduler.new(init_data(port, data))
        self.scheduler.mainloop()

def init_data(port, data):
    yield from port.send(data)

def send_data(node, port, data):
    yield from node.out_ports[port].send(data)
