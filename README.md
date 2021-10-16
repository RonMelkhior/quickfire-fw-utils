# Quickfire FW Utils

Interesting addresses:

- `0x2800` - Version string section
- `0x2c00` - Firmware

By default, `read` packets directed at >= 0x2c00 are blocked (result returns NULLs).  
Requires a patched firmware in order for it to work.
