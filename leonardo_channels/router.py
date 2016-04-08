
import logging

from leonardo import leonardo
from leonardo_channels.routing import include, route

LOG = logging.getLogger(__name__)


class Router(object):

    '''Load the channel routes from Leonardo modules'''

    _routes = []
    loaded = False

    def include(self, *args, **kwargs):
        self._routes.append(include(*args, **kwargs))

    def route(self, *args, **kwargs):
        '''Add a route'''
        self._routes.append(route(*args, **kwargs))

    def get_routes(self, force_reload=False):
        '''returns collected routes
        prevents reloading
        '''

        if not self.loaded or force_reload:

            self.channel_routing = [
                include(r[0], **r[1]) if len(r) > 1 else include(r[0])
                for r in leonardo.config.channel_routing
            ]

            self.loaded = True

        return self.channel_routing

    @property
    def routes(self):
        return self.get_routes()

    def __new__(cls, *args, **kwargs):
        """A singleton implementation of Router. There can be only one.
        """
        if not cls._instance:
            cls._instance = super(Router, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    _instance = None


router = Router()
