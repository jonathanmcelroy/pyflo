#!/usr/bin/env python3

from functools import wraps
import scheduler


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


def init_data(port, data):
    yield from port.send(data)


def send_data(node, port, data):
    yield from node.out_ports[port].send(data)
