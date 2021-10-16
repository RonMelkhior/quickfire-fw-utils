import usb1

def main():
	with usb1.USBContext() as c:
		for device in c.getDeviceList():
			if device.getVendorID() != 0x2516:
				continue

			print('Found the device!')
			print(f'Product ID: {device.getProductID()}')

if __name__ == '__main__':
	main()
