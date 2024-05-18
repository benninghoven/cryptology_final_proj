def PeerNameToStringName(conn):
    peername = conn.getpeername()
    return f"{peername[0]}:{peername[1]}"
