let protocol;
let unreadMsgCount = 0;
if (location.hostname.includes('localhost')) {
    protocol = 'http://'
} else {
    protocol = 'https://'
}
document.addEventListener("visibilitychange", function() {
    if (!document.hidden) {
        document.title = "Hexora";
        unreadMsgCount = 0;
    }
});

var socket = io.connect(`${protocol}${location.hostname}:${location.port}`)
socket.on(chatId, (data) => {
    if (data && data.hasOwnProperty('message')) {
        let message;
        if (email === data.email) {
            const messageOut = `
            <div class="message message-out">
                <span class="messsage-text">
                    ${decodeURIComponent(data.message)}
                </span>
            </div>
            `;
            message = messageOut;
        } else {
            const messageIn = `
            <div class="message message-in">
                <span class="message-sender">
                    ${data.email}
                </span> <br>
                <span class="messsage-text">
                    ${decodeURIComponent(data.message)}
                </span>
            </div>
            `;
            message = messageIn;
        }
        const chat = $("#chat");
        chat.append(message).hide().show('slow');
        chat.scrollTop(chat.prop("scrollHeight"));
        if (document.hidden) {
            setTimeout(() => {
                playAlert("pop");
            }, 10);
            document.title = `(${++unreadMsgCount}) Hexora`;
        }
    }
});

// press enter to submit the message
$("#message").keypress(function (e) {
    var key = e.which;
    if (key == 13) {
        $("#btn-send").click();
        return false;
    }
});

// submit a new message
function submitMessage() {
    const message = document.getElementById("message").value;
    if (message) {
        $("#btn-send").html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        socket.emit('messageHandler', {
            message: encodeURI(message),
            chatId,
        }, () => {
            $("#btn-send").html('SEND');
            $("#message").val('');			
        });
    }
}


var button = document.querySelector('#emoji-btn');
var picker = new EmojiButton({
    position: 'top',
    showPreview: false
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
