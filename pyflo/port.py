#!/usr/bin/env python3

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
