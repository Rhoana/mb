var D = D || {};

D.manager = function() {

  this._data_path = null;

  // the three OSD viewers for prev, current and next
  this._prev_viewer = null;
  this._viewer = null;
  this._next_viewer = null;

  // the contrast value
  this._contrast = 10;

  this.init();

};

D.manager.prototype.init = function() {

  // let's parse the url args
  var args = UTIL.parse_args();

  if (args['data']) {

    // directly view data
    this.view(args['data']);

  } else {

    // show tree view
    this.setup_tree();

  }

};


D.manager.prototype.view = function(data_path) {

  if (this._data_path) {

    // we have data loaded - reset everything

    if (this._prev_viewer) {
      this._prev_viewer.destroy();
    }
    this._prev_viewer = null;

    if (this._viewer) {
      this._viewer.destroy();
    }
    this._viewer = null;

    if (this._next_viewer) {
      this._next_viewer.destroy();
    }
    this._next_viewer = null;

    $('#viewers').html("");

    // the contrast value
    this._contrast = 10;

    this.setup_controls();

  }

  this._data_path = data_path;

  // get the contents for the data path
  var contents = $.ajax({
      type: "GET",
      url: 'content/' + this._data_path
    }).done(function() {
      
      // setup the viewer
      this.setup_viewer(JSON.parse(contents.responseText));

      // and the controls
      this.setup_controls();

    }.bind(this));

};


D.manager.prototype.setup_tree = function() {


  var tree = $('#nav').tree({});


  tree.bind(
      'tree.click', 
      function(e) {

        var node = e.node;
        var element = e.node.element;

        // if (node.type == "NULL") {


          var r = $.ajax({
            url: 'type/' + node.full_url,
            type: 'GET'
          }).done(function() {

            node.type = r.responseText;
            
            if (element.children[0].children.length == 2) {
              $(element.children[0]).append("&nbsp;&nbsp;<img style='vertical-align:middle' src='gfx/"+node.type+".gif' onclick='MANAGER.view(\""+node.full_url+"\")'>");
            }

          });

      }

    );  

};


D.manager.prototype.setup_viewer = function(content) {

  this._content = content;
  console.log(content)

  for (var i=0; i<content.length; i++) {

    content[i].meta_info_url = 'metainfo/' + content[i].data_path;

    content[i].getTileUrl = function( level, x, y ) {
      // in openseadragon:
      // 0: smallest
      // for us, 0 is the largest
      level = this.maxLevel - level;

      return "data/" + this.data_path + '/' + level + "-" + x + "-" + y + "-" + this.layer;
    
    }

  }

  this._page = 0;

  this._viewer = this.create_viewer(this._page, true);

  if (content.length > 1) {
    this._next_viewer = this.create_viewer(this._page+1, false);
  }

  // update data_path in the controller
  this._data_path = content[0].data_path;

};



D.manager.prototype.create_viewer = function(page, visible) {
  
  // create dom element
  var container_id = 'viewer_'+page;
  if (!visible) {
    var style = 'z-index:0'//display:none';
  } else {
    var style = 'z-index:1';
  }

  $('#viewers').append('<div id="'+container_id+'" class="viewers" style="'+style+'"></div>');

  var ts = this._content[page];

  var meta_info = $.ajax({
    type: "GET",
    url: ts.meta_info_url,
    async: false
  }).responseText;

  meta_info = JSON.parse(meta_info);

  ts.width = meta_info.width;
  ts.height = meta_info.height;
  ts.minLevel = meta_info.minLevel;
  ts.maxLevel = meta_info.maxLevel;
  ts.tileSize = meta_info.tileSize;
  ts.layer = meta_info.layer;


  var viewer = OpenSeadragon({
      id:            container_id,
      prefixUrl:     "images/",
      navigatorSizeRatio: 0.25,
      maxZoomPixelRatio: 10,
      showNavigationControl: false,
      imageLoaderLimit: 3,
      tileSources:   ts
    });

  viewer.innerTracker.keyHandler = null;
  viewer.innerTracker.keyDownHandler = null;

  // keyboard (needs to be rebound to overwrite OSD)
  window.onkeydown = this.onkeydown.bind(this);

  return viewer;  

};



D.manager.prototype.setup_controls = function() {

  // update sequence label
  if (this._content.length > 1) {
    $('#section').html('Section 1/'+this._content.length);
    $('.labels').show();
  } else {
    $('.labels').hide();
  }

  $("#contrast").slider({
    range: "min",
    min: 10,
    max: 100,
    value: 10,
    slide: function(e, ui) {
      MANAGER._contrast = ui.value;
      MANAGER.update_parameters();
    }
  });

  // keyboard
  $('window').onkeydown = this.onkeydown.bind(this);

};

