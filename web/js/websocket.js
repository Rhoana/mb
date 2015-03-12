var D = D || {};

D.websocket = function(manager) {

  this._manager = manager;

  this._controller = this._manager._controller;

  this._socket = null;

  this.connect();

};

D.websocket.prototype.connect = function() {

  try {

    var host = "ws://"+window.location.hostname+":"+window.location.port+"/ws";  
    this._socket = new WebSocket(host);
    this._socket.binaryType = 'arraybuffer';
    this._socket.onopen = this.on_open.bind(this);
    this._socket.onmessage = this.on_message.bind(this);
    this._socket.onclose = this.on_close.bind(this);

  } catch (e) {
    console.log('Websocket connection failed.');
  }

};

D.websocket.prototype.on_open = function() {

  console.log('Established websocket connection.');

  this._controller.request_content();

};

D.websocket.prototype.on_message = function(m) {

  this._controller.on_message(JSON.parse(m.data));

};

D.websocket.prototype.send = function(m) {

  this._socket.send(JSON.stringify(m));

};

D.websocket.prototype.on_close = function() {

  console.log('Websocket connection dropped.');

};
