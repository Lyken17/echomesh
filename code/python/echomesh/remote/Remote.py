from __future__ import absolute_import, division, print_function, unicode_literals

from echomesh.remote import REGISTRY

from echomesh.util import Log

LOGGER = Log.logger(__name__)

def execute(instance, **data):
    try:
        data_type = data.pop('type')
        function = REGISTRY.function(data_type)
        if not function:
            raise Exception("Didn't understand data type %s" % type)

        return function(instance, data_type=type, **data)

    except Exception:
        LOGGER.error()
