
from leonardo import leonardo
from constance import config
from leonardo_channels.managers import users
from leonardo_channels.senders import sender as channel_sender

SKIP_MODELS = ['Session', 'WidgetDimension']

IS_WS_ENABLED = leonardo.config.get_attr("is_websocket_enabled", None)


def update_widget_reciever(sender, instance, created, **kwargs):
    """check changes and update view on the clients

    basicaly send request on widget update after update
    and on widget create send request for render region

    for other models build NestedObjects and for widgets
    update view
    """

    # this works only with websocket
    if IS_WS_ENABLED and config.LEONARDO_CHANNELS_STREAMING_UPDATE:

        # check if anybody listen to update
        if users.count() == 0:
            return

        needs_update = False

        # instance wan't update related models
        if hasattr(instance, "update_view") and not instance.update_view:
            return
        else:
            needs_update = True

        if created or kwargs.get("update_fields", {}) or needs_update:

            if hasattr(instance, "fe_identifier"):

                msg = {
                    "widget": instance,
                    "created": created,
                    "sender": sender,
                    "path": "/widgets/update"}

                channel_sender.send("http.request", msg)

            else:

                # TODO: use loaded classes
                if instance.__class__.__name__ in SKIP_MODELS:
                    return

                # now we want collect all related widgets
                # for this model and rerender them
                # this is time expensive operation

                msg = {
                    "sender": instance.__class__,
                    "instance": instance,
                    "created": created,
                    "path": "/signals/recieve"
                }

                channel_sender.send("http.request", msg)


def update_widget_post_delete(sender, instance, **kwargs):
    """update region after widget was deleted

    """

    if IS_WS_ENABLED and config.LEONARDO_CHANNELS_STREAMING_UPDATE:

        # instance wan't update related models
        if hasattr(instance, "update_view") and not instance.update_view:
            return

        if hasattr(instance, "fe_identifier"):

            msg = {
                # instance is not thread safety
                "widget": instance,
                "deleted": True,
                "sender": sender,
                "path": "/widgets/update"}

            channel_sender.send("http.request", msg)
