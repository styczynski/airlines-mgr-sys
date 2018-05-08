$(document).ready(function(){
  var parsedParams = location.search.replace('?','').split('&').reduce(function(s,c){var t=c.split('=');s[t[0]]=t[1];return s;},{});
  
  if(parsedParams.error) {
    parsedParams.message = parsedParams.error;
    parsedParams.messageType = 'error';
  } else if(parsedParams.info) {
    parsedParams.message = parsedParams.info;
    parsedParams.messageType = 'info';
  }
  
  if(parsedParams.message) {
    var messageObj = $('<p></p>');
    messageObj.addClass('message');
    messageObj.css('margin-left', '100vw');
    messageObj.addClass(parsedParams.messageType);
    messageObj.html(decodeURI(parsedParams.message));
    setTimeout(function(){
      $('.messagesContainer').append(messageObj);
      messageObj.click(function(){
        messageObj.stop().animate({
          marginLeft: '110vw'
        }, 'slow');
      });
      messageObj.animate({
        marginLeft: '50vw'
      }, 'slow');
      setTimeout(function(){
        messageObj.stop().animate({
          marginLeft: '110vw'
        }, 'slow');
      }, 4000);
    }, 750);
  }
});