
from django.conf import settings


if getattr(settings, 'LEONARDO_CHANNELS_RECIEVERS', False):

    from django.db.models.signals import post_save, post_delete
    from .widgets.reciever import update_widget_reciever, update_widget_post_delete
    post_save.connect(update_widget_reciever,
                      dispatch_uid="update_widgets")

    post_delete.connect(update_widget_post_delete,
                        dispatch_uid="update_widget_post_delete")

    # from leonardo_channels.managers import users
    # users.clear()
