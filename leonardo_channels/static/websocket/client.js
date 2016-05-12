
/* Just an example

TODO: make leonardo client which accepts session key and make subscription to a topic
*/
var ws_scheme = window.location.protocol == 'https:' ? 'wss' : 'ws';

if (window.location.port) {
    var basepath = ws_scheme + "://" + window.location.hostname + ":" + window.location.port;
} else {
    var basepath = ws_scheme + "://" + window.location.hostname
}

socket = new ReconnectingWebSocket(basepath + "/messages?session_key={{ request.session.session_key }}");

/* Bind django-messages */
socket.onmessage = function(e) {
    msg = JSON.parse(e.data)
    horizon.alert(msg.level, msg.message, msg.extra_tags)
}
