(function(){

  var messageIDCounter = 1;

  function showMessage(parsedParams) {
    if(parsedParams.error) {
      parsedParams.message = parsedParams.error;
      parsedParams.messageType = 'error';
    } else if(parsedParams.info) {
      parsedParams.message = parsedParams.info;
      parsedParams.messageType = 'info';
    }

    var autoHide = parsedParams.autoHide;
    if(autoHide === null || typeof autoHide === 'undefined') {
      autoHide = true;
    }
    
    var enableClickDismiss = parsedParams.click;
    if(enableClickDismiss === null || typeof enableClickDismiss === 'undefined') {
      enableClickDismiss = true;
    }
    
    if(parsedParams.message) {
      var messageID = messageIDCounter;
      messageIDCounter++;
      
      var messageObj = $('<p></p>');
      messageObj.addClass('message');
      messageObj.css('margin-left', '100vw');
      messageObj.attr('id', 'message'+messageID);
      messageObj.addClass(parsedParams.messageType);
      messageObj.html(decodeURI(decodeURI(parsedParams.message)));
      setTimeout(function(){
        $('.messagesContainer').append(messageObj);
        if(enableClickDismiss) {
          messageObj.click(function(){
            messageObj.stop().animate({
              marginLeft: '110vw'
            }, 'slow');
          });
        } else {
          messageObj.css('cursor', 'default');
        }
        messageObj.animate({
          marginLeft: '50vw'
        }, 'slow');
        if(autoHide) {
          setTimeout(function(){
            messageObj.stop().animate({
              marginLeft: '110vw'
            }, 'slow');
          }, 4000);
        }
      }, 750);
    }
    
    return messageID;
  }
  
  function changeMessageText(messageID, newText, parsedParams) {
    var messageObj = $('#message'+messageID);
    if(messageObj.length <= 0) {
      if(parsedParams) {
        messageID = showMessage(parsedParams)
        messageObj = $('#message'+messageID);
      } else {
        return;
      }
    }
    if(!messageObj.length) return;
    messageObj.text(newText)
  }
  
  function hideMessage(messageID) {
    var messageObj = $('#message'+messageID);
    if(!messageObj.length) return;
    messageObj.stop().animate({
      marginLeft: '110vw'
    }, 'slow');
  }

  $(document).ready(function(){
    var parsedParams = location.search.replace('?','').split('&').reduce(function(s,c){var t=c.split('=');s[t[0]]=t[1];return s;},{});
    showMessage(parsedParams);
  });

  window.showMessage = showMessage;
  window.changeMessageText = changeMessageText;
  window.hideMessage = hideMessage;

})();