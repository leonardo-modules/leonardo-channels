
from django.apps import AppConfig

from leonardo_channels.router import router  # noqa


default_app_config = 'leonardo_channels.Config'


LEONARDO_APPS = ['leonardo_channels', 'channels']

LEONARDO_CHANNEL_ROUTING = [
    ('leonardo_channels.messages.routing.channel_routing',
     {'path': r"^/messages"})
]


class Config(AppConfig):
    name = 'leonardo_channels'
    verbose_name = "leonardo-channels"
