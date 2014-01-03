from __future__ import absolute_import, division, print_function, unicode_literals

from echomesh.color import GammaTable
from echomesh.util.thread import Lock

# See http://dev.moorescloud.com/2012/10/18/about-lpd8806-based-rgb-led-strips/
#
# Inspired by:
# https://github.com/adammhaile/RPi-LPD8806/blob/master/LPD8806.py#L90

class LEDBank(object):
  RGB_ORDER = lambda r, g, b: (r, g, b)
  GRB_ORDER = lambda r, g, b: (g, r, b)
  BRG_ORDER = lambda r, g, b: (b, r, g)

  LATCH_BYTES = 2

  def __init__(self, count,
               device='/dev/spidev0.0',
               gamma_correction=GammaTable.correct,
               channel_order=None,
               offset=0x80):
    self.count = count
    self.device = open(device, 'wb')
    self.gamma_correction = gamma_correction
    self.channel_order = channel_order or LEDBank.RGB_ORDER
    self.offset = offset

    self.brightness = 1.0
    self.control_data = bytearray(3 * count + LEDBank.LATCH_BYTES)
    self.control_data_dirty = False

    self.led = [[0.0] * 3] * count

    self.led_dirty = True
    self.lock = Lock.Lock()
    self.reserved = set()
    self.reserved_uniquely = set()

  def set_brightness(self, brightness):
    with self.lock:
      self.brightness = brightness
      self.led_dirty = True

  def update(self):
    with self.lock:
      if self.led_dirty:
        for i in range(self.count):
          self._set_control_data(i)
        self.control_data_dirty = True
        self.led_dirty = False

      if self.control_data_dirty:
        self.device.write(self.control_data)
        self.control_data_dirty = False

  def set_led(self, i, rgb):
    with self.lock:
      self.led[3 * i:3 * (i + 1)] = rgb
      self._set_control_data(i)
      self.control_data_dirty = True

  def _set_control_data(self, i):
    b, e = 3 * i, 3 * (i + 1)
    rgb = (self.offset + self.gamma_correction(self.led[i] * self.brightness)
           for i in range(b, e))
    self.control_data[b:e] = self.channel_order(*rgb)

