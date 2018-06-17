$(document).ready(function() {
    (function () {

        let realTimeStatusEnabled = true;
        let realTimeStatusMessageID = null;
        const webSocketBridge = new channels.WebSocketBridge();
        webSocketBridge.connect(SERVER_STATUS_URL);
        webSocketBridge.listen(function(action, stream) {
            var data = action;
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
        });
    })();
});