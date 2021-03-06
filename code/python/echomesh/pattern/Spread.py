from __future__ import absolute_import, division, print_function, unicode_literals

from echomesh.Cechomesh import cechomesh
import six

from echomesh.base import Settings
from echomesh.color.LightCount import light_count
from echomesh.pattern.Pattern import Pattern
from echomesh.util.string.Plural import plural

class Spread(Pattern):
    HELP = 'Display a spread of colors between two or more color endpoints.'

    SETTINGS = {
      'colors': {
        'default': [],
        'help': 'The list of two or more colors to be spread.',
        },
      'model': {
        'constant': True,
        'default': 'rgb',
        'help': 'The color model used for interpolation, either rgb or hsb.',
        },
      'steps': {
        'default': [],
        'help': ('A list containing the number of steps inserted between each '
                 'color in the spread.  If there are not enough steps, the '
                 'last step is repeated as needed.  If steps is empty, the '
                 'steps are computed from the total_steps, and if that\'s '
                 'empty, from the number of colors in the input.'),
        },
      'total_steps': {
        'default': 0,
        'help': ('The total number of steps in the entire spread, or 0 for '
                 'use "all lights."' ),
        },
      'transform': {
        'default': '',
        'help': 'The transform to apply to the spread - see "transforms".',
        },
      }

    PATTERN_COUNT = 0

    def _evaluate(self):
        color_names = self.get_raw('colors')
        colors, error_colors = cechomesh.color_list_with_errors(color_names)
        if error_colors:
            raise Exception('\nCan\'t understand %s: %s.' % (
                plural(len(error_colors), 'color'), ', '.join(error_colors)))

        steps = self.get('steps')
        total_steps = self.get('total_steps')
        max_steps = light_count(Settings.get)

        if not total_steps:
            if steps:
                total_steps = steps
                steps = None
            else:
                total_steps = None
                max_steps = len(colors)

        return cechomesh.color_spread(
          colors,
          self.get('model'),
          max_steps=max_steps,
          steps=steps,
          total_steps=total_steps,
          transform=self.get('transform'))
