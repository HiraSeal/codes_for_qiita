# -*- coding: utf-8 -*-
from bluepy.btle import Peripheral
import bluepy.btle as btle
import binascii
import time
import sys
import datetime
import subprocess
import struct

exflag = False #無限ループから抜ける判定用：ボタン長押しで抜けるようにしている。
# BLE ペリフェラル= micro:bit のBLEアドレス, 複数あるのでコマンドパラメーターで切り替えられるようにしている。

list_dev = [ "C4:A7:19:XX:XX:XX", "C4:A7:19:YY:YY:YY" ]

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data): # notify callback: cHandle で何の情報かを見分けて処理分岐
        global exflag
        c_data = binascii.b2a_hex(data)

        if cHandle == 0x27: # 加速度センサー
            accX = struct.unpack('h', data[0:2] )[0]
            accY = struct.unpack('h', data[2:4] )[0]
            accZ = struct.unpack('h', data[4:6] )[0]
            strX = "Flat"
            strY = "Flat"
            if accX > 700: strX = "Plus"
            if accX < -700: strX = "Minus"
            if accY > 700: strY = "Plus"
            if accY < -700: strY = "Minus"

            print( "%s: %d, %d, %d : %s %s " % (c_data, accX, accY, accZ, strX, strY) )
            return

        if cHandle == 0x2d: # left button
            b = "button1"
            if data[0] == "\x02": exflag = True # long push to exit
        if cHandle == 0x30: # right button
            b = "button2"
            if data[0] == "\x02": exflag = True # long push to exit
            if data[0] == "\x01":
                subprocess.call(['/usr/bin/python', '/home/pi/TYBLE/ntptime1.py', '2', 'SingleDivert'] )
                print( "Call SingleDivert" )

        print( "%s: %s" % (b,c_data) )

class MyPeripheral(Peripheral):
    def __init__(self, addr):
        Peripheral.__init__(self, addr, addrType="random")

def main():
    args = sys.argv
    if ( len(args) <= 1 or (args[1] != "1" and args[1] != "2") ) :
        print( "Bad Param: ", args[1] )
        return

    # 初期設定
    perip = MyPeripheral(list_dev[int(args[1])-1]) # コマンドラインパラメーターで 1 or 2 を指定するので、1引いてlist_dev の添え字に
    perip.setDelegate(MyDelegate(btle.DefaultDelegate))

    # device name, serial number
    devname = perip.readCharacteristic(0x0003)
    print( "Device Name: %s" % devname )
    serialnum = perip.readCharacteristic(0x0017)
    print( "Serial Number: %s" % serialnum )

    # 温度を表示してみる(気温より高く出るのでそのまま表示してもあまり意味が無い）
    val0045 = perip.readCharacteristic(0x0045) # 1バイトのバイト列なのだが文字列にされてしまう
    print( "温度: %d " % int(binascii.b2a_hex(val0045[0]) ,16)) # python の型変換よくわからん

    # LED
    print( "LED操作" )
    perip.writeCharacteristic(0x003e,"\x01\x02\x04\x08\x1f" ) # 5x5 LED の光る場所を 5bit x 5つ16六進数で指定
    """
    00001 = \x01
    00010 = \x02
    00100 = \x04
    01000 = \x08
    11111 = \x1f   という意味
    """
    time.sleep(1)

    # 文字列表示
    print( "micro:bit に文字列'ABC'を表示" )
    perip.writeCharacteristic(0x0040, "ABC")

   # ABCを表示完了しなくても次に進むので、表示途中でもボタンなどの通知は来る

    # ボタン notify を要求
    perip.writeCharacteristic(0x002e, "\x01\x00", True) # button A notifyを有効にする
    perip.writeCharacteristic(0x0031, "\x01\x00", True) # button B notifyを有効にする

    # 加速度 notify 間隔を指定して、通知要求
    perip.writeCharacteristic(0x002a, "\x50\x00", True) # 80ms ごとに通知 #デフォルトは 20ms
    perip.writeCharacteristic(0x0028, "\x01\x00", True) # 通知有効化


    # データを受信し続ける
    print( "Notification を待機。A or B ボタン長押しでプログラム終了")
    while exflag == False:
        if perip.waitForNotifications(1.0):
            continue
        #sys.stdout.write( "." )

if __name__ == "__main__":
    main()

