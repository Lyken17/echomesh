"""An instance of echomesh, representing one node."""

from __future__ import absolute_import, division, print_function, unicode_literals

import time

from echomesh.base import Config
from echomesh.base import Quit
from echomesh.element import ScoreMaster
from echomesh.graphics import Display
from echomesh.light import LightSingleton
from echomesh.network import PeerSocket
from echomesh.network import Peers
from echomesh.util import CLog
from echomesh.util import Log
from echomesh.util.thread.MasterRunnable import MasterRunnable

LOGGER = Log.logger(__name__)

USE_KEYBOARD_THREAD = False

class Instance(MasterRunnable):
  def __init__(self):
    super(Instance, self).__init__()

    CLog.initialize()
    self.score_master = ScoreMaster.ScoreMaster()
    self.peers = Peers.Peers(self)
    self.socket = PeerSocket.PeerSocket(self, self.peers)

    self.display = Display.display()
    self.keyboard = self.osc = None
    if Config.get('control_program'):
      from echomesh.util.thread import Keyboard
      args = {'new_thread': USE_KEYBOARD_THREAD or self.display}
      is_cechomesh = hasattr(self.display, 'write')
      if is_cechomesh:
        args[reader] = None
        args[writer] = self.display
      self.keyboard = Keyboard.keyboard(self, **args)
      if is_cechomesh:
        # We have to store the callback to avoid it being garbage collected.
        self.keyboard_callback = self.display.queue.put
        self.display.add_read_callback(self.keyboard_callback)

    osc_client = Config.get('osc', 'client', 'enable')
    osc_server = Config.get('osc', 'server', 'enable')
    if osc_client or osc_server:
      from echomesh.sound.Osc import Osc
      self.osc = Osc(osc_client, osc_server)

    self.add_mutual_pause_slave(self.socket, self.keyboard, self.osc)
    self.add_slave(self.score_master)
    self.add_slave(self.display)
    self.set_broadcasting(False)
    self.mic = None
    self.timeout = Config.get('network', 'timeout')

    def do_quit():
      self.pause()
      self.unload()

    Quit.register_atexit(do_quit)

  def _on_pause(self):
    super(Instance, self)._on_pause()
    LightSingleton.stop()

  def broadcasting(self):
    return self._broadcasting

  def set_broadcasting(self, b):
    self._broadcasting = b
    if self.keyboard:
      self.keyboard.alert_mode = b

  def send(self, **data):
    self.socket.send(data)

  def handle(self, event):
    return self.score_master.handle(event)

  def main(self):
    if hasattr(self.display, 'callback'):
      self.display.callback = self.run
      self.display.run()
    else:
      self.run()
    if self.display:
      self.display.loop()
      if self.keyboard.thread:
        self.keyboard.thread.join()
    elif not USE_KEYBOARD_THREAD and self.keyboard:
      self.keyboard.loop()
    else:
      while self.is_running:
        time.sleep(self.timeout)
    time.sleep(self.timeout)
    # Prevents crashes if you start and stop echomesh very fast.

  def start_mic(self):
    if not self.mic:
      from echomesh.sound import Microphone
      def mic_event(level):
        self.send(type='event', event_type='mic', key=level)

      self.mic = Microphone.microphone(mic_event)
      self.mic.run()
      self.add_mutual_pause_slave(self.mic)

  def stop_mic(self):
    if self.mic:
      self.mic.pause()
      self.remove_slave(self.mic)
      self.mic = None


INSTANCE = Instance()
main = INSTANCE.main

