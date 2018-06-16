(function () {
    try {
        console.log('Pull server status from "{{ server_status_url }}"');
        var statusSocket = new WebSocket('{{ server_status_url }}');
        var realTimeStatusEnabled = false;
        var realTimeStatusMessageID = null;
        var forceDisable = false;

        function makeForceDisable() {
            forceDisable = true;
            /*setTimeout(function(){
              $('figure.real-time-status').html('<i class="fas fa-ban"></i><b>Real time status disabled</b>');
            },100);*/
        }

        statusSocket.onopen = function (e) {
            e.stopImmediatePropagation()
            e.stopPropagation()
            e.preventDefault()
            return false;
        };

        statusSocket.onerror = function (e) {
            e.stopImmediatePropagation()
            e.stopPropagation()
            e.preventDefault()
            if (forceDisable) return false;
            makeForceDisable();
            console.log('Server status is not real-time available. Socket errored :(');
            return false;
        };

        statusSocket.onmessage = function (e) {
            if (forceDisable) return;
            var data = JSON.parse(e.data);
            if (data) {
                if (data.server_mode == 'init') {
                    console.log('Server status real-time is available :)');
                    realTimeStatusEnabled = true;
                    setTimeout(function () {
                        $('figure.real-time-status').html('<i class="fas fa-asterisk"></i><b>Real time status enabled</b>');
                    }, 100);
                }
                if (realTimeStatusEnabled) {
                    if (data.server_mode == 'progress') {
                        console.log(data);
                        var message = data.server_status || {};
                        var task_name = message.task_name;
                        var task_progress = message.task_progress;
                        if (realTimeStatusMessageID === null) {
                            if (window.showMessage) {
                                realTimeStatusMessageID = window.showMessage({
                                    info: 'Server: ...',
                                    autoHide: false,
                                    click: false
                                });
                            }
                        } else {
                            if (window.changeMessageText) {
                                window.changeMessageText(realTimeStatusMessageID, 'Server: ' + task_name + ' ' + task_progress);
                            }
                        }
                    } else if (data.server_mode == 'progress_end') {
                        if (window.hideMessage) {
                            window.hideMessage(realTimeStatusMessageID);
                            realTimeStatusMessageID = null;
                            realTimeStatusMessageID = window.showMessage({
                                info: (data.server_status + '')
                            })
                        }
                    }
                }
            }
        };

        statusSocket.onclose = function (e) {
            if (forceDisable) return;
            makeForceDisable();
            console.error('Server status is not real-time available. Socket closed unexpectedly :(');
        };
    } catch (e) {
        if (forceDisable) return;
        makeForceDisable();
        console.log('Server status is not real-time available. Socket errored :(');
    }
})();