var D = D || {};

D.manager = function() {

  this._websocket = null;

};

D.manager.prototype.init = function() {

  this._websocket = new D.websocket(this);

};
