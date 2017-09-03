import unittest
from unittest import mock
from io import StringIO
import os, sys

sys.modules['NetworkManager'] = mock.MagicMock()
import pifi.nm_helper as nm_helper

class NMHelperTests(unittest.TestCase):

    def test_managed_wifi_devices_no_devices(self):
        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': list()})

        generator = nm_helper.managedWifiDevices(NetworkManager=nm)
        with self.assertRaises(StopIteration):
            next(generator)

    def test_managed_wifi_devices_no_wifi_devices(self):
        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 0})

        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': [dev],
                     'NM_DEVICE_TYPE_WIFI' : 2
                    })

        generator = nm_helper.managedWifiDevices(NetworkManager=nm)
        with self.assertRaises(StopIteration):
            next(generator)

    def test_managed_wifi_devices_one_wifi_device(self):
        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 2})

        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': [dev],
                             'NM_DEVICE_TYPE_WIFI' : 2
                            })

        generator = nm_helper.managedWifiDevices(NetworkManager=nm)

        self.assertEqual(dev, next(generator))

        with self.assertRaises(StopIteration):
            next(generator)

    def test_managed_ap_devices_no_devices(self):
        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': list(),
                             'NM_DEVICE_TYPE_WIFI' : 2
                            })

        generator = nm_helper.managedWifiDevices(NetworkManager=nm)

        with self.assertRaises(StopIteration):
            next(generator)

    def test_managed_ap_devices_no_ap_devices(self):
        wi_dev = mock.MagicMock()
        wi_dev.configure_mock(**{'WirelessCapabilities' : 200})

        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 2,
                               'SpecificDevice.return_value': wi_dev
                             })

        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': [dev],
                             'NM_DEVICE_TYPE_WIFI' : 2,
                             'NM_WIFI_DEVICE_CAP_AP' : 100
                            })

        generator = nm_helper.managedAPCapableDevices(NetworkManager=nm)

        with self.assertRaises(StopIteration):
            next(generator)

    def test_managed_ap_devices_one_ap_device(self):
        wi_dev = mock.MagicMock()
        wi_dev.configure_mock(**{'WirelessCapabilities' : 100})

        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 2,
                               'SpecificDevice.return_value': wi_dev
                             })

        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': [dev],
                             'NM_DEVICE_TYPE_WIFI' : 2,
                             'NM_WIFI_DEVICE_CAP_AP' : 100
                            })

        generator = nm_helper.managedAPCapableDevices(NetworkManager=nm)

        self.assertEqual(dev, next(generator))

        with self.assertRaises(StopIteration):
            next(generator)

    def test_managed_ap_devices_multiple_ap_devices(self):
        wi_dev = mock.MagicMock()
        wi_dev.configure_mock(**{'WirelessCapabilities' : 100})

        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 2,
                               'SpecificDevice.return_value': wi_dev
                             })

        non_wifi_dev = mock.MagicMock()
        non_wifi_dev.configure_mock(**{'DeviceType' : 0})

        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': [dev, non_wifi_dev, dev],
                             'NM_DEVICE_TYPE_WIFI' : 2,
                             'NM_WIFI_DEVICE_CAP_AP' : 100
                            })

        generator = nm_helper.managedAPCapableDevices(NetworkManager=nm)

        self.assertEqual(dev, next(generator))
        self.assertEqual(dev, next(generator))

        with self.assertRaises(StopIteration):
            next(generator)

    def test_seen_SSIDs_empty(self):
        wi_dev = mock.MagicMock()
        wi_dev.configure_mock(**{'GetAccessPoints.return_value': list()})

        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 2,
                               'SpecificDevice.return_value': wi_dev
                             })
        generator = nm_helper.seenSSIDs([dev])
        with self.assertRaises(StopIteration):
            next(generator)

    def test_seen_SSIDs_one(self):
        wi_dev = mock.MagicMock()
        wi_dev.configure_mock(**{'GetAccessPoints.return_value': 
                                  [mock.MagicMock(**{'Ssid' : 'Foo'})]
                                })

        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 2,
                               'SpecificDevice.return_value': wi_dev
                             })
        generator = nm_helper.seenSSIDs([dev])

        self.assertEqual('Foo', next(generator))
        with self.assertRaises(StopIteration):
            next(generator)

    def test_seen_SSIDs_multiple(self):
        wi_dev = mock.MagicMock()
        wi_dev.configure_mock(**{'GetAccessPoints.return_value': 
                                  [mock.MagicMock(**{'Ssid' : 'Foo'}),
                                   mock.MagicMock(**{'Ssid' : 'Bar'})]
                                })

        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 2,
                               'SpecificDevice.return_value': wi_dev
                             })
        generator = nm_helper.seenSSIDs([dev])

        self.assertEqual('Foo', next(generator))
        self.assertEqual('Bar', next(generator))
        with self.assertRaises(StopIteration):
            next(generator)

    def test_seen_SSIDs_multiple_multiple_devices(self):
        wi_dev = mock.MagicMock()
        wi_dev.configure_mock(**{'GetAccessPoints.return_value': 
                                  [mock.MagicMock(**{'Ssid' : 'Foo'}),
                                   mock.MagicMock(**{'Ssid' : 'Bar'})]
                                })

        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 2,
                               'SpecificDevice.return_value': wi_dev
                             })
        generator = nm_helper.seenSSIDs([dev, dev])

        self.assertEqual('Foo', next(generator))
        self.assertEqual('Bar', next(generator))
        self.assertEqual('Foo', next(generator))
        self.assertEqual('Bar', next(generator))
        with self.assertRaises(StopIteration):
            next(generator)

    def test_select_connection_none_availible(self):
        with self.assertRaises(ValueError):
            nm_helper.selectConnection(list())

    def test_select_connection_one_availible(self):
        ap = mock.MagicMock(**{'Strength' : 50})
        ret_ap, con = nm_helper.selectConnection([(ap, 1)])

        self.assertEqual(ret_ap, ap)
        self.assertIs(con, 1)

    def test_select_connection_multiple_availible(self):
        ap_strong = mock.MagicMock(**{'Strength' : 90})
        ap_mid = mock.MagicMock(**{'Strength' : 70})
        ap_weak = mock.MagicMock(**{'Strength' : 10})
        ret_ap, con = nm_helper.selectConnection([(ap_strong, 1), 
                                                  (ap_mid, 2), 
                                                  (ap_weak, 3)]
                                                )

        self.assertEqual(ret_ap, ap_strong)
        self.assertEqual(con, 1)

        ret_ap, con = nm_helper.selectConnection([(ap_mid, 1), 
                                                  (ap_strong, 2), 
                                                  (ap_weak, 3)]
                                                )

        self.assertEqual(ret_ap, ap_strong)
        self.assertEqual(con, 2)

        ret_ap, con = nm_helper.selectConnection([(ap_mid, 1), 
                                                  (ap_weak, 2), 
                                                  (ap_strong, 3)]
                                                )

        self.assertEqual(ret_ap, ap_strong)
        self.assertEqual(con, 3)


    def test_availible_connections_no_aps(self):
        wi_dev = mock.MagicMock(**{'GetAccessPoints.return_value': list()})
        dev = mock.MagicMock(**{'SpecificDevice.return_value': wi_dev})

        generator = nm_helper.availibleConnections(dev, list()) 
        with self.assertRaises(StopIteration):
            next(generator)

    def test_availible_connections_no_connections(self):
        ap = mock.MagicMock(**{'Ssid': 'Foo'})
        wi_dev = mock.MagicMock(**{'GetAccessPoints.return_value': [ap]})
        dev = mock.MagicMock(**{'SpecificDevice.return_value': wi_dev})

        generator = nm_helper.availibleConnections(dev, list()) 
        with self.assertRaises(StopIteration):
            next(generator)

    def test_availible_connections_no_matching_connections(self):
        ap1 = mock.MagicMock(**{'Ssid': 'Foo'})
        ap2 = mock.MagicMock(**{'Ssid': 'Bar'})
        wi_dev = mock.MagicMock(**{'GetAccessPoints.return_value': [ap1, ap2]})
        dev = mock.MagicMock(**{'SpecificDevice.return_value': wi_dev})
        cons = [{'802-11-wireless': {'ssid' : 'Baz'}}, {'802-11-wireless': {'ssid' : 'Qux'}}]

        generator = nm_helper.availibleConnections(dev, cons) 
        with self.assertRaises(StopIteration):
            next(generator)

    def test_availible_connections_one_connection(self):
        ap1 = mock.MagicMock(**{'Ssid': 'Foo'})
        ap2 = mock.MagicMock(**{'Ssid': 'Bar'})
        ap3 = mock.MagicMock(**{'Ssid': 'Baz'})
        wi_dev = mock.MagicMock(**{'GetAccessPoints.return_value': [ap1, ap2, ap3]})
        dev = mock.MagicMock(**{'SpecificDevice.return_value': wi_dev})
        cons = [{'802-11-wireless': {'ssid' : 'Baz'}}, {'802-11-wireless': {'ssid' : 'Qux'}}]

        generator = nm_helper.availibleConnections(dev, cons)
        self.assertEqual((ap3, cons[0]), next(generator))
        with self.assertRaises(StopIteration):
            next(generator)

    def test_availible_connections_multiple_connections(self):
        ap1 = mock.MagicMock(**{'Ssid': 'Foo'})
        ap2 = mock.MagicMock(**{'Ssid': 'Bar'})
        ap3 = mock.MagicMock(**{'Ssid': 'Baz'})
        wi_dev = mock.MagicMock(**{'GetAccessPoints.return_value': [ap1, ap2, ap3]})
        dev = mock.MagicMock(**{'SpecificDevice.return_value': wi_dev})
        cons = [{'802-11-wireless': {'ssid' : 'Baz'}}, {'802-11-wireless': {'ssid' : 'Foo'}}]

        # Use list and assertIn beacuse we don't care about order
        output = list(nm_helper.availibleConnections(dev, cons))
        self.assertIn((ap3, cons[0]), output)
        self.assertIn((ap1, cons[1]), output)
        self.assertEqual(len(output), 2)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
