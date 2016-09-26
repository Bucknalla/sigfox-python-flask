from bitstring import BitArray, BitStream

byte1 = 161
byte2 = 107

byte1 = BitArray(uint=byte1, length=8)
print byte1.bin
byte2 = BitArray(uint=byte2, length=8)
print byte2.bin
batt = byte1[0:1] + byte2[0:4]
print batt.uint
