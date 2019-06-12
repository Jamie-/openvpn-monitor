import os
import logging
import configparser
from util.errors import InvalidConfigError
from vpn import VPN

logger = logging.getLogger(__name__)


class ConfigParser:
    locations = [
        '/etc/openvpn-monitor.conf',
        '/etc/openvpn/openvpn-monitor.conf',
        '/etc/openvpn/monitor.conf',
    ]

    def __init__(self):
        self.settings = {}
        self.vpns = []

    @staticmethod
    def from_file(filename):
        """Create and return a ConfigParser object from file.
        """
        cp = ConfigParser()
        cp.parse_file(filename)
        return cp

    def _parse_file(self, filename):
        config = configparser.RawConfigParser()
        logger.info('Parsing config file: %s', filename)
        contents = config.read(filename)
        if not contents:
            raise InvalidConfigError('Unable to read config file: {}'.format(filename))
        if 'Monitor' not in config.sections():
            raise InvalidConfigError("'Monitor' section required, but not found in config")
        # Parse 'Monitor' section
        monitor = config['Monitor']
        self.settings['name'] = monitor.get('name')
        self.settings['geoip_data'] = monitor.get('geoip_data')
        self.settings['datetime_format'] = monitor.get('datetime_format', '%d/%m/%Y %H:%M:%S')
        # Parse other (VPN) sections
        for s in [s for s in config.sections() if s != 'Monitor']:
            section = config[s]
            # Compulsory
            host = section.get('host')
            try:
                port = section.getint('port')
            except ValueError:
                port = None
            socket = section.get('socket')
            if (socket and host) or (socket and port) or (not socket and not host and not port):
                raise InvalidConfigError('Must specify either socket or host and port')
            if socket:
                vpn = VPN(socket=socket)
            else:
                vpn = VPN(host=host, port=port)
            vpn.name = s
            # Optional
            try:
                vpn.allow_disconnect = section.getboolean('allow_disconnect', True)
            except configparser.NoOptionError:
                pass
            # Add VPN
            self.vpns.append(vpn)

    def parse_file(self, filename):
        """Parse a given config file.
        """
        self._parse_file(filename)

    def parse_etc_file(self):
        """Find config from one of listed locations in /etc and parse.
        Returns True if file found and parsed, returns False if no file is found.
        """
        for l in self.locations:
            if os.path.isfile(l):
                self._parse_file(l)
                return True
        return False

    def load_defaults(self):
        """Load default config options.
        """
        # Settings
        self.settings = {}
        self.settings['name'] = None
        self.settings['geoip_data'] = None
        self.settings['datetime_format'] = '%d/%m/%Y %H:%M:%S'
        # VPN(s)
        self.vpns = []
        vpn = VPN(host='localhost', port=5555)
        vpn.name = 'Default VPN'
        vpn.allow_disconnect = True
        self.vpns.append(vpn)
