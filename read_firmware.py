import usb1
import IPython
import libscrc
import struct

COOLER_MASTER_VENDOR_ID = 0x2516
KEYBOARD_NORMAL_PRODUCT_ID = 0x2e
KEYBOARD_INTERFACE_ID = 0x1

def find_keyboard_device(c):
	for device in c.getDeviceList():
		if device.getVendorID() == COOLER_MASTER_VENDOR_ID and device.getProductID() == KEYBOARD_NORMAL_PRODUCT_ID:
			return device

	return None

def p16(num):
	return struct.pack('=H', num)

def p32(num):
	return struct.pack('=L', num)

def u32(payload):
	return struct.unpack('=L', payload)[0]
	
def build_read_packet(start):
	buf = bytearray(64)
	buf[0] = 0x1
	buf[1] = 0x2
	buf[4:8] = p32(start)
	buf[8:12] = p32(start + 63)
	buf[2:4] = p16(libscrc.xmodem(bytes(buf)))
	return buf


def main():
	with usb1.USBContext() as c:
		k = find_keyboard_device(c).open()
		with k.claimInterface(KEYBOARD_INTERFACE_ID):
			result = b''
			for i in range(1100):
				buf = build_read_packet(0x2c00 + (64 * i))
				k.interruptWrite(4, buf)
				result += bytes(k.interruptRead(3, 64))
			IPython.embed()

if __name__ == '__main__':
	main()
