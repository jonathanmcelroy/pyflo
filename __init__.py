#!/usr/bin/env python3
"""
File: __init__.py
Author: Jonathan McElroy
"""

from functools import wraps
import scheduler

class EventEmitter:
    """Event emitter"""

    def __init__(self):
        self.__handlers = {}

    def add_listener(self, event, handler):
        """Adds a handler for event event"""
        if event in self.__handlers:
            self.__handlers[event].add(handler)
        else:
            self.__handlers[event] = set((handler,))

    on = add_listener

    def remove_listener(self, event, handler):
        """Removes a handler from listenin to event event"""
        handlers = self.__handlers.get(event, None)
        if handlers:
            handlers.discard(handler)
        elif handlers != None:
            del self.__handlers[event]

    def remoave_all_listeners(self, event):
        """Removes all listeners associated with an evetn"""
        if event in self.__handlers:
            del self.__handlers[event]

    def emit(self, event, *args, **kwargs):
        """Emits an event for all the listeners to use"""
        handlers = self.__handlers.get(event, tuple())
        for handler in handlers:
            handler(*args, **kwargs)

'''class InternalSocket:
    def __init__(self, out_port, in_port):
        self.conncted = False
        self.ports = (out_port, in_port)

    def connect(self, out_port, in_port):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def isConnected(self):
        return self.connected

    def send(self, data):'''

class Port:

    def __init__(self, port_type, data_type=object):
        """Port for sending packets"""
        self.type = port_type
        if self.type == 'out': self.socket = self._out
        elif self.type == 'in': self.socket = self._in
        else: raise Exception("Unknown port type {}".format(str(port_type)))
        if not isinstance(data_type, type):
            raise Exception("port data_type not a data type")
        self.data_type = data_type
        self.port = None

    def attach(self, *args):
        if len(args) == 1:
            # args = [port]
            self.port = args[0]
        elif len(args) == 2:
            # args = [node, port_name]
            self.port = args[0].in_ports[args[1]]

    def disattach(self):
        self.port = None

    def is_attached(self):
        return bool(self.port)

    def _in(self, data_type=object):
        "Connection for recieving packets"
        data = yield
        if not self.node:
            raise Exception("self.node should have been set in the node's __init__")
        yield self.node._inport(self, data)

    def _out(self, data_type=object):
        "Connection for sending packets"
        data = yield
        if not self.port:
            raise Exception("Port not attached to any other ports")
        if not isinstance(data, data_type):
            raise Exception('wrong data type')
        yield self.port.send(data)

    def send(self, data):
        connection = self.socket(self.data_type)
        connection.send(None)
        yield from connection.send(data)

class Component:
    """Component for flows"""
    in_ports = {}
    out_ports = {}

    def __init__(self):
        """Initializes the component"""
        self._call = {}
        for port_name, port in self.in_ports.items():
            port.node = self
        self._send_ports = set()

    def _inport(self, port, data):
        try:
            yield self._call[port](data)
        except KeyError:
            raise KeyError("You must have @self.on_data(port_name) before a function")
        while self._send_ports:
            port, data = self._send_ports.pop()
            yield scheduler.NewTask(send_data(self, port, data))

    def on_data(self, port):
        def decorator(f):
            @wraps(f)
            def wrapper(data):
                return f(data)
            try:
                self._call[self.in_ports[port]] = wrapper
            except KeyError:
                raise Exception("You must specify an in_port name in the decorator")
            return wrapper  
        return decorator
    
    def send(self, port, data):
        #print('send', port, data)
        self._send_ports.add((port, data))

class Graph:
    """A collection of components and edges"""

    def __init__(self, name):
        self.name = name
        self.nodes = {}
        self.edges = {}
        self.initializers = {}
        self.exports = {}
    
    def add_node(self, name, component):
        'adds a node to the graph with name name.'
        self.nodes[name] = {'name':name,
                            'component':component}
        self.edges[name] = {}

    def remove_node(self, name):
        'removes a node with from the graph.'
        if name in self.nodes:
            del self.nodes[name]
            for edge in self.edges[name].values():
                del self.edges[edge['from']['node']][edge['from']['port']]
                del self.edges[edge['to']['node']][edge['to']['port']]

    def get_node(self, name, default=None):
        "returns the node with name name"
        return self.nodes.get(name, default)
        
    def rename_node(self, name, new_name):
        "renames the node from name to new_name"
        node = self.nodes.get(name)
        if node:
            self.nodes[new_name] = node
            del self.nodes[name]
            self.edges[new_name] = self.edges[name]
            del self.edges[name]
            for edge in self.edges[new_name].values():
                if edge['from']['node'] == name:
                    self.edges[new_name] \
                              [edge['from']['port']] \
                              ['from']['node']       = new_name
                    self.edges[edge['to']['node']] \
                              [edge['to']['port']] \
                              ['from']['node']       = new_name
                else:
                    self.edges[new_name] \
                              [edge['to']['port']] \
                              ['to']['node']         = new_name
                    self.edges[edge['from']['node']] \
                              [edge['from']['port']] \
                              ['to']['node']         = new_name

    def add_edge(self, out_node, out_port, in_node, in_port):
        'adds an edge beween out_node and in_node at ports out_port and in_port'
        edge = {'from': {'node': out_node,
                         'port': out_port},
                'to': {'node': in_node,
                       'port': in_port}}
        self.edges[out_node][out_port] = edge
        self.edges[in_node][in_port] = edge
        
    def remove_edge(self, name, port):
        "deletes the edge at name's port"
        edge = self.edges.get(name, {}).get(port, None)
        if edge:
            del self.edges[edge['from']['node']][edge['from']['port']]
            del self.edges[edge['to']['node']][edge['to']['port']]

    def add_initializer(self, data, name, port):
        """Adds an initial data signal"""
        self.initializers[name, port] = {'from': {'data':data},
                                         'to': {'node':name,
                                                'port':port}}

    def remove_initializer(self, node, port):
        """Removes initial data signal"""
        if (node, port) in self.initializers:
            del self.initializers[node, port]

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

if __name__ == "__main__":
    '''graph = Graph('graph')
    graph.add_node('hello', 'comp')
    graph.add_node('nothin', 'nothin')
    graph.add_edge('nothin', 'out', 'hello', 'in')
    print(graph.nodes)
    print(graph.edges)'''

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

    network = Network()
    network.run()

    #port = Port('out')
    #comp = MyComp()

    #sched.new(port)
    #sched.mainloop()

    #port.send({'ports': [comp.in_ports['in']], 'data':'hello world'})
