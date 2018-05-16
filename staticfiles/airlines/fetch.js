(function(){
  
  function requestDataAPI(route, callback, errCallback) {
    var path = '/api/'+route;
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
      if(this.readyState == 4 && this.status == 200) {
        var res = null;
        try {
          res = JSON.parse(this.responseText);
        } catch(e) {
          res = null;
        }
        if(res) {
          callback(res.results || [], res);
        } else {
          if(errCallback) {
            errCallback();
          }
        }
      } else if(this.readyState == 4) {
        if(errCallback) {
          errCallback();
        }
      }
    };
    req.open('GET', path, true);
    req.send();
  };
  
  function patchDataAPI(route, params, callback, errCallback) {
    var path = '/api/'+route;
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
      if(this.readyState == 4 && this.status == 200) {
        var res = null;
        try {
          res = JSON.parse(this.responseText);
        } catch(e) {
          res = null;
        }
        if(res) {
          callback(res.results || [], res);
        } else {
          if(errCallback) {
            errCallback();
          }
        }
      } else if(this.readyState == 4) {
        if(errCallback) {
          errCallback();
        }
      }
    };
    req.open('PATCH', path, true);
    req.setRequestHeader('Content-Type', 'application/json');
    req.send(JSON.stringify(params));
  };
  
  window.requestDataAPI = requestDataAPI;
  window.patchDataAPI = patchDataAPI;
  
})();