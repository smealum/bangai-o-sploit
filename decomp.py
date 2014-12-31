# REd this from the game's code
# looks like some LZ variant but couldn't identify which one
import sys
import struct

def repeatData(data, length, disp):
	remainder = length % disp
	data += data[-disp:]*int((length-remainder)/disp)
	if remainder>0:
		data += data[-disp:-disp+remainder]

comp_data = bytearray(open("comp.bin", "rb").read())
out_data = []

c = 0
while c < len(comp_data):
	code = comp_data[c]
	stride = 1
	if code&0x80 != 0:
		disp = ((code>>2)&0x1F) + 1
		length = (code&0x3) + 1
		print("mini repeat block ! "+hex(length)+" "+hex(disp))
		if disp > len(out_data):
			print("invalid mini repeat block !")
		repeatData(out_data, length, disp)
	elif code&0x40 != 0:
		code = (code<<8) | comp_data[c+1]
		disp = ((code>>4)&0x3FF) + 1
		length = (code&0xF) + 2
		stride += 1
		print("distant repeat block ! "+hex(length)+" "+hex(disp))
		if disp > len(out_data):
			print("invalid distant repeat block !")
		repeatData(out_data, length, disp)
	elif code&0x20 != 0:
		code = (code<<8) | comp_data[c+1]
		disp = ((code>>9)&0xF)+1
		length = (code&0x1FF)+2
		stride += 1
		print("repeat block ! "+hex(length)+" "+hex(disp))
		if disp > len(out_data):
			print("invalid repeat block !")
		repeatData(out_data, length, disp)
	else:
		length = code
		out_data += comp_data[c+1:c+1+length]
		print("raw block ! "+hex(length))
		stride += length
	c += stride

open("out.bin", "wb").write(struct.pack('%sB' % len(out_data), *out_data))
