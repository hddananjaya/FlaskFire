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
socket.on('{{ chatid }}', (data) => {
    if (data && data.hasOwnProperty('message')) {
        const chatText = $("#chatview").val()
        $("#chatview").val(`${chatText}\n${data['message']}`);
        var $textarea = $('#chatview');
        $textarea.scrollTop($textarea[0].scrollHeight);
        if (document.hidden) {
            setTimeout(() => {
                playAlert("pop");
            }, 10);
            document.title = `(${++unreadMsgCount}) Hexora`;
        }
    }
});

var textarea = document.getElementById('chatview');
textarea.scrollTop = textarea.scrollHeight;
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
            message,
            chatId: '{{ chatid }}'
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
