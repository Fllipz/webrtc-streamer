var ws;

window.addEventListener('beforeunload', (event) => {
    ws.close();
    // Cancel the event as stated by the standard.
    event.preventDefault();
    // Older browsers supported custom message
    event.returnValue = '';
});

function WebSocketBegin() {
    if ("WebSocket" in window) {
        // Let us open a web socket
        ws = new WebSocket(
            location.hostname.match(/\.husarnetusers\.com$/) ? "wss://" + location.hostname + "/__port_8001/" : "ws://" + location.hostname + ":8001"
        );

        ws.onopen = function () {
            // Web Socket is connected
            console.log("Websocket connected!");
            ws.send('{"check_connection": 1}');
            ws.send('{"get_feed_options": 1}');
        };

        ws.onmessage = function (evt) {
            //create a JSON object
            var jsonObject = JSON.parse(evt.data);
            console.log(jsonObject);
            if(jsonObject.hasOwnProperty("connection")){
                if(jsonObject['connection']==0)
                $('#p2p_connection').removeClass('invisible');
            }else if(jsonObject.hasOwnProperty("options")){
                
            }
        };

        ws.onclose = function (evt) {
            if (evt.wasClean) {
                console.log(`[close] Connection closed cleanly, code=${evt.code} reason=${evt.reason}`);
            } else {
                // e.g. server process killed or network down
                // event.code is usually 1006 in this case
                console.log('[close] Connection died');
            }
        };

        ws.onerror = function (error) {
            alert(`[error] ${error.message}`);
        }

    } else {
        // The browser doesn't support WebSocket
        alert("WebSocket NOT supported by your Browser!");
    }
}