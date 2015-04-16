var D = D || {};

D.manager = function() {

  this._websocket = null;
  this._controller = new D.controller(this);

  this._viewers = [];

  this._contrast = 10;

  this.init();

};

D.manager.prototype.init = function() {

  // let's parse the url args
  var args = UTIL.parse_args();

  if (args['data']) {
    this._controller._data = args['data'];
  }


  this._websocket = new D.websocket(this);

  this.setup_controls();

};

D.manager.prototype.setup_controls = function() {

  $("#contrast").slider({
    range: "min",
    min: 10,
    max: 100,
    value: 10,
    slide: function(e, ui) {
      // $("#c_currentVal").html(ui.value);
      MANAGER._contrast = ui.value;
      MANAGER.update_parameters();
    }
  });

};

D.manager.prototype.update_parameters = function() {

  $(MANAGER._viewer.canvas.children[0]).css('webkit-filter','contrast('+(this._contrast)/10+')');

};

D.manager.prototype.update_tree = function(data) {

  $('#nav').tree({
    data: data,
    autoOpen: 0
  });

};

D.manager.prototype.setup_viewer = function(content) {

  this._content = content;

  for (var i=0; i<content.length; i++) {

    var that = this;

    content[i].getImageInfo = function(a,b,c) {
      console.log('aaa',a,b,c)
    }

    content[i].getTileUrl = function( level, x, y ) {
      // in openseadragon:
      // 0: smallest
      // for us, 0 is the largest
      level = this.maxLevel - level;

      // // grab the image roi
      // var viewport_top_left = new OpenSeadragon.Point(0,0);
      // var viewport_bottom_right = new OpenSeadragon.Point(window.document.body.clientWidth, window.document.body.clientHeight);
      // var image_top_left = openseadragon.viewport.windowToImageCoordinates(viewport_top_left);
      // var image_bottom_right = openseadragon.viewport.windowToImageCoordinates(viewport_bottom_right);

      // var image_top_left_x = Math.floor(Math.max(0, image_top_left.x));
      // var image_top_left_y = Math.floor(Math.max(0, image_top_left.y));
      // var image_bottom_right_x = Math.floor(Math.min(this.width, image_bottom_right.x));
      // var image_bottom_right_y = Math.floor(Math.min(this.height, image_bottom_right.y));

      // TODO fragile with passing the data

      return "data/" + this.data_path + '/' + level + "-" + x + "-" + y + "-" + this.layer;// + '-' + Math.random();// + '-'+image_top_left_x+'-'+image_top_left_y+'-'+image_bottom_right_x+'-'+image_bottom_right_y;
    
    }

  }

  this._page = 0;

  this._viewers.push(this.create_viewer(this._page, true));
  this._viewers.push(this.create_viewer(this._page+1, false));

  // we need to monitor page changes to update our data path
  // this._viewer.addHandler('page', function(event) {

  //   this._controller._data = content[event.page].data_path;

  // }.bind(this));

  // update data_path in the controller
  this._controller._data = content[0].data_path;

  

};

D.manager.prototype.create_viewer = function(page, visible) {
  
  // create dom element
  var container_id = 'viewer_'+page;
  if (!visible) {
    var style = 'display:none';
  } else {
    var style = '';
  }

  $('#viewers').append('<div id="'+container_id+'" style="'+style+'"></div>');

  return OpenSeadragon({
      id:            container_id,
      prefixUrl:     "images/",
      navigatorSizeRatio: 0.25,
      // preserveViewport: true,
      // sequenceMode:   false,
      maxZoomPixelRatio: 10,
      showFullPageControl: false,
      imageLoaderLimit: 3,
      // showNavigator: true,
      tileSources:   this._content[page]
    });

};



D.manager.prototype.next = function() {

  var old_container = '#viewer_'+this._page;
  this._page++;
  var new_container = '#viewer_'+this._page;
  
  // 
  this._controller._data = this._content[this._page].data_path;
  // CCC[this._page].width = CCC[0].width
  // CCC[this._page].height = CCC[0].height
  // CCC[this._page].layer = 0;

  // this._viewer.destroy();

  // var new_viewer = this.create_viewer(this._page, false);

  this._viewers.push(this.create_viewer(this._page+1, false));

  $(new_container).show();
  $(old_container).hide();

  // this._viewer = new_viewer;

  // this._viewer.destroy();

  // hide current viewer

  // show new viewer

};

D.manager.prototype.prev = function() {
  

  var old_container = '#viewer_'+this._page;
  this._page--;
  var new_container = '#viewer_'+this._page;
  
  // 
  this._controller._data = this._content[this._page].data_path;
  // CCC[this._page].width = CCC[0].width
  // CCC[this._page].height = CCC[0].height
  // CCC[this._page].layer = 0;

  // this._viewer.destroy();

  // var new_viewer = this.create_viewer(this._page, false);

  this._viewers.push(this.create_viewer(this._page-1, false));

  $(new_container).show();
  $(old_container).hide();

};


D.manager.prototype.refresh_viewer = function() {

  console.log('Refreshing');
  this._viewer.world.resetItems();

};