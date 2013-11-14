from __future__ import absolute_import, division, print_function, unicode_literals

from echomesh.network import ClientServer
from echomesh.sound import PlayerSetter
from echomesh.util import Log
from echomesh.util.thread.Runnable import Runnable

LOGGER = Log.logger(__name__)

_ENVELOPE_ERROR = "ClientPlayer.%s must either be constant or an envelope."
_INF = float('inf')

class ClientPlayer(Runnable):
  _FIELDS = ['begin', 'end', 'filename', 'passthrough', 'level', 'pan',
             'length', 'loops']

  def __init__(self, element, level=1, pan=0, loops=1, length=_INF, **kwds):
    ClientServer.instance()
    super(ClientPlayer, self).__init__()
    PlayerSetter.evaluated_player(
      self, element, level=level, pan=pan, loops=loops, length=length, **kwds)

    data = dict((f, getattr(self, '_' + f)) for f in ClientPlayer._FIELDS)
    self._write(type='construct', **data)

  def _on_run(self):
    self._write(type='run')

  def _on_begin(self):
    self._write(type='begin')

  def _on_pause(self):
    self._write(type='pause')

  def unload(self):
    self._write(type='unload')

  def _write(self, **data):
    data['hash'] = hash(self)
    ClientServer.instance().write(type='audio', data=data)
