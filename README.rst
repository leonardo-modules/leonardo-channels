
==========================
Leonardo leonardo-channels
==========================

Channels for Leonardo CMS. As an example this module has implemented django-messages.

.. contents::
    :local:

Installation
------------

.. code-block:: bash

    pip install leonardo-channels

Integrate
---------

.. code-block:: javascript

    var basepath = "ws://" + window.location.hostname + ":" + window.location.port;

    socket = new WebSocket(basepath + "/messages?session_key={{ request.session.session_key }}");

    /* Bind django-messages */
    socket.onmessage = function(e) {
        msg = JSON.parse(e.data)
        horizon.alert(msg.level, msg.message, msg.extra_tags)
    }

Use from python

.. code-block:: python

    from leonardo_channels import router
    router.route("websocket.connect", ws_add)
    router.include("websocket.myroutes", path=r"/chat")

Use channels for messages

.. code-block:: python

    from leonardo_channels.messages import add_message
    add_message(user, level, message)


Read More
=========

* https://github.com/django-leonardo/django-leonardo
