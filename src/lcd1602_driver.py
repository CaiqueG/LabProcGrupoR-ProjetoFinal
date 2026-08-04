#!/usr/bin/env python3
import time

try:
    import smbus
except ImportError:
    import smbus2 as smbus


class CharLCD1602(object):
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.BLEN = 1
        self.PCF8574_address = 0x27
        self.PCF8574A_address = 0x3f
        self.LCD_ADDR = self.PCF8574_address

    def write_word(self, addr, data):
        temp = data
        if self.BLEN == 1:
            temp |= 0x08
        else:
            temp &= 0xF7
        self.bus.write_byte(addr, temp)

    def send_command(self, comm):
        buf = comm & 0xF0
        buf |= 0x04
        self.write_word(self.LCD_ADDR, buf)
        time.sleep(0.002)
        buf &= 0xFB
        self.write_word(self.LCD_ADDR, buf)
        buf = (comm & 0x0F) << 4
        buf |= 0x04
        self.write_word(self.LCD_ADDR, buf)
        time.sleep(0.002)
        buf &= 0xFB
        self.write_word(self.LCD_ADDR, buf)

    def send_data(self, data):
        buf = data & 0xF0
        buf |= 0x05
        self.write_word(self.LCD_ADDR, buf)
        time.sleep(0.002)
        buf &= 0xFB
        self.write_word(self.LCD_ADDR, buf)
        buf = (data & 0x0F) << 4
        buf |= 0x05
        self.write_word(self.LCD_ADDR, buf)
        time.sleep(0.002)
        buf &= 0xFB
        self.write_word(self.LCD_ADDR, buf)

    def i2c_scan(self):
        import subprocess
        cmd = "i2cdetect -y 1 |awk 'NR>1 {$1=\"\";print}'"
        result = subprocess.check_output(cmd, shell=True).decode()
        result = result.replace("\n", "").replace(" --", "")
        return result.split(" ")

    def init_lcd(self, addr=None, bl=1):
        i2c_list = self.i2c_scan()
        if addr is None:
            if "27" in i2c_list:
                self.LCD_ADDR = self.PCF8574_address
            elif "3f" in i2c_list:
                self.LCD_ADDR = self.PCF8574A_address
            else:
                raise IOError("Endereço I2C 0x27 ou 0x3f não encontrado.")
        else:
            self.LCD_ADDR = addr
            if str(hex(addr)).strip("0x") not in i2c_list:
                raise IOError(f"Endereço I2C {hex(addr)} não encontrado.")
        self.BLEN = bl
        try:
            self.send_command(0x33)
            time.sleep(0.005)
            self.send_command(0x32)
            time.sleep(0.005)
            self.send_command(0x28)
            time.sleep(0.005)
            self.send_command(0x0C)
            time.sleep(0.005)
            self.send_command(0x01)
            self.bus.write_byte(self.LCD_ADDR, 0x08)
        except Exception:
            return False
        return True

    def clear(self):
        self.send_command(0x01)

    def write(self, x, y, texto):
        x = 0 if x < 0 else min(x, 15)
        y = 0 if y < 0 else min(y, 1)
        addr = 0x80 + 0x40 * y + x
        self.send_command(addr)
        for ch in texto:
            self.send_data(ord(ch))
