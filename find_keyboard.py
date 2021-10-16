import usb1
import itertools

DEVICE_TARGET = 0x2516

def find_device(device_list, target):
	return next((device for device in device_list if device.getVendorID() == target), None)

def main():
	with usb1.USBContext() as c:
		device = find_device(c.getDeviceList(), 5426)
		if device:
			print('Found the device!')
			print(f'Product ID: {device.getProductID()}')

if __name__ == '__main__':
	main()
