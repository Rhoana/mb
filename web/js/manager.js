var D = D || {};

D.manager = function() {

  this._websocket = null;
  this._controller = new D.controller(this);

  this.init();

};

D.manager.prototype.init = function() {

  // let's parse the url args
  var args = UTIL.parse_args();

  if (args['data']) {
    this._controller._data = args['data'];
  }


  this._websocket = new D.websocket(this);

};

D.manager.prototype.update_tree = function(data) {

  $('#nav').tree({
    data: data,
    autoOpen: 0
  });

};

D.manager.prototype.setup_viewer = function(content) {

  for (var i=0; i<content.length; i++) {

    var that = this;

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

      return "/data/" + that._controller._data + '/' + level + "-" + x + "-" + y + "-" + this.layer + '-' + Math.random();// + '-'+image_top_left_x+'-'+image_top_left_y+'-'+image_bottom_right_x+'-'+image_bottom_right_y;
    
    }

  }

  openseadragon = OpenSeadragon({
    id:            "viewer",
    prefixUrl:     "images/",
    navigatorSizeRatio: 0.25,
    preserveViewport: true,
    tileSources:   content
  });

};