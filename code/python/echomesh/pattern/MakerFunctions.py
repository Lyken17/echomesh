from __future__ import absolute_import, division, print_function, unicode_literals

import itertools
import math
import six

from echomesh.color import ColorSpread
from echomesh.base import Config
from echomesh.pattern.Maker import maker
from echomesh.pattern import PatternDesc

@maker('choose')
def choose(light_sets, choose=None):
  length = len(light_sets)
  def restrict(size):
    return int(max(0, min(length - 1, size)))

  if hasattr(choose, '__call__'):
    # TODO: there's no way to specify callables to choose.
    zipped = itertools.izip_longest(*light_sets)
    return [vec[restrict(choose(i))] for i, vec in enumerate(zipped)]
  else:
    return light_sets[restrict(choose.evaluate())]

@maker
def concatenate(light_sets):
  return list(itertools.chain(*light_sets))

@maker
def inject(light_sets, mapping, length):
  """
    mapping:
      Maps a light index in the result to the light index in the original
      light_set.  We need a reverse mapping because we need a way to map one
      light in the input to many lights in the output.

  """
  assert len(light_sets) == 1
  light_set = light_sets[0]

  def _map(i):
    x = mapping.get(i)
    return x is not None and light_set[x]

  return [_map(i) for i in range(max(int(length), 0))]

@maker('offset', 'length', 'rollover', 'skip')
def insert(light_sets, target=None, offset=None, length=None, rollover=True,
           skip=None):
  assert len(light_sets) == 1
  light_set = light_sets[0]

  skip = int(skip or 1)
  offset = int((offset and offset.evaluate()) or 0)
  if length is None:
    length = Config.get('light', 'count') if target is None else len(target)

  result = target or ([None] * length)
  for i, light in enumerate(light_set):
    index = offset + i
    if index < 0 or index >= length:
      if rollover:
        index = index % length
      else:
        continue
    result[index] = light

  return result

def _to_list(s):
  if s is None:
    return []
  if isinstance(s, six.string_types):
    return [i.strip() for i in s.split(', ')]
  elif not isinstance(s, (list, tuple)):
    return [s]
  else:
    return s

@maker('steps')
def spread(colors=None, steps=None, transforms=None):
  assert colors

  colors = _to_list(colors)
  transforms = _to_list(transforms)

  if len(colors) == 1:
    colors = [colors[0], colors[0]]

  if steps is None:
    steps = [math.ceil(Config.get('light', 'count') / len(colors))]
  else:
    steps = _to_list(steps.evaluate())

  result = []
  for i in xrange(len(colors) - 1):
    s = steps[i if i < len(steps) else -1]
    t = transforms and transforms[i if i < len(transforms) else -1]
    result.extend(ColorSpread.color_name_spread(begin=colors[i],
                                                end=colors[i + 1],
                                                steps=s,
                                                transform=t))
  return result

# The Python built-in works perfectly.
@maker
def reverse(light_sets):
  assert len(light_sets) == 1
  light_set = light_sets[0]
  return reversed(light_set)

@maker('x', 'y', 'reverse_x', 'reverse_y')
def transpose(light_sets, x=None, y=None, reverse_x=False, reverse_y=False):
  assert len(light_sets) == 1
  light_set = light_sets[0]
  if not (x and y):
    default_x, default_y = Config.get('light', 'visualizer', 'layout')
    x = x or default_x
    y = y or default_y

  result = [None] * len(light_set)
  for i, light in enumerate(light_set):
    my_x = i % x
    my_y = i // x
    if reverse_x:
      my_x = x - my_x - 1
    if reverse_y:
      my_y = y - my_y - 1
    index = my_x * y + my_y
    if index < len(result):
      result[index] = light
  return result

_REGISTRY = PatternDesc.REGISTRY

_REGISTRY.register(choose, 'choose')
_REGISTRY.register(concatenate, 'concatenate')
_REGISTRY.register(inject, 'inject')
_REGISTRY.register(insert, 'insert')
_REGISTRY.register(reverse, 'reverse')
_REGISTRY.register(spread, 'spread')
_REGISTRY.register(transpose, 'transpose')
