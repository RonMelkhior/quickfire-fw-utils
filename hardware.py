from struct import pack
from libscrc import xmodem
from typing import Optional
from usb1 import USBContext, USBDevice
from argparse import ArgumentParser, Namespace as ArgsNameSpace

PACKET_FORMAT = "BBHII"
NULL_BYTE = b"\x00"
PACKET_SIZE = 64
VERBOSE = 1
DEBUG = 2


def find_device(vendor_id: int,
                product_id: int,
                device_list: Optional[list] = None) -> Optional[USBDevice]:
    """
    Finds a USB device by given vendor and product ID.

    Args:
        vendor_id (int): The device's vendor ID
        product_id (int): The device's product ID
        device_list (Optional[list], optional): The list of devices (libusb1
            format). Otherwise getting all USBs

    Returns:
        USBDevice or None: The device if found, otherwise None
    """
    use_internal_device_list = device_list is None
    if use_internal_device_list:
        context = USBContext()
        try:
            device_list = context.getDeviceList()
        finally:
            context.close()
    for device in device_list:
        if device.getVendorID() == vendor_id and \
                device.getProductID() == product_id:
            return device


def build_read_packet(start: int) -> Bytes:
    """Building the read packet to send.

    Args:
        start (int): The start offset for reading.

    Returns:
        Bytes: The read packet with the start offset followed by 63 more.
    """
    buf = pack(PACKET_FORMAT, 0x1, 0x2, 0, start, start+63)
    padding = NULL_BYTE * (PACKET_SIZE - len(buf))
    crc = xmodem(buf + padding)
    buf = pack(PACKET_FORMAT, 0x1, 0x2, crc, start, start+63) + padding
    return buf


def print_list_devices() -> None:
    """Prints the list of all the current USB devices."""
    print("List of current devices:")
    print("Bus\tDevice\tHEX ID [Vendor:Product]")
    for device in USBContext().getDeviceList():
        print(device)


def _validate_args(args: ArgsNameSpace) -> bool:
    """Validates if the given args do contain vendor id and product id.

    Args:
        args (ArgsNameSpace): The arguments object.

    Returns:
        bool: failed or not.
    """
    failed = False
    if args.vendor_id is None:
        print("Error: Missing vendor id.")
        failed = True
    if args.product_id is None:
        print("Error: Missing product id.")
        failed = True
    return failed


def _parse_args() -> Optional[ArgsNameSpace]:
    """Retrieve the given args of the calling process.

    Returns:
        ArgsNameSpace: An args object containing all of the arguments passed,
            or None if failure or print only.
    """
    parser = ArgumentParser(
        description="Process the given vendor and product IDs.")
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Give more output. Option is additive, "
        "and can be used up to 2 times."
    )
    parser.add_argument(
        "-l", "--list",
        action='store_true',
        help="Show the list of all devices and exit."
    )

    # I am aware that '--' or '-' makes it optional.
    # I force it to be required - 'positional' because:
    #   * I want the freedom in calling options, order and style.
    #   * I want the ability to have the arguments as class members.
    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "-vi", "--vendor-id",
        default=None,
        type=int,
        help="The device's vendor ID.",
    )
    required.add_argument(
        "-pi", "--product-id",
        default=None,
        type=int,
        help="The device's product ID.",
    )

    args = parser.parse_args()
    if args.list:
        print_list_devices()
        return

    failed = _validate_args(args)
    if failed:  # Silent crashing.
        parser.print_usage()
        return
    return args


def main() -> int:
    """main function, called if specifically executed this file,
        will enable you to retrieve a device or view current devices.

    Returns:
        int: status code.
    """
    args = _parse_args()
    if args is None:  # Silent crashing.
        return -1
    if args.verbose >= VERBOSE:
        print("Starting to scan devices...")
    device = find_device(args.vendor_id, args.product_id)
    if device:
        print(f"Device {device} found!")
    else:
        print(f"Device of {args.vendor_id=}, {args.product_id=} not found.")
        if args.verbose >= DEBUG:
            print_list_devices()


if __name__ == '__main__':
    main()
