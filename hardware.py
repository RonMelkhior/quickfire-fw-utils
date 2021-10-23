from struct import pack
from libscrc import xmodem
from usb1 import USBContext
from argparse import ArgumentParser, Namespace

PACKET_SIZE = 64
VERBOSE = 1
DEBUG = 2


def find_device(vendor_id: int,
                product_id: int,
                device_list: list = USBContext().getDeviceList()):
    for device in device_list:
        if device.getVendorID() == vendor_id and \
                device.getProductID() == product_id:
            return device


def build_read_packet(start: int):
    buf = pack("BBHII", 0x1, 0x2, 0, start, start+63)
    padding = pack("B", 0) * (PACKET_SIZE - len(buf))
    crc = xmodem(buf + padding)
    buf = pack("BBHII", 0x1, 0x2, crc, start, start+63) + padding
    return buf


def print_list_devices():
    print("List of current devices:")
    print("Bus\tDevice\tHEX ID [Vendor:Product]")
    for device in USBContext().getDeviceList():
        print(device)


def _validate_args(args):
    failed = False
    if args.vendor_id is None:
        print("Error: Missing vendor id.")
        failed = True
    if args.product_id is None:
        print("Error: Missing product id.")
        failed = True
    return failed


def _parse_args() -> Namespace:
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
        help="The device's vendor ID."
    )
    required.add_argument(
        "-pi", "--product-id",
        default=None,
        type=int,
        help="The device's product ID."
    )

    args = parser.parse_args()
    if args.list:
        print_list_devices()
        return

    failed = _validate_args(args)
    if failed:  # Silent crushing.
        parser.print_usage()
        return
    return args


def main():
    args = _parse_args()
    if args is None:  # Silent crushing.
        return
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
