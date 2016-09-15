import logging
from copy import deepcopy

from channels.generic import BaseConsumer

LOG = logging.getLogger(__name__)


class SignalConsumer(BaseConsumer):

    method_mapping = {
        "http.request": "signal_reciever",
    }

    def signal_reciever(self, message, **kwargs):
        """Collect related models to instance and for widgets
        call widget_update

        in message expect:

            singal_name: string
            instance: instance
            created: bool
        """

        sender = message.content['sender']
        instance = message.content['instance']
        update_fields = message.content['update_fields']
