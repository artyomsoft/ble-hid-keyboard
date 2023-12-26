# ble-hid-keyboard
This is the application which transform the device running Linux into the Bluetooth Low Energy keyboard.

The application is tested on Debian based Linux distributions and Raspberry Pi OS with BlueZ 5.55 and above.

## How to use
1. Install required packages:
```
$ sudo apt install libdbus-1-3 libdbus-1-dev libcairo2-dev libxt-dev libgirepository1.0-dev git mc
```
2. Get source code of application to your Linux distribution
```
$ git clone https://github.com/artyomsoft/ble-hid-keyboard.git
```
3. Switch directory to ble-hid-keyboard
```   
$ cd ble-hid-keyboard
```
5. Install systemd service ble-hid-keyboard.
```
$ sudo ./install.sh
```
6. Connect to USB port USB usb keyboard.
  
7. Device running service must be visible to other devices as BLE Keyboars

8. Connect from the computer or the mobile phone to device named BLE Keyboard
