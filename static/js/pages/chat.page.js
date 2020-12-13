import BBParser from '../utils/BBParser.js';
import { NotificationType } from '../constants/constants.js';
import ChatService from '../services/chat.service.js';

// vars
let unreadMsgCount = 0;
const picker = new EmojiButton({
  position: 'top',
  showPreview: false
});

// elements
const chat = $("#chat");
const imageInput = $("#image-input");
const userControls = $("#user-controls :input");
const button = document.querySelector('#emoji-btn');

// services
let chatService;

window.submitMessage = () => {
  const message = document.getElementById("message").value;
  if (message && message.trim()) {
    $("#btn-send").html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
    chatService.emitMessage(message, () => {
      $("#btn-send").html('SEND');
      $("#message").val('');
    })
  }
}

window.uploadFile = () => {
  imageInput.click();
}

document.addEventListener("visibilitychange", function () {
  if (!document.hidden) {
    document.title = "Hexora";
    unreadMsgCount = 0;
  }
});

setInterval(() => {
  $(".disposable").remove();
}, 2000);

// press enter to submit the message
$("#message").keypress(function (e) {
  chatService.emitNotification(NotificationType.KEYPRESS);
  var key = e.which;
  if (key == 13) {
    $("#btn-send").click();
    return false;
  }
});

picker.on('emoji', emoji => {
  document.querySelector('#message').value += emoji;
  $('#message').focus();
});

button.addEventListener('click', () => {
  if (picker.pickerVisible) {
    picker.hidePicker();
  } else {
    picker.showPicker(button)
  };

});

$('#message').keydown(function (e) {
  if (e.ctrlKey && e.keyCode == 13) {
    picker.pickerVisible ? picker.hidePicker() : picker.showPicker(button);
  }
});

$('#image-input').on('change', () => {
  const fileReader = new FileReader();
  fileReader.onload = () => {
    const data = fileReader.result;
    userControls.attr("disabled", true);;
    chatService.emitMessage(`[img]${data}[/img]`, () => {
      userControls.attr("disabled", false);
    })
  };
  if (imageInput.prop('files').length > 0) {
    const file = imageInput.prop('files')[0];
    fileReader.readAsDataURL(file);
  }
});

chatService = new ChatService();
chatService.getNotifications((notification) => {
  switch (notification.type) {
    case NotificationType.KEYPRESS:
      const eventKeypress = `
            <div class="message message-eventKeypress disposable">
                <span class="messsage-text">
                    ${notification.email} is typing...
                </span>
            </div>
            `;
      $(".disposable").remove();
      chat.append(eventKeypress)
      chat.scrollTop(chat.prop("scrollHeight"));
      break;
    case NotificationType.JOIN:
      const eventJoin = `
            <div class="message message-eventJoin">
                <span class="messsage-text">
                    ${notification.email} joined to room!
                </span>
            </div>
            `;
      chat.append(eventJoin)
      chat.scrollTop(chat.prop("scrollHeight"));
      break;
    case NotificationType.EXIT:
        const eventLeft = `
                <div class="message message-eventJoin">
                    <span class="messsage-text">
                        ${notification.email} just left the room!
                    </span>
                </div>
                `;
        chat.append(eventLeft)
        chat.scrollTop(chat.prop("scrollHeight"));
        break;
  }
});

chatService.getMessages((message) => {
  $(".disposable").remove();
  let messageNode;
  if (email === message.email) {
    const messageOut = `
        <div class="message message-out">
            <span class="messsage-text">
                ${BBParser.parse(decodeURIComponent(message.message))}
            </span>
        </div>
        `;
    messageNode = messageOut;
  } else {
    const messageIn = `
        <div class="message message-in">
            <span class="message-sender">
                ${message.email}
            </span> <br>
            <span class="messsage-text">
                ${BBParser.parse(decodeURIComponent(message.message))}
            </span>
        </div>
        `;
    messageNode = messageIn;
  }
  chat.append(messageNode);
  chat.scrollTop(chat.prop("scrollHeight"));
  if (document.hidden) {
    setTimeout(() => {
      playAlert("pop");
    }, 10);
    document.title = `(${++unreadMsgCount}) Hexora Web`;
  }
})