from peernametostringname import PeerNameToStringName
from states import STATES


class ActiveClient:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.name = PeerNameToStringName(self.conn)
        self.state = STATES["initial_menu"]
        self.thread = None
        self.username = None
        self.password = None
        self.logged_in = False
        self.chatting_with = None
