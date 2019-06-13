import unittest
from vpn import VPN, VPNType
from util.errors import MonitorError


class TestVPNModel(unittest.TestCase):
    """Test the config file parser monitor.util.config_parser.ConfigParser
    """

    def test_host_port_socket(self):
        with self.assertRaises(MonitorError) as ctx:
            VPN(host='localhost', port=1234, socket='file.sock')
        self.assertEqual('Must specify either socket or host and port', str(ctx.exception))

    def test_host_port(self):
        vpn = VPN(host='localhost', port=1234)
        self.assertEqual(vpn._mgmt_host, 'localhost')
        self.assertEqual(vpn._mgmt_port, 1234)
        self.assertIsNone(vpn._mgmt_socket)
        self.assertEqual(vpn.type, VPNType.IP)
        self.assertEqual(vpn.mgmt_address, 'localhost:1234')

    def test_socket(self):
        vpn = VPN(socket='file.sock')
        self.assertEqual(vpn._mgmt_socket, 'file.sock')
        self.assertIsNone(vpn._mgmt_host)
        self.assertIsNone(vpn._mgmt_port)
        self.assertEqual(vpn.type, VPNType.UNIX_SOCKET)
        self.assertEqual(vpn.mgmt_address, 'file.sock')

    def test_anchor(self):
        vpn = VPN(host='localhost', port=1234)
        vpn.name = 'Test VPN'
        self.assertEqual(vpn.anchor, 'test_vpn')
        vpn.name = 'asd_asd'
        self.assertEqual(vpn.anchor, 'asd_asd')
