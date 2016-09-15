
from channels.routing import route, route_class

from .consumers import ws_add, ws_disconnect, FrontendEditConsumer, SignalConsumer

channel_widget_http = [
    route_class(FrontendEditConsumer, path=r"/widgets/update"),
    route_class(SignalConsumer, path=r"/signals/recieve"),
]

channel_widget_routing = [
    route("websocket.connect", ws_add),
    route("websocket.disconnect", ws_disconnect),
]
