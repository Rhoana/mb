var D = D || {};

D.controller = function(manager) {

  this._manager = manager;

  this._user_id = UTIL.make_id();

  this._data = null;

};

D.controller.prototype.on_message = function(message) {

  // check message type
  if (message['name'] == 'NEW_DATA') {
    
    this.update_tree(message['value']);

  } else if (message['name'] == 'CONTENT') {
    
    this.parse_contents(message['value']);

  } else if (message['name'] == 'REFRESH') {

    this.refresh(message['value']);

  }

};

D.controller.prototype.parse_contents = function(contents) {

  console.log('Content:', contents);
  
  this._manager.setup_viewer(contents);

};

D.controller.prototype.request_content = function() {

  if (!this._data) return;

  console.log('Requesting content listing for', this._data);

  var output = {};
  output['name'] = 'CONTENT';
  output['origin'] = this._user_id;
  output['value'] = this._data;
 
  this._manager._websocket.send(output);

};

D.controller.prototype.refresh = function(data_path) {

  if (this._data == data_path) {
    // yep, we should refresh

    this._manager.refresh_viewer();
    
  }

};

D.controller.prototype.update_tree = function(data) {
  
  new_data = [];
  UTIL.traverse_dictionary(data, function(current, children) {
    var n = {};
    n.label = current;
    if (children) {
      n.children = [children];
    } else {
      n.children = [];
    }

    // if top-level
    new_data.push(n);
  });
  

  // $('#nav').tree({
  //   data: data,
  //   autoOpen: 0
  // });

};
