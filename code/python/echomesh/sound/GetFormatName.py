from __future__ import absolute_import, division, print_function, unicode_literals

from echomesh.util import Log

LOGGER = Log.logger(__name__)

def get_format_name(sample_bytes):
  import pyaudio

  FORMAT_NAMES = {
    1: pyaudio.paInt8,
    2: pyaudio.paInt16,
    3: pyaudio.paInt24,
    4: pyaudio.paInt32,
    }

  fmt = FORMAT_NAMES.get(sample_bytes, 0)
  if fmt:
    return fmt
  LOGGER.error("Didn't understand sample_bytes = %s.", sample_bytes)
  return FORMAT_NAMES[1]
