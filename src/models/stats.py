
class ServerStats:
    client_count = None  # Number of connected clients
    bytes_in = None  # Server bytes in
    bytes_out = None  # Server bytes out


class RemoteClientStats:
    bytes_recv = None  # Number of bytes received
    bytes_sent = None  # Number of bytes sent


class LocalClientStats:
    tuntap_read = None
    tuntap_write = None
    tcpudp_read = None
    tcpudp_write = None
    auth_read = None
