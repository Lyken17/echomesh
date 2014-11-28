from __future__ import absolute_import, division, print_function, unicode_literals

from echomesh.element.Repeat import Repeat
from echomesh.element import Load
from echomesh.util import Log
from echomesh.util.string import RemoveHashtags

from echomesh.util.Twitter import Search

LOGGER = Log.logger(__name__)

DEFAULT_PRELOAD = 1

class Twitter(Repeat):
    def __init__(self, parent, description):
        super(Twitter, self).__init__(
          parent, description, name='Twitter', pause_on_exception=False)
        preload = description.get('preload', DEFAULT_PRELOAD)
        search = description['search']
        if not isinstance(search, list):
            search = [search]

        self.searches = [
            Search(s, self.callback, preload=preload) for s in search]
        self.handler = description.get('handler')
        if self.handler:
            self.handler = Load.load_one_element(self, self.handler)
        self.remove_hashtags = description.get('remove_hashtags', True)

    def loop_target(self, t):
        for s in self.searches:
            s.refresh()

        super(Twitter, self).loop_target(t)

    def callback(self, twitter):
        if self.handler:
            text = twitter['text']
            if self.remove_hashtags:
                twitter['text'] = RemoveHashtags.remove_hashtags(text)
            self.handler.handle(twitter)
