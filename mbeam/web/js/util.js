var UTIL = {};

UTIL.traverse_dictionary = function(o, func) {
  for (var i in o) {
    
    func.apply(this,[i,o[i]]);  
    
    if (o[i] !== null && typeof(o[i])=="object") {
      //going on step down in the object tree!!
      UTIL.traverse_dictionary(o[i],func);
    }
  }
};


UTIL.parse_args = function() {

  // from http://stackoverflow.com/a/7826782/1183453
  var args = document.location.search.substring(1).split('&');
  argsParsed = {};
  for (var i=0; i < args.length; i++)
  {
      arg = unescape(args[i]);

      if (arg.length == 0) {
        continue;
      }

      if (arg.indexOf('=') == -1)
      {
          argsParsed[arg.replace(new RegExp('/$'),'').trim()] = true;
      }
      else
      {
          kvp = arg.split('=');
          argsParsed[kvp[0].trim()] = kvp[1].replace(new RegExp('/$'),'').trim();
      }
  }

  return argsParsed;

};



UTIL.make_id = function() {
  var text = "";
  var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

  for( var i=0; i < 5; i++ )
      text += possible.charAt(Math.floor(Math.random() * possible.length));

  return text;
};
