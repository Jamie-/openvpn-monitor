import logging
from util.errors import MonitorError
from models.state import ServerState
from models.stats import ServerStats

logger = logging.getLogger(__name__)


class VPNType:
    IP = 'ip'
    UNIX_SOCKET = 'socket'


class VPN:
    _mgmt_host = None  # Management interface host
    _mgmt_port = None  # Management interface port
    _mgmt_socket = None  # Management interface UNIX socket
    _type = None  # VPNType object to choose between IP (host:port) and socket
    error = None  # Error if thrown when trying to connect to management interface
    name = None  # VPN name from config
    release = None  # OpenVPN release string
    version = None  # OpenVPN version
    state = ServerState()  # State object
    stats = ServerStats()  # Stats object
    sessions = []  # Client sessions
    allow_disconnect = False  # Allow disconnect via API

    def __init__(self,
                 host=None,
                 port=None,
                 socket=None):
        if (socket and host) or (socket and port) or (not socket and not host and not port):
            raise MonitorError('Must specify either socket or host and port')
        if socket:
            self._mgmt_socket = socket
            self._type = VPNType.UNIX_SOCKET
        else:
            self._mgmt_host = host
            self._mgmt_port = port
            self._type = VPNType.IP

    @property
    def type(self):
        """Get VPNType object for this VPN.
        """
        return self._type

    @property
    def anchor(self):
        """Get VPN name as an HTML anchor compatible string.
        """
        return self.name.lower().replace(' ', '_')

    @property
    def mgmt_address(self):
        """Get address of management interface.
        1"""
        if self.type == VPNType.IP:
            return '{}:{}'.format(self._mgmt_host, self._mgmt_port)
        else:
            return str(self._mgmt_socket)
