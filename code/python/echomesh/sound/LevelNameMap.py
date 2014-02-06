from __future__ import absolute_import, division, print_function, unicode_literals

import six

# Not used - what is this?

class LevelNameMap(object):
  def __init__(self, **kwds):
    self.levels, self.names = zip(*sorted((v, k)
                                          for k, v in six.iteritems(kwds)))

  def name(self, level):
    for i, lev in enumerate(self.levels):
      if level < lev:
        return self.names[i]
    return self.names[-1]

