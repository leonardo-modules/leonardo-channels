
from channels.routing import route_class

from .consumers import SignalConsumer


channel_routing = [
    route_class(SignalConsumer, path=r"/signals/recieve"),
]
