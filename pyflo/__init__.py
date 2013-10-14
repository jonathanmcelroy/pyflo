#!/usr/bin/env python3
"""
File: __init__.py
Author: Jonathan McElroy
"""

from graph import Graph
from component import Component
from network import Network
from port import Port


class Display(Component):

    def __init__(self):
        self.in_ports = {'in': Port('in',  str)}
        self.out_ports = {'out': Port('out', str)}

        super().__init__()

        @self.on_data('in')
        def myPrint(data):
            print(data)
            if self.out_ports['out'].is_attached():
                self.send('out', data)


def init_data(port, data):
    yield from port.send(data)


def send_data(node, port, data):
    yield from node.out_ports[port].send(data)


if __name__ == "__main__":
    graph = Graph('graph')

    graph.add_node('d1', Display)
    graph.add_node('d2', Display)

    graph.add_edge('d1', 'out', 'd2', 'in')

    graph.add_initial('hello', 'd1', 'in')

    network = Network(graph)
    network.run()

    #port = Port('out')
    #comp = MyComp()

    #sched.new(port)
    #sched.mainloop()

    #port.send({'ports': [comp.in_ports['in']], 'data':'hello world'})
