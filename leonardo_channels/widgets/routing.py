
from channels.routing import route

from .consumers import widget_update, ws_add, ws_disconnect

channel_widget_http = [
    route("http.request", widget_update, path=r"/widgets/update"),
]

channel_widget_routing = [
    route("websocket.connect", ws_add),
    route("websocket.disconnect", ws_disconnect),
]
