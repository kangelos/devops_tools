//
// original code from mqtt-panel
// abuser: angelos@unix.gr
//
//
let serial;
let username;
let password;
let relay ;
let mqtt;
let message;
let destination;
let topic = '/dingtian/#';
let switches = [];

let useTLS = true;
let cleansession = true;
let reconnectTimeout = 5000;
let host = 'mqtt-server';
let port = 9001;

function MQTTconnect() {
    if ((typeof username == "undefined") ||  (typeof password == "undefined")) {
        showPopup();
        return;
    }
    if (typeof path == "undefined") {
        path = '/';
    }
    mqtt = new Paho.MQTT.Client(host, port, path, "kangelos-"+Math.floor(Math.random() * 1000));
    let options = {
        timeout: 300,
        useSSL: useTLS,
        cleanSession: cleansession,
        onSuccess: onConnect,
        userName: username,
        password: password,
        onFailure: function (message) {
            $('#status').html("Connection failed: " + message.errorMessage + "Retrying...").attr('class', 'alert alert-danger');
            setTimeout(MQTTconnect, reconnectTimeout);
        }
    };

    mqtt.onConnectionLost = onConnectionLost;
    mqtt.onMessageArrived = onMessageArrived;
    console.log("Host: " + host + ", Port: " + port + ", Path: " + path + " TLS: " + useTLS);
    mqtt.connect(options);
};

function onConnect() {
    $('#status').html('Connected')
        .attr('class', 'alert alert-success');
    mqtt.subscribe(topic, { qos: 1 });
    $('#topic').html(topic);
    document.getElementById("popup").style.display = "none";
};

function onConnectionLost(response) {
    setTimeout(MQTTconnect, reconnectTimeout);
    $('#status').html("Connection Lost, Reconnecting...")
        .attr('class', 'alert alert-warning');
};

function onMessageArrived(message) {
    let topic   = message.destinationName;
    let payload = message.payloadString;
    let topics  = topic.split('/');
    let serial  = topics[2];
    let inout   = topics[3];
    let relay   = topics[4];

    serial=serial.replace("relay","");
    idx=add_switch(serial);
    idx++;

    const re = new RegExp('\/dingtian\/relay[1-9]+\/in/r[1-9]');
    if ( ! re.test(topic) ) {
        return;
    }
    console.log("Topic:"+topic+" Payload:"+payload);
    
    let relnum=relay.replace("r","");

    serial=serial.replace("relay","");
//    console.log("Switch:" + serial + ", Relay: " + relay + ", State: " + payload);

    document.getElementById("switch-number"+idx).style.display = "block";
    document.getElementById("number"+idx).innerHTML=serial;

    let label =    '#number' +idx +'-label' + relnum;
    let valuetag = '#number'+ idx +'-value' + relnum;
    $(valuetag).html('State: ' + payload );

    switch(payload) {
        case('ON'):
            $(label).text('ON');
            $(label).removeClass('badge-danger').addClass('badge-success');
            break;
        case('OFF'): 
            $(label).text('OFF');
            $(label).removeClass('badge-success').addClass('badge-danger');
            break;
        default:
            console.log("Uknown Payload:"+payload);
            break;
    }
};


function toggle(number,relay,state) {
    number=number.replace("number","");
    idx=parseInt(number,10)-1;
    serial=switches[idx];
    console.log("Turning " +state+" Relay:"+relay+ ' On Switch:'+serial);
    destination='/dingtian/relay'+serial+'/in/'+relay;

    message = new Paho.MQTT.Message(state);
    message.destinationName = destination;
    message.retained=true;
    message.qos=1;
    mqtt.send(message);
}


function donepass() {
    username = document.getElementById("user").value;
    password = document.getElementById("pass").value;
    $('#status').html("Attempting to connect...")
        .attr('class', 'alert alert-warning');
    MQTTconnect();
};


function showPopup() {
    $('#status').html("Please Login")
        .attr('class', 'alert alert-warning');
     document.getElementById("popup").style.display = "block";
}

$(document).ready(function () {
    MQTTconnect();
});


function add_switch(serial) {
	for (i=0; i<switches.length; i++) {
		if ( switches[i] == serial ) {
			return(i);
		}
	}
	switches.push(serial);
	return(i);
}

