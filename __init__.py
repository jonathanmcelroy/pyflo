#!/usr/bin/env python3
"""
File: __init__.py
Author: Jonathan McElroy
"""


from component import Component
from network import Network

def init_data(port, data):
    yield from port.send(data)

def send_data(node, port, data):
    yield from node.out_ports[port].send(data)

if __name__ == "__main__":
    '''graph = Graph('graph')
    graph.add_node('hello', 'comp')
    graph.add_node('nothin', 'nothin')
    graph.add_edge('nothin', 'out', 'hello', 'in')
    print(graph.nodes)
    print(graph.edges)'''

    network = Network()
    network.run()

    #port = Port('out')
    #comp = MyComp()

    #sched.new(port)
    #sched.mainloop()

    #port.send({'ports': [comp.in_ports['in']], 'data':'hello world'})
