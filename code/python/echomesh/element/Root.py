from __future__ import absolute_import, division, print_function, unicode_literals

import copy

from echomesh.element import Element

PRINT_FORMAT = '{state:5} {time:9} {classes:12}'

class Root(Element.Element):
    def __init__(self, description, score):
        self.score = score
        self.handlers = {}
        self.original_description = copy.deepcopy(description)
        super(Root, self).__init__(None, description)

    def clone(self):
        return Root(self.original_description, self.score)

    def add_handler(self, handler, *types):
        if not types:
            types = handler.event_type
            if not types:
                raise Exception('Handler needs to have an event_type')
            types = [types]
        for t in (types or []):
            self.handlers.setdefault(t, set()).add(handler)

    def __str__(self):
        if not self.elements:
            return '(empty)'
        classes = ', '.join(e.class_name() for e in self.elements)
        return PRINT_FORMAT.format(classes=classes, **self.info())

    def remove_handler(self, handler, *types):
        for t in (types or [handler['event_type']]):
            self.handlers.get(t, set()).discard(handler)

    def handle(self, event):
        if self.handlers:
            event_type = event.get('event_type')
            if not event_type:
                raise Exception('The event %s had no type' % event)
            handlers = self.handlers.get(event_type) or []
            for handler in handlers:
                handler.handle(event)
