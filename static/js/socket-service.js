let protocol;
let unreadMsgCount = 0;
const chat = $("#chat");
const imageInput = $("#image-input"); 
const userControls = $("#user-controls :input");

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

const bbParser = (text) => {
    const imgRe = /^\[img\](?<imgData>[/;,=+A-Za-z0-9:]*)\[\/img\]$/;
    const image = text.match(imgRe);
    if (image) {
        const imageTag = `<img class="img-msg" src="${image.groups.imgData}">`;
        return imageTag;
    } else {
        return text;
    }
}

var socket = io.connect(`${protocol}${location.hostname}:${location.port}`);

setInterval(() => {
    $(".keyevents").remove();
}, 2000);

socket.on(`${chatId}.NOTIFICATION`, (notification) => {
    if (!notification || !notification.hasOwnProperty('type')) {
        return;
    }
    if (email === notification.email) {
        return;
    }
    const events = `
    <div class="message message-keyevents keyevents">
        <span class="messsage-text">
            ${notification.email} is typing...
        </span>
    </div>
    `;
    $(".keyevents").remove();
    chat.append(events)
    chat.scrollTop(chat.prop("scrollHeight"));
})

socket.on(`${chatId}.MESSAGE`, (data) => {
    if (data && data.hasOwnProperty('message')) {
        $(".keyevents").remove();
        let message;
        if (email === data.email) {
            const messageOut = `
            <div class="message message-out">
                <span class="messsage-text">
                    ${bbParser(decodeURIComponent(data.message))}
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
                    ${bbParser(decodeURIComponent(data.message))}
                </span>
            </div>
            `;
            message = messageIn;
        }
        chat.append(message);
        chat.scrollTop(chat.prop("scrollHeight"));
        if (document.hidden) {
            setTimeout(() => {
                playAlert("pop");
            }, 10);
            document.title = `(${++unreadMsgCount}) Hexora Web`;
        }
    }
});

// press enter to submit the message
$("#message").keypress(function (e) {
    emitNotification("KEYPRESS");
    var key = e.which;
    if (key == 13) {
        $("#btn-send").click();
        return false;
    }
});

// submit a new message
function submitMessage() {
    const message = document.getElementById("message").value;
    if (message && message.trim()) {
        $("#btn-send").html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        emitMessage(message, () => {
            $("#btn-send").html('SEND');
            $("#message").val('');		
        })
    }
}

const emitNotification = (type, callback) => {
    socket.emit('notificationGateway', {
        chatId,
        type,
    }, () => {
        if (callback) {
            callback();
        }
    });
}

const emitMessage = (message, callback) => {
    socket.emit('messageGateway', {
        message: encodeURI(message),
        chatId,
    }, () => {
        if (callback) {
            callback();
        }
    });
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


uploadFile = () => {
    imageInput.click();
}

$('#image-input').on('change', () => {
    const fileReader = new FileReader();
    fileReader.onload = () => {
    const data = fileReader.result;
    userControls.attr("disabled", true);;
    emitMessage(`[img]${data}[/img]`, () => {
        userControls.attr("disabled", false);
    })
    };
    if (imageInput.prop('files').length > 0) {
        const file = imageInput.prop('files')[0];
        fileReader.readAsDataURL(file);
    }
});