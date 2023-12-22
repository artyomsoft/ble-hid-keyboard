set -x
systemctl disable ble-hid-keyboard
systemctl stop ble-hid-keyboard.service
rm /usr/lib/systemd/system/ble-hid-keyboard.service
rm -r /usr/lib/ble-hid-keyboard
