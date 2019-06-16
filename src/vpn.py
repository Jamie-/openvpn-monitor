import logging
import socket
import re
import contextlib
from util.errors import MonitorError, ParseError
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
    _socket = None
    error = None  # Error if thrown when trying to connect to management interface

    name = None  # VPN name from config
    _release = None  # OpenVPN release string
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
        """
        if self.type == VPNType.IP:
            return '{}:{}'.format(self._mgmt_host, self._mgmt_port)
        else:
            return str(self._mgmt_socket)

    def connect(self):
        """Connect to management interface socket.
        """
        try:
            if self.type == VPNType.IP:
                self._socket = socket.create_connection((self._mgmt_host, self._mgmt_port), timeout=3)

            else:
                self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self._socket.connect(self._mgmt_socket)
            resp = self._socket_recv()
            assert resp.startswith('>INFO'), 'Did not get expected response from interface when opening socket.'
            return True
        except (socket.timeout, socket.error) as e:
            logger.error(e, exc_info=True)
            self.error = str(e)
            return False

    def disconnect(self):
        """Disconnect from management interface socket.
        """
        if self._socket is not None:
            self._socket_send('quit\n')
            self._socket.close()
            self._socket = None

    @property
    def is_connected(self):
        """Determine if management interface socket is connected or not.
        """
        return self._socket != None

    @contextlib.contextmanager
    def connection(self):
        """Create context where management interface socket is open and close when done.
        """
        self.connect()
        try:
            yield
        finally:
            self.disconnect()

    def _socket_send(self, data):
        """Convert data to bytes and send to socket.
        """
        self._socket.send(bytes(data, 'utf-8'))

    def _socket_recv(self):
        """Receive bytes from socket and convert to string.
        """
        return self._socket.recv(4096).decode('utf-8')

    def send_command(self, cmd):
        """Send command to management interface and fetch response.
        """
        logger.debug('Sending cmd: %s', cmd.strip())
        self._socket_send(cmd + '\n')
        if cmd.startswith('kill') or cmd.startswith('client-kill'):
            return
        resp = self._socket_recv()
        if cmd.strip() != 'load-stats':
            while not resp.strip().endswith('END'):
                resp += self._socket_recv()
        logger.debug('Cmd response: %s', resp)
        return resp

    # Interface commands and parsing

    def _get_version(self):
        """Get OpenVPN version from socket.
        """
        raw = self.send_command('version')
        for line in raw.splitlines():
            if line.startswith('OpenVPN Version'):
                return line.replace('OpenVPN Version: ', '')
        raise ParseError('Unable to get OpenVPN version, no matches found in socket response.')

    @property
    def release(self):
        """OpenVPN release string.
        """
        if self._release is None:
            self._release = self._get_version()
        return self._release

    @property
    def version(self):
        """OpenVPN version number.
        """
        release = self.release()
        if release is None:
            return None
        match = re.search('OpenVPN (?P<version>\d+.\d+.\d+)', release)
        if not match:
            raise ParseError('Unable to parse version from release string.')
        return match.group('version')
