#!/usr/bin/env python3

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
