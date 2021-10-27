from IPython import embed

from hardware import find_device, build_read_packet

COOLER_MASTER_VENDOR_ID = 0x2516
KEYBOARD_NORMAL_PRODUCT_ID = 0x2e
KEYBOARD_INTERFACE_ID = 0x1


def main() -> int:
    """Reading keyboard's firmware.

    Returns:
        int or None: status code, None for success.
    """
    keyboard = find_device(COOLER_MASTER_VENDOR_ID, KEYBOARD_NORMAL_PRODUCT_ID)
    if not keyboard:  # Silent crashing.
        print("Keyboard not found.")
        return -1
    interface = keyboard.open()
    with interface.claimInterface(KEYBOARD_INTERFACE_ID):
        result = b''
        for i in range(1100):
            buf = build_read_packet(0x2c00 + (64 * i))
            interface.interruptWrite(4, buf)
            result += bytes(interface.interruptRead(3, 64))
        embed()


if __name__ == '__main__':
    main()
