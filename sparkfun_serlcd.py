#!/usr/bin/python3

import os
import time
import datetime
import math
import threading
from smbus import SMBus

class SerLCD:
	"""SparkFun SerLCD"""

	#I2C Slave Address
	I2C_ADDRESS = 0x72
	#Display
	MAX_ROWS = 4
	MAX_COLUMNS = 20
	#Command Char
	SPECIAL_COMMAND = 254
	SETTING_COMMAND = 0x7C
	#Commands
	CLEAR_COMMAND = 0x2D
	CONTRAST_COMMAND = 0x18
	ADDRESS_COMMAND = 0x19
	SET_RGB_COMMAND = 0x2B
	ENABLE_SYSTEM_MESSAGE_DISPLAY = 0x2E
	DISABLE_SYSTEM_MESSAGE_DISPLAY = 0x2F
	ENABLE_SPLASH_DISPLAY = 0x30
	DISABLE_SPLASH_DISPLAY = 0x31
	SAVE_CURRENT_DISPLAY_AS_SPLASH = 0x0A
	#Special Commands
	LCD_RETURNHOME = 0x02
	LCD_ENTRYMODESET = 0x04
	LCD_DISPLAYCONTROL = 0x08
	LCD_CURSORSHIFT = 0x10
	LCD_SETDDRAMADDR = 0x80
	#Flags for display entry mode
	LCD_ENTRYRIGHT = 0x00
	LCD_ENTRYLEFT = 0x02
	LCD_ENTRYSHIFTINCREMENT = 0x01
	LCD_ENTRYSHIFTDECREMENT = 0x00
	#Flags for display on/off control
	LCD_DISPLAYON = 0x04
	LCD_DISPLAYOFF = 0x00
	LCD_CURSORON = 0x02
	LCD_CURSOROFF = 0x00
	LCD_BLINKON = 0x01
	LCD_BLINKOFF = 0x00
	#Flags for display/cursor shift
	LCD_DISPLAYMOVE = 0x08
	LCD_CURSORMOVE = 0x00
	LCD_MOVERIGHT = 0x04
	LCD_MOVELEFT = 0x00

	#I2C Config
	_bus = SMBus(1)
	_i2cAddr = I2C_ADDRESS
	_displayControl = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
	_displayMode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT

	def __init__(self, i2cAddr=I2C_ADDRESS):
		self._i2cAddr = i2cAddr

		self.specialCommand([self.LCD_DISPLAYCONTROL | self._displayControl])
		self.specialCommand([self.LCD_ENTRYMODESET | self._displayMode])
		self.clear()

	def command(self, byteCmd):
		self._bus.write_i2c_block_data(self._i2cAddr, self.SETTING_COMMAND, byteCmd)
		time.sleep(0.010)

	def specialCommand(self, byteCmd):
		self._bus.write_i2c_block_data(self._i2cAddr, self.SPECIAL_COMMAND, byteCmd)
		time.sleep(0.050)

	def clear(self):
		self.command([self.CLEAR_COMMAND])
		time.sleep(0.010)

	def home(self):
		self.specialCommand([self.LCD_RETURNHOME])

	def setCursor(self, col, row):
		row_offsets = [0x00, 0x40, 0x14, 0x54]
		row = max([0, row])
		row = min([row, self.MAX_ROWS - 1])
		self._bus.write_i2c_block_data(self._i2cAddr, self.SPECIAL_COMMAND, [self.LCD_SETDDRAMADDR | (col + row_offsets[row])])
		time.sleep(0.050)

	#Custom character
	def createChar(self, location, char_map):
		location = location & 0x7
		char_map.insert(0, 27 + location)
		char_map.insert(0, self.SETTING_COMMAND)
		self._bus.write_i2c_block_data(self._i2cAddr, 0, char_map)
		time.sleep(0.050)

	def writeChar(self, location):
		location = location & 0x7
		self._bus.write_i2c_block_data(self._i2cAddr, self.SETTING_COMMAND, [35 + location])
		time.sleep(0.010)

	#Write string
	def write(self, text):
		data = []
		for char in text:
			hv = ord(char)
			data.append(hv)
		data0 = data[0]
		del data[0]
		self._bus.write_i2c_block_data(self._i2cAddr, data0, data)
		time.sleep(0.010)

	#Display control
	def noDisplay(self):
		self._displayControl = self._displayControl & ~self.LCD_DISPLAYON
		self.specialCommand([self.LCD_DISPLAYCONTROL | self._displayControl])

	def display(self):
		self._displayControl = self._displayControl | self.LCD_DISPLAYCONTROL
		self.specialCommand([self.LCD_DISPLAYCONTROL | self._displayControl])

	def noCursor(self):
		self._displayControl = self._displayControl & ~self.LCD_CURSORON
		self.specialCommand([self.LCD_DISPLAYCONTROL | self._displayControl])

	def cursor(self):
		self._displayControl = self._displayControl | self.LCD_CURSORON
		self.specialCommand([self.LCD_DISPLAYCONTROL | self._displayControl])

	def noBlink(self):
		self._displayControl = self._displayControl & ~self.LCD_BLINKON
		self.specialCommand([self.LCD_DISPLAYCONTROL | self._displayControl])

	def blink(self):
		self._displayControl = self._displayControl | self.LCD_BLINKON
		self.specialCommand([self.LCD_DISPLAYCONTROL | self._displayControl])

	def scrollDisplayLeft(self):
		self.specialCommand([self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT])

	def scrollDisplayRight(self):
		self.specialCommand([self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT])

	def moveCursorLeft(self):
		self.specialCommand([self.LCD_CURSORSHIFT | self.LCD_CURSORMOVE | self.LCD_MOVELEFT])

	def moveCursorRight(self):
		self.specialCommand([self.LCD_CURSORSHIFT | self.LCD_CURSORMOVE | self.LCD_MOVERIGHT])

	def setBacklight(self, r, g, b):
		self._bus.write_i2c_block_data(self._i2cAddr, self.SETTING_COMMAND, [self.SET_RGB_COMMAND, r, g, b])
		time.sleep(0.010)

	def enableSystemMessages(self):
		self._bus.write_i2c_block_data(self._i2cAddr, self.SETTING_COMMAND, [self.ENABLE_SYSTEM_MESSAGE_DISPLAY])
		time.sleep(0.010)

	def disableSystemMessages(self):
		self._bus.write_i2c_block_data(self._i2cAddr, self.SETTING_COMMAND, [self.DISABLE_SYSTEM_MESSAGE_DISPLAY])
		time.sleep(0.010)

	def enableSplash(self):
		self._bus.write_i2c_block_data(self._i2cAddr, self.SETTING_COMMAND, [self.ENABLE_SPLASH_DISPLAY])
		time.sleep(0.010)

	def disableSplash(self):
		self._bus.write_i2c_block_data(self._i2cAddr, self.SETTING_COMMAND, [self.DISABLE_SPLASH_DISPLAY])
		time.sleep(0.010)

	def saveAsSplash(self):
		self._bus.write_i2c_block_data(self._i2cAddr, self.SETTING_COMMAND, [self.SAVE_CURRENT_DISPLAY_AS_SPLASH])
		time.sleep(0.010)

	def leftToRight(self):
		self._displayMode = self._displayMode | self.LCD_ENTRYLEFT
		self.specialCommand([self.LCD_ENTRYMODESET | self._displayMode])

	def rightToLeft(self):
		self._displayMode = self._displayMode & ~self.LCD_ENTRYLEFT
		self.specialCommand([self.LCD_ENTRYMODESET | self._displayMode])

	def autoScroll(self):
		self._displayMode = self._displayMode | self.LCD_ENTRYSHIFTINCREMENT
		self.specialCommand([self.LCD_ENTRYMODESET | self._displayMode])

	def noAutoScroll(self):
		self._displayMode = self._displayMode & ~self.LCD_ENTRYSHIFTINCREMENT
		self.specialCommand([self.LCD_ENTRYMODESET | self._displayMode])

	def setContrast(self, newVal):
		self._bus.write_i2c_block_data(self._i2cAddr, self.SETTING_COMMAND, [self.CONTRAST_COMMAND, newVal])
		time.sleep(0.010)

	def setAddress(self, newAddr):
		self._bus.write_i2c_block_data(self._i2cAddr, self.SETTING_COMMAND, [self.ADDRESS_COMMAND, newAddr])
		self._i2cAddr = newAddr
		time.sleep(0.050)

def main():
	lcd = SerLCD()
	lcd.setBacklight(64, 64, 64)
	lcd.noCursor()
	while True:
		now = datetime.datetime.utcnow()
		lcd.clear()
		lcd.write("Hello World!")
		#lcd.scrollDisplayLeft()
		lcd.setCursor(0, 1)
		lcd.write(now.strftime("%H:%M:%S"))
		time.sleep(1.0)

if __name__ == '__main__':
	main()