
/* Just an example

TODO: make leonardo client which accepts session key and make subscription to a topic
handle protocols reconnetion timeout etc.
*/

/* Subscrive socket messages */
var basepath = "ws://" + window.location.hostname + ":" + window.location.port;

socket = new WebSocket(basepath + "/messages?session_key={{ request.session.session_key }}");

/* Bind django-messages */
socket.onmessage = function(e) {
    msg = JSON.parse(e.data)
    horizon.alert(msg.level, msg.message, msg.extra_tags)
}
socket.onopen = function() {
    //
}