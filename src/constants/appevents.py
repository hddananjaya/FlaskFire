from enum import Enum

class HexoraEvents(Enum):
    MESSAGE = "MESSAGE"
    NOTIFCATION = "NOTIFICATION"

class NotificationType(Enum):
    KEYPRESS = "KEYPRESS"
    JOIN = "JOIN"
    EXIT = "EXIT"