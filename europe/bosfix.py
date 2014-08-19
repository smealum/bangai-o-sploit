import struct
import os

def checksum(f):
	f.seek(0x2000)
	b=0
	for i in range(0x1000):
		b=b+(f.read(1))[0]
	return b

def copyFileToFile(destf, srcfn, addr, maxsize):
	s=os.path.getsize(srcfn)
	file=open(srcfn,"rb")
	destf.seek(addr)
	print(s)
	for i in range(min(s,maxsize)):
		destf.write(file.read(1))
	file.close()

fn="bosnewus.SAV"

file=open(fn,"rb+")

c=checksum(file)
hex(c)

file.seek(0x22)
file.write(struct.pack('B',c&0xFF))
file.write(struct.pack('B',(c>>8)&0xFF))

copyFileToFile(file, "arm9.bin", 0x16CD0, 0x1D800)
copyFileToFile(file, "arm7.bin", 0x35000, 0xFB98)

file.close()
