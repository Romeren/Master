function loadRestService(htmlLocation, hostLocaton, requestType="GET", data = "") {
    $.ajax({
     type: requestType,
     url: hostLocaton,
     data: data,
    // xhrFields: {
    //     withCredentials: true
    // },
     success:function(response){
         // do stuff with json (in this case an array)
         $(htmlLocation).html(response);
     },
     error:function(){
         console.log("cannot load from:");
         console.log(hostLocaton);
         //alert("Error could not load content from: " + hostLocaton);
     }
    });
    return false;
}

class ServiceHandler {
    constructor() {
        this.connection_dict = {};
    }

    connect(address, location) {
        var socket = new WebSocketHandler(address, location);
        this.connection_dict[location] = socket;
    }

    send_message(location, message) {
        this.connection_dict[location].connection.send(JSON.stringify(message))
    }
}


class WebSocketHandler{
    constructor(address, location) {
        this.connection = new WebSocket(address);
        this.location = location

        this.connection.onopen = function(){
           console.log('Connection open!');
        }

        this.connection.onclose = function(){
           console.log('Connection closed');
        }

        this.connection.onerror = function(error){
           console.log('Error detected: ' + error);
        }

        this.connection.onmessage = function(e){
            console.log(e.data);
            var server_message = JSON.parse(e.data);
            if (server_message.hasOwnProperty('panel')){
                $('#' + location).html(server_message.panel);
            }
        }
    }
}

var plugin_handler = new ServiceHandler()
