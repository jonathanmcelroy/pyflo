#!/usr/bin/env python3

class Graph:
    """A collection of components and edges"""

    def __init__(self, name):
        self.name = name
        self.nodes = {}
        self.edges = {}
        self.initializers = {}
    
    def add_node(self, name, component):
        'adds a node to the graph with name name.'
        self.nodes[name] = {'name':name,
                            'component':component}
        self.edges[name] = {}
        self.initializers[name] = {}

    def remove_node(self, name):
        'removes a node with from the graph.'
        if name in self.nodes:
            del self.nodes[name]
            for port in tuple(self.edges[name].keys()):
                self.remove_edge(name, port)
            for port in tuple(self.initializers[name].keys()):
                self.remove_initializer(name, port)
            

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
        if out_node not in self.nodes:
            raise Exception("Creating connction to node {} that doesn't exist".format(out_node))
        if in_node not in self.nodes:
            raise Exception("Creating connction to node {} that doesn't exist".format(in_node))
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

    def add_initial(self, data, node, port):
        """Adds an initial data signal"""
        self.initializers[node][port] = {'from': {'data':data},
                                         'to': {'node':node,
                                                'port':port}}

    def remove_initial(self, node, port):
        """Removes initial data signal"""
        if node in self.initializers and port in self.initializers[node]:
            del self.initializers[node][port]
