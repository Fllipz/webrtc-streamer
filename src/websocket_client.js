var ws;

feed_options={};

selected_size = '320x240';
selected_fps = '15.000';
protocol = null;

window.addEventListener('beforeunload', (event) => {
    ws.close();
    // Cancel the event as stated by the standard.
    event.preventDefault();
    // Older browsers supported custom message
    event.returnValue = '';
});

function setUpListeners(){
    var $select_s = $('#size_select');
    $select_s.val(selected_size);
    var $select = $('#fps_select');
    fps = feed_options["options"][" "+selected_size];
    $select.find('option').remove();
    for(var fp in fps){
        $select.append('<option value=' + fps[fp] + '>' + fps[fp]+ '</option>');
    }
    $select.val(selected_fps);

    $('#size_select').change(function(evt) {
        var $select = $('#fps_select');
        fps = feed_options["options"][" "+evt.target.value];
        $select.find('option').remove();
        selected_size = evt.target.value;
        selected_fps = null;
        for(var fp in fps){
            $select.append('<option value=' + fps[fp] + '>' + fps[fp]+ '</option>');
        }
        selected_fps=fps[0];
    });
    $('#fps_select').change(function(evt){
        selected_fps = evt.target.value;
    });
    $('#submit_btn').click(function(evt){
        evt.preventDefault();
        if(selected_size==null||selected_fps==null){
            alert("You need to chose desired size and fps to change stream parameters!");
        }else{
            stopStream();
            ws.send(`{"change_feed":{"size": \"${selected_size}\"  ,  "fps": \"${selected_fps}\" , "protocol" : \"${protocol}\" }}`);
        }
    })
}


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
            setInterval(function(){
                ws.send('{"check_connection": 1}');
            },5000)
        };

        ws.onmessage = function (evt) {
            //create a JSON object
            var jsonObject = JSON.parse(evt.data);
            console.log(jsonObject);
            if(jsonObject.hasOwnProperty("connection")){
                $('#p2p_connection').find('span').remove();
                $('#p2p_connection').find('br').remove();
                if(jsonObject['connection']==0){
                    $('#p2p_connection').append('<span>Peer-to-peer error. Forwarding traffic through a Base Server.</span>');
                    $('#p2p_connection').append('<br>')
                    $('#p2p_connection').append('<span> Visit <a href="https://husarnet.com/docs/tutorial-troubleshooting" a>https://husarnet.com/docs/tutorial-troubleshooting</a> to solve your connection issue</span>')
                }else{
                    $('#p2p_connection').append('<span>Peer-to-peer connection established</span>')
                }
                $('#p2p_connection').removeClass('invisible');
            }else if(jsonObject.hasOwnProperty("options")){
                var $select = $('#size_select')
                feed_options = jsonObject;
                sizes = Object.keys(jsonObject["options"])
                $select.find('option').remove();
                for (var i=0;i<sizes.length;i++) {
                    $select.append('<option value=' + sizes[i] + '>' + sizes[i]+ '</option>');
                }
                setUpListeners();
            }else if(jsonObject.hasOwnProperty("error")){
                alert(jsonObject["error"])
            }else if(jsonObject.hasOwnProperty("stream_start")){
                 start(selected_stream);
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