(function () {
    ///airlines/api/check-auth/
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    function requestCSRFToken() {
        return getCookie('csrftoken');
    };

    function checkUserAuth(callback) {
        authCheckDataAPI(function (res) {
            callback(res);
        });
    };

    function authCheckDataAPI(callback, errCallback) {
        var params = {};
        var path = '/airlines/api/check-auth/';
        var req = new XMLHttpRequest();
        req.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var res = null;
                try {
                    res = JSON.parse(this.responseText);
                } catch (e) {
                    res = null;
                }
                if (res) {
                    callback(res[0] || null, res);
                } else {
                    if (errCallback) {
                        errCallback();
                    }
                }
            } else if (this.readyState == 4) {
                if (errCallback) {
                    errCallback();
                }
            }
        };
        req.open('GET', path, true);
        req.setRequestHeader('Content-Type', 'application/json');
        req.setRequestHeader('X-CSRFToken', requestCSRFToken());
        req.send(JSON.stringify(params));
    };


    function requestDataAPI(route, callback, errCallback) {
        var path = '/airlines/api/' + route;
        var req = new XMLHttpRequest();
        req.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var res = null;
                try {
                    res = JSON.parse(this.responseText);
                } catch (e) {
                    res = null;
                }
                if (res) {
                    callback(res.results || [], res);
                } else {
                    if (errCallback) {
                        errCallback();
                    }
                }
            } else if (this.readyState == 4) {
                if (errCallback) {
                    errCallback();
                }
            }
        };
        req.open('GET', path, true);
        req.send();
    };

    function patchDataAPI(route, params, callback, errCallback) {
        var path = '/airlines/api/' + route;
        var req = new XMLHttpRequest();
        req.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var res = null;
                try {
                    res = JSON.parse(this.responseText);
                } catch (e) {
                    res = null;
                }
                if (res) {
                    callback(res.results || [], res);
                } else {
                    if (errCallback) {
                        try {
                            res = JSON.parse(this.responseText);
                        } catch (e) {
                            res = null;
                        }
                        errCallback(res);
                    }
                }
            } else if (this.readyState == 4) {
                if (errCallback) {
                    try {
                        res = JSON.parse(this.responseText);
                    } catch (e) {
                        res = null;
                    }
                    errCallback(res);
                }
            }
        };
        req.open('PATCH', path, true);
        req.setRequestHeader('Content-Type', 'application/json');
        req.setRequestHeader('X-CSRFToken', requestCSRFToken());
        req.send(JSON.stringify(params));
    };

    function getParameterByName(name, url) {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    window.requestDataAPI = requestDataAPI;
    window.patchDataAPI = patchDataAPI;
    window.checkUserAuth = checkUserAuth;
    window.getParameterByName = getParameterByName;

})();