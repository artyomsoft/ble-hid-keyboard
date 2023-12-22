import dbus
import logging

from core.ble_dbus import InvalidArgsException, DBUS_PROP_IFACE, BLUEZ_SERVICE_NAME
from core.bluetooth_utils import enable_discovering

LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"


class LEAdvertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/BLEHidKeyBoard/LEAdvertisement'

    def __init__(self, bus, index, discoverable):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = "peripheral"
        self.local_name = "BLE Keyboard"
        self.service_uuids = ["1812", "180F"]
        self.appearance = 0x03c1
        self.discoverable = discoverable
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = dict()
        properties["Type"] = self.ad_type
        properties["ServiceUUIDs"] = dbus.Array(self.service_uuids, signature='s')
        properties["LocalName"] = dbus.String(self.local_name)
        properties["Appearance"] = dbus.UInt16(self.appearance)
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature='', out_signature='')
    def Release(self):
        logging.info("%s: Released!" % self.path)

    def register_ad_cb(self):
        logging.info("Advertisement registered")
        if self.discoverable:
            logging.info("Enable discovering")
            enable_discovering(self.bus)

    def register_ad_error_cb(self, error):
        print(error.get_dbus_message())
        logging.info("Failed to register advertisement: " + str(error))


def register_advertisement(adapter, bus, discoverable):
    manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), LE_ADVERTISING_MANAGER_IFACE)
    advertisement = LEAdvertisement(bus, 0, discoverable)
    manager.RegisterAdvertisement(advertisement, {},
                                  reply_handler=advertisement.register_ad_cb,
                                  error_handler=advertisement.register_ad_error_cb)





