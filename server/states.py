from enum import Enum, auto

class STATES(Enum):
    INITIAL_MENU = auto()
    LOGIN_USERNAME = auto()
    LOGIN_PASSWORD = auto()
    REGISTER_USERNAME = auto()
    REGISTER_PASSWORD = auto()
    REENTER_PASSWORD = auto()
    MAIN_MENU = auto()
    VIEW_DIRECT_MESSAGES = auto()
    OPEN_DIRECT_MESSAGE = auto()
    STARTING_A_NEW_CHAT = auto()
    PING_A_USER = auto()
