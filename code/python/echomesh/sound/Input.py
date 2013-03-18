from __future__ import absolute_import, division, print_function, unicode_literals

from echomesh.sound import Sound
from echomesh.util import Log
from echomesh.util import ImportIf

analyse = ImportIf.imp('analyse')
numpy = ImportIf.imp('numpy')
pyaudio = ImportIf.imp('pyaudio')

LOGGER = Log.logger(__name__)

MAX_INPUT_DEVICES = 6
TRY_ALL_DEVICES = False


# TODO: Integrate this with the routines in sound.Sound.

def get_pyaudio_stream(name, index, rates, sample_bytes):
  pyaud = Sound.PYAUDIO()
  FORMAT_NAMES = {1: pyaudio.paInt8, 2: pyaudio.paInt16, 3:
                  pyaudio.paInt24, 4: pyaudio.paInt32}
  fmt = FORMAT_NAMES.get(sample_bytes, 0)
  if not fmt:
    LOGGER.error("Didn't understand sample_bytes = %s.", sample_bytes)
    fmt = FORMAT_NAMES[1]

  def _make_stream(i, rate):
    stream = pyaud.open(format=fmt, channels=1, rate=rate,
                        input_device_index=i, input=True)
    LOGGER.debug('Opened pyaudio stream %s.',
                 pyaud.get_device_info_by_index(i)['name'])
    return stream

  if index < 0:
    if name:
      for i in range(pyaud.get_device_count()):
        if pyaud.get_device_info_by_index(i)['name'].startswith(name):
          index = i
          break
      else:
        LOGGER.error("Didn't find audio input device named %s.", name)
    if index < 0:
      index = pyaud.get_default_input_device_info()['index']

  for rate in rates:
    try:
      return _make_stream(index, rate)
    except IOError as e:
      if 'Invalid sample rate' not in str(e):
        raise
  LOGGER.error("Couldn't open audio device named %s.", name)

def get_mic_level(data, length=-1, dtype=None):
  if dtype is None:
    dtype = numpy.int16

  samps = numpy.fromstring(data, dtype=dtype, count=length)
  return analyse.loudness(samps)
