import sys
import wave
import struct

# bit0 is a single period sine wave at 1024Hz with a given amplitude
# bit1 is the same but with ~2.7 times the amplitude
bits = [[0x00, 0x09, 0x12, 0x1A, 0x21, 0x27, 0x2C, 0x2F, 0x30, 0x2F, 0x2C, 0x27, 0x21, 0x1A, 0x12, 0x09, 0x00, 0xF6, 0xED, 0xE5, 0xDE, 0xD8, 0xD3, 0xD0, 0xD0, 0xD0, 0xD3, 0xD8, 0xDE, 0xE5, 0xED, 0xF6], [0x00, 0x18, 0x30, 0x46, 0x59, 0x69, 0x75, 0x7C, 0x7F, 0x7C, 0x75, 0x69, 0x59, 0x46, 0x30, 0x18, 0x00, 0xE7, 0xCF, 0xB9, 0xA6, 0x96, 0x8A, 0x83, 0x81, 0x83, 0x8A, 0x96, 0xA6, 0xB9, 0xCF, 0xE7]]
bits[0] = [b^0x80 for b in bits[0]]
bits[1] = [b^0x80 for b in bits[1]]
bits[0] = struct.pack('%sB' % len(bits[0]), *bits[0])
bits[1] = struct.pack('%sB' % len(bits[1]), *bits[1])

data_fn = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "raw"

data = open(data_fn, "rb").read()

if mode == "level":
	header = [0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0x0A, 0x02, 0x02]
	header = struct.pack('%sB' % len(header), *header)
	header += struct.pack('<HH', len(data), len(data))
	data = header + data + struct.pack('<L', sum(data))

open("test.bin","wb").write(data)

wav_out = wave.open('noise.wav', 'w')
wav_out.setparams((1, 1, 32768, 0, 'NONE', 'not compressed'))

for v in data:
	for i in range(8):
		wav_out.writeframes(bits[(v>>i)&1])

wav_out.close()
