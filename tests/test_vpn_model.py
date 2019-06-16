import unittest
from unittest.mock import patch
from vpn import VPN, VPNType
from util.errors import MonitorError, ParseError


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

    @patch('vpn.VPN.send_command')
    def test__get_version(self, mock_send_command):
        vpn = VPN(host='localhost', port=1234)
        mock_send_command.return_value = """
OpenVPN Version: OpenVPN 2.4.4 x86_64-pc-linux-gnu [SSL (OpenSSL)] [LZO] [LZ4] [EPOLL] [PKCS11] [MH/PKTINFO] [AEAD] built on Sep  5 2018
Management Version: 1
END
        """
        self.assertEqual(vpn._get_version(),
                         'OpenVPN 2.4.4 x86_64-pc-linux-gnu [SSL (OpenSSL)] [LZO] [LZ4] [EPOLL] [PKCS11] [MH/PKTINFO] [AEAD] built on Sep  5 2018')
        mock_send_command.assert_called_once_with('version')
        mock_send_command.reset_mock()
        mock_send_command.return_value = ""
        with self.assertRaises(ParseError) as ctx:
            vpn._get_version()
        self.assertEqual('Unable to get OpenVPN version, no matches found in socket response.', str(ctx.exception))
        mock_send_command.assert_called_once_with('version')
        mock_send_command.reset_mock()
        mock_send_command.return_value = """
Management Version: 1
END
        """
        with self.assertRaises(ParseError) as ctx:
            vpn._get_version()
        self.assertEqual('Unable to get OpenVPN version, no matches found in socket response.', str(ctx.exception))
        mock_send_command.assert_called_once_with('version')
        mock_send_command.reset_mock()

    @patch('vpn.VPN._get_version')
    def test_release(self, mock_get_version):
        vpn = VPN(host='localhost', port=1234)
        self.assertIsNone(vpn._release)
        release_string = 'OpenVPN 2.4.4 x86_64-pc-linux-gnu [SSL (OpenSSL)] [LZO] [LZ4] [EPOLL] [PKCS11] [MH/PKTINFO] [AEAD] built on Sep  5 2018'
        mock_get_version.return_value = release_string
        self.assertEqual(vpn.release, release_string)
        self.assertEqual(vpn._release, release_string)
        mock_get_version.assert_called_once_with()
        mock_get_version.reset_mock()
        vpn._release = 'asd'
        self.assertEqual(vpn.release, 'asd')
        mock_get_version.assert_not_called()

    @patch('vpn.VPN.release')
    def test_version(self, mock_release):
        vpn = VPN(host='localhost', port=1234)
        mock_release.return_value = 'OpenVPN 2.4.4 x86_64-pc-linux-gnu [SSL (OpenSSL)] [LZO] [LZ4] [EPOLL] [PKCS11] [MH/PKTINFO] [AEAD] built on Sep  5 2018'
        self.assertEqual(vpn.version, '2.4.4')
        mock_release.assert_called_once_with()
        mock_release.reset_mock()
        mock_release.return_value = 'OpenVPN 1.2.3 x86_64-pc-linux-gnu [SSL (OpenSSL)] [LZO] [LZ4] [EPOLL] [PKCS11] [MH/PKTINFO] [AEAD] built on Sep  5 2018'
        self.assertEqual(vpn.version, '1.2.3')
        mock_release.assert_called_once_with()
        mock_release.reset_mock()
        mock_release.return_value = 'OpenVPN 11.22.33 x86_64-pc-linux-gnu [SSL (OpenSSL)] [LZO] [LZ4] [EPOLL] [PKCS11] [MH/PKTINFO] [AEAD] built on Sep  5 2018'
        self.assertEqual(vpn.version, '11.22.33')
        mock_release.assert_called_once_with()
        mock_release.reset_mock()
        mock_release.return_value = None
        self.assertIsNone(vpn.version)
        mock_release.assert_called_once_with()
        mock_release.reset_mock()
        mock_release.return_value = 'asd'
        with self.assertRaises(ParseError) as ctx:
            vpn.version()
        self.assertEqual('Unable to parse version from release string.', str(ctx.exception))
        mock_release.assert_called_once_with()
