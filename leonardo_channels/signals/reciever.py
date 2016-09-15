
from leonardo import leonardo
from copy import deepcopy

from leonardo_channels.utils import send_message

SKIP_MODELS = ['Session', 'WidgetDimension']

IS_WS_ENABLED = leonardo.config.get_attr("is_websocket_enabled", None)


def update_widget_reciever(sender, instance, created=None,
                           update_fields={}, **kwargs):

    """resend signals to the workers
    """

    # this works only with websocket
    if IS_WS_ENABLED:

        # TODO: use loaded classes
        if instance.__class__.__name__ in SKIP_MODELS:
            return

        # just resend signal to the worker

        msg = {
            "sender": sender,
            "instance": deepcopy(instance),
            "created": created,
            "update_fields": {
                'update_fields': kwargs.get('update_fields', None)
            },
            "path": "/signals/recieve"
        }

        send_message("http.request", msg)
