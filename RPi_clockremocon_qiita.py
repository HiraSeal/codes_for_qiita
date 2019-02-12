# -*- coding: utf-8 -*-

from bluepy.btle import Peripheral
import bluepy.btle as btle
import binascii
import sys

devaddr =  "xx:xx:xx:xx:xx:xx" # BLE ペリフェラルのアドレス

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data): # notify callback
        sys.stdout.write( data )

class MyPeripheral(Peripheral):
    def __init__(self, addr):
        Peripheral.__init__(self, addr, addrType="random")

def main():
    # 初期設定
    perip = MyPeripheral(devaddr)
    perip.setDelegate(MyDelegate(btle.DefaultDelegate))

    perip.writeCharacteristic(0x0001, "\x01\x00", True) # notifyを有効にする # 0x0001 は自分で調べたハンドルで
    perip.writeCharacteristic(0x0004, "2001/01/01 00:00:01\r\n") # 0x0004 は自分で調べたハンドルで

    # データを受信し続ける
    while True:
        perip.waitForNotifications(1.0)

if __name__ == "__main__":
    main()
