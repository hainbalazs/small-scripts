from z3 import *

#Type declarations
BYTE = 8


def substitute(n):
    n = int(n)
    if n < 10:
        return str(n)
    else:
        return chr(ord('a') + (n - 10))


# Get 'bits' amount of bits from the ch + offset address, takes care of endianness
def data(ch, bits, offset):
    assert bits % 4 == 0
    assert offset % 4 == 0
    assert offset / 4 + bits / 4 <= len(ch)
    offset = offset // 4
    bits = bits // 4

    sequence = None
    for i in range(offset, offset + bits, 2):
        byte = Concat(ch[i], ch[i + 1])
        if sequence is not None:
            sequence = Concat(byte, sequence)
        else:
            sequence = byte
    assert sequence is not None
    return sequence


# Variable to solve for
checksum = [BitVec(f'c_{c}', 4) for c in range(32 * 8)]
s = Solver()
legi_array = [3, 1, 3, 3, 7, 0, 4, 2]

# Constraint by func1
s.add(Sum(data(checksum, 8 * BYTE, 0),
          data(checksum, 8 * BYTE, 8 * BYTE),
          data(checksum, 8 * BYTE, 2 * 8 * BYTE),
          data(checksum, 8 * BYTE, 3 * 8 * BYTE)) == 0xFFD7C787879FC7FF)

# Constraint by func2
for i in range(8):
    c = data(checksum, BYTE, i * BYTE)
    s.add(legi_array[i] == ((c ^ 0xc9) >> 0x6 & 0x3) | ((c ^ 0xc9) & 0x3f) << 2)

# Constraint by func3
for i in range(8):
    s.add(data(checksum, BYTE, i * BYTE) ^ data(checksum, BYTE, (15 - i) * BYTE) == i)

# Constraint by func4
s.add(data(checksum, BYTE, 16 * BYTE) == sum(legi_array))
for i in range(17, 24):
    s.add(data(checksum, BYTE, i * BYTE) == data(checksum, BYTE, (i - 1) * BYTE) + data(checksum, BYTE, (i - 2) * BYTE))

# Print the licence
if s.check() == sat:
    d = dict()
    for name in s.model():
        d[str(name)] = substitute(s.model()[name].as_long())
    dic = dict(sorted(d.items(), key=lambda x: int(x[0].split('_')[1])))
    print("".join(dic.values()))
