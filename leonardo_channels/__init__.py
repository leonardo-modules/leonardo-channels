
from django.apps import AppConfig


default_app_config = 'leonardo_channels.Config'


LEONARDO_APPS = ['leonardo_channels', 'channels']

LEONARDO_CHANNEL_ROUTING = [
    ('leonardo_channels.messages.routing.channel_routing',
     {'path': r"^/messages"})
]

LEONARDO_JS_FILES = [
    'websocket/reconnecting-websocket.js'
]


class Config(AppConfig):
    name = 'leonardo_channels'
    verbose_name = "leonardo-channels"

try:
    from django.channels import Channel, Group  # NOQA isort:skip
    from django.channels.asgi import channel_layers  # NOQA isort:skip
    from django.channels.routing import route, include  # NOQA isort:skip
except ImportError:
    from channels import Channel, Group
    from channels.asgi import channel_layers  # NOQA isort:skip
    from channels.routing import route, include  # NOQA isort:skip

from leonardo_channels.router import router  # noqa