D.manager.prototype.onkeydown = function(e) {

  if (e.keyCode == 87) {
  
    this._keypress_callback = setTimeout(function() {
      this.move(1);
      this._keypress_callback = null;
    }.bind(this),10);   

  } else if (e.keyCode == 83) {
  
    this._keypress_callback = setTimeout(function() {
      this.move(-1);
      this._keypress_callback = null;
    }.bind(this),10);   

  }

};

D.manager.prototype.update_parameters = function() {

  $('#section').html('Section '+(this._page+1)+'/'+this._content.length);


  $(MANAGER._viewer.canvas.children[0]).css('webkit-filter','contrast('+(this._contrast)/10+')');

};




D.manager.prototype.propagate_viewport = function(event) {

  // propagate the current viewport to the previous and the next viewers

  // console.log('propagating viewport', event.eventSource.id)
  return
  if (this._prev_viewer) {
    this._prev_viewer.viewport.panTo(this._viewer.viewport.getCenter(), true);
    this._prev_viewer.viewport.zoomTo(this._viewer.viewport.getZoom(), null, true);    
  }

  if (this._next_viewer) {
    this._next_viewer.viewport.panTo(this._viewer.viewport.getCenter(), true);
    this._next_viewer.viewport.zoomTo(this._viewer.viewport.getZoom(), null, true);    
  }

};



D.manager.prototype.move = function(sign) {

  if (this._page + 1*sign >= this._content.length) {
    // console.log('reached right end');
    return;
  } else if (this._page + 1*sign < 0) {
    // console.log('reached left end');
    return;
  }

  var old_container = '#viewer_'+this._page;
  this._page += 1*sign;
  var new_container = '#viewer_'+this._page;
  
  // 
  this._data_path = this._content[this._page].data_path;


  if (sign > 0) {
    // moving to next

    // we destroy the old previous viewer
    if (this._prev_viewer) {
      // this._prev_viewer.removeAllHandlers('pan');
      // this._prev_viewer.removeAllHandlers('zoom');
      this._prev_viewer.destroy();
      // console.log('freeing previous viewer');
    }

    // the prev viewer is set to the current one
    var old_viewer = this._viewer;
    // old_viewer.removeAllHandlers('pan');
    // old_viewer.removeAllHandlers('zoom');        
    this._prev_viewer = this._viewer;
    // this._prev_viewer.removeAllHandlers('pan');
    // this._prev_viewer.removeAllHandlers('zoom');

    // the current viewer is set to the next one
    this._viewer = this._next_viewer;

    // this._viewer.addHandler('pan', this.propagate_viewport.bind(this));
    // this._viewer.addHandler('zoom', this.propagate_viewport.bind(this));


    // and the next viewer shall be a new one
    if (this._page+1 >= this._content.length) {
      this._next_viewer = null;
    } else {
      // this._controller.request_meta_data(this._content[this._page+1]['data_path'])
      this._next_viewer = this.create_viewer(this._page+1, false);
    }
    

  } else {
    // moving to prev

    // we destroy the old next viewer
    if (this._next_viewer) {
      // this._next_viewer.removeAllHandlers('pan');
      // this._next_viewer.removeAllHandlers('zoom');      
      this._next_viewer.destroy();
      // console.log('freeing next viewer');
    }

    // the next viewer is set to the current one
    var old_viewer = this._viewer;
    // old_viewer.removeAllHandlers('pan');
    // old_viewer.removeAllHandlers('zoom');          
    this._next_viewer = this._viewer;
    // this._next_viewer.removeAllHandlers('pan');
    // this._next_viewer.removeAllHandlers('zoom'); 

    // the current viewer is set to the previous one
    this._viewer = this._prev_viewer;

    // this._viewer.addHandler('pan', this.propagate_viewport.bind(this));
    // this._viewer.addHandler('zoom', this.propagate_viewport.bind(this));


    // and the previous viewer shall be a new one
    if (this._page-1 < 0) {
      this._prev_viewer = null;
    } else {
      this._prev_viewer = this.create_viewer(this._page-1, false);
    }

  }

  this._viewer.viewport.panTo(old_viewer.viewport.getCenter(), true);
  this._viewer.viewport.zoomTo(old_viewer.viewport.getZoom(), null, true);

  $(new_container).css('z-index', 1);    
  $(old_container).css('z-index', 0);

  this.update_parameters();

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