from peernametostringname import PeerNameToStringName
from states import STATES


class ActiveClient:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr

        self.peername = PeerNameToStringName(self.conn)

        self.state = STATES.INITIAL_MENU
        self.thread = None
        self.username = None
        self.password = None
        self.logged_in = False
        self.chatting_with = None

        self.current_state = None
        self.next_state = None

        self.public_key = None
