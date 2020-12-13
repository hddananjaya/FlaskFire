import { NotificationType } from '../constants/constants.js';
import { getProtocol } from '../utils/common.js';

class ChatService {

  constructor() {
    this.socket = io.connect(`${getProtocol()}${location.hostname}:${location.port}`);    
    this.socket.on('connect', () => {
      this.emitNotification(NotificationType.JOIN);
    });

    this.socket.on('disconnect', () => {
      this.emitNotification(NotificationType.EXIT);
    });
  }

  emitNotification = (type, callback) => {
    this.socket.emit('notificationGateway', {
      chatId,
      type,
    }, () => {
      if (callback) {
        callback();
      }
    });
  }

  emitMessage = (message, callback) => {
    this.socket.emit('messageGateway', {
      message: encodeURI(message),
      chatId,
    }, () => {
      if (callback) {
        callback();
      }
    });
  }

  getNotifications = (callback) => {
    this.socket.on(`${chatId}.NOTIFICATION`, (notification) => {
      if (!notification || !notification.hasOwnProperty('type')) {
          return;
      }
      if (email === notification.email) {
          return;
      }
      callback(notification);
    });
  }

  getMessages = (callback) => {
    this.socket.on(`${chatId}.MESSAGE`, (message) => {
      if (message && message.hasOwnProperty('message')) {
          callback(message)
      }
    });
  }

}

export default ChatService;