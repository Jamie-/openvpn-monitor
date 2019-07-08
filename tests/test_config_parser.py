import unittest
from util.config_parser import ConfigParser
from util.errors import InvalidConfigError

# Sneaky hack to get PyCharm test runner to pick up data dir
import os
if 'data' not in os.listdir('.'):
    os.chdir('tests')


class TestConfigParser(unittest.TestCase):
    """Test the config file parser monitor.util.config_parser.ConfigParser
    """

    def test_load_defaults(self):
        """Test loaded defaults are as expected.
        """
        cp = ConfigParser()
        cp.load_defaults()
        self.assertEqual(cp.settings, {
            'name': None,
            'geoip_data': None,
            'datetime_format': '%d/%m/%Y %H:%M:%S',
        })
        self.assertEqual(1, len(cp.vpns))
        vpn = cp.vpns[0]
        self.assertEqual(vpn.name, 'Default VPN')
        self.assertEqual(vpn.mgmt_address, 'localhost:5555')
        self.assertEqual(vpn.allow_disconnect, True)

    def test_file_not_exists(self):
        """Test parsing non-existant config file raises and InvalidConfigError.
        """
        cp = ConfigParser()
        with self.assertRaises(InvalidConfigError) as ctx:
            cp.parse_file('this_file_doesnt_exist')
        self.assertEqual('Unable to read config file: this_file_doesnt_exist', str(ctx.exception))

    def test_parse_etc_no_file(self):
        """Test parsing a file from /etc returns False when no expect files are present.
        """
        cp = ConfigParser()
        self.assertFalse(cp.parse_etc_file())

    def test_empty_config(self):
        cp = ConfigParser()
        with self.assertRaises(InvalidConfigError) as ctx:
            cp.parse_file('data/configs/empty_config.conf')
        self.assertEqual("'Monitor' section required, but not found in config", str(ctx.exception))

    def test_missing_monitor(self):
        cp = ConfigParser()
        with self.assertRaises(InvalidConfigError) as ctx:
            cp.parse_file('data/configs/missing_monitor.conf')
        self.assertEqual("'Monitor' section required, but not found in config", str(ctx.exception))

    def test_lowercase_monitor(self):
        cp = ConfigParser()
        with self.assertRaises(InvalidConfigError) as ctx:
            cp.parse_file('data/configs/lowercase_monitor.conf')
        self.assertEqual("'Monitor' section required, but not found in config", str(ctx.exception))

    def test_socket_host_port(self):
        cp = ConfigParser()
        with self.assertRaises(InvalidConfigError) as ctx:
            cp.parse_file('data/configs/socket_host_port.conf')
        self.assertEqual('Must specify either socket or host and port', str(ctx.exception))

    def test_empty_socket(self):
        cp = ConfigParser()
        with self.assertRaises(InvalidConfigError) as ctx:
            cp.parse_file('data/configs/empty_socket.conf')
        self.assertEqual('Must specify either socket or host and port', str(ctx.exception))

    def test_empty_host_port(self):
        cp = ConfigParser()
        with self.assertRaises(InvalidConfigError) as ctx:
            cp.parse_file('data/configs/empty_host_port.conf')
        self.assertEqual('Must specify either socket or host and port', str(ctx.exception))

    def test_no_vpns(self):
        cp = ConfigParser()
        cp.parse_file('data/configs/no_vpns.conf')
        self.assertEqual(cp.settings['name'], 'No VPNs')
        self.assertIsNone(cp.settings['geoip_data'])
        self.assertEqual(cp.settings['datetime_format'], '%d/%m/%Y %H:%M:%S')
        self.assertEqual(len(cp.vpns), 0)

    def test_many_vpns(self):
        cp = ConfigParser.from_file('data/configs/many_vpns.conf')
        self.assertEqual(cp.settings['name'], 'Many VPNs')
        self.assertEqual(cp.settings['geoip_data'], '/asd/asd/a_data_file.whatever')
        self.assertEqual(cp.settings['datetime_format'], '%Y/%d/%m %S:%H:%M')
        self.assertEqual(len(cp.vpns), 4)
        self.assertEqual(
            sorted(['A VPN', 'Another VPN', 'All the VPNs', 'So many !"£$%^&*()\'']),
            sorted([v.name for v in cp.vpns]))
        # A VPN
        vpn = [v for v in cp.vpns if v.name == 'A VPN'][0]
        self.assertEqual(vpn.mgmt_address, '/asd/asd/asd')
        self.assertEqual(vpn.allow_disconnect, False)
        # Another VPN
        vpn = [v for v in cp.vpns if v.name == 'Another VPN'][0]
        self.assertEqual(vpn.mgmt_address, '1.2.3.4:5678')
        self.assertEqual(vpn.allow_disconnect, True)
        # All the VPNs
        vpn = [v for v in cp.vpns if v.name == 'All the VPNs'][0]
        self.assertEqual(vpn.mgmt_address, '/asd/asd.sock')
        self.assertEqual(vpn.allow_disconnect, True)
        # So many !"£$%^&*()'
        vpn = [v for v in cp.vpns if v.name == 'So many !"£$%^&*()\''][0]
        self.assertEqual(vpn.mgmt_address, 'localhost:1234')
        self.assertEqual(vpn.allow_disconnect, False)
