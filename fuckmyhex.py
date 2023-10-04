import argparse
import sys
import itertools

'''
# Generate permutations of characters
characters=['r', 'x', 'b']
permutations = []
for r in range(1, len(characters) + 1):
        permutations.extend(itertools.permutations(characters, r))
ops = [''.join(permutation) for permutation in permutations]
'''

# right now the program assumes that the input is uniform in the convention
# e.g.: all lines are bytes or all lines are hex

byte_mode=True

# functions operations
# detects and clear \x prepends before hex bytes if they are present
def clean_hex(output):
    return [line.replace("\\x", "") for line in output]

def tobytes(output):
    global byte_mode
    try:
        byte_mode=False
        return [bytes.fromhex(hex_str) for hex_str in clean_hex(output)]
    except:
        byte_mode=True
        return [line.strip().encode() for line in output]

def tohex(output):
    return [bs.hex() for bs in output]

#expects bytes
def bytes_reverse(output):
    return [bs[::-1] for bs in output]

#expects bytes
def bytes_xor(output):
    result = []

    for i in range(0, len(output) - 1, 2):
        if i + 1 < len(output):
            if len(output[i]) != len(output[i + 1]):
                print(f"fuckmyhex.py: error: xor: bytes of different length:\n{i}: {output[i]} is {len(output[i])} bytes\n{i+1}: {output[i+1]} is {len(output[i+1])} byts") 
                exit(-1)
            xored_bytes = bytes(a ^ b for a, b in zip(output[i], output[i + 1]))
            result.append(xored_byte)

    # If there's an odd number of bytes, append the last one as is 
    if len(output) % 2 == 1:
        result.append(output[-1])
    return result

#expect bytes
def bytes_add(output):
    result = []

    for i in range(0, len(output) - 1, 2):
        if i + 1 < len(output):
            result_int = int.from_bytes(output[i], byteorder="little") + int.from_bytes(output[i+1], byteorder="little")
            result.append(result_int.to_bytes((result_int.bit_length() + 7) // 8, byteorder="little"))

    # If there's an odd number of bytes, append the last one as is 
    if len(output) % 2 == 1:
        result.append(output[-1])
    return result

#expect bytes
def bytes_mul(output):
    result = []

    for i in range(0, len(output) - 1, 2):
        if i + 1 < len(output):
            result_int = int.from_bytes(output[i], byteorder="little") * int.from_bytes(output[i+1], byteorder="little")
            result.append(result_int.to_bytes((result_int.bit_length() + 7) // 8, byteorder="little"))

    # If there's an odd number of bytes, append the last one as is 
    if len(output) % 2 == 1:
        result.append(output[-1])
    return result


# parsing args
parser = argparse.ArgumentParser(description='Hex tool for various ops')
parser.add_argument('-f', '--file', type=argparse.FileType('r'), default=sys.stdin, help="specify a file path to read from input. stdin is default if not provided")
parser.add_argument('ops', nargs='*', default=[], help='Do operations with bytes or hex provided. Operations: (h): hex mode, (b) bytes mode, (r): revert bytes line by line, (x) xor byte lines two by two, (a) arithmetic addition of lines two by two [lITTLE ENDIAN], (m) arithmetic multiplication of lines two by two [lITTLE ENDIAN]')
args = parser.parse_args()
file = args.file
valid_ops = ['r', 'h', 'b', 'x', 'a', 'm']
ops = list(itertools.chain.from_iterable(args.ops))
for op in ops:
    if op not in valid_ops:
        print(f"fuckmyhex.py: error: argument ops: invalid choice: '{op}' (choose from {valid_ops})")
        exit(-1)


# reading data from file
output = tobytes(file.readlines())

# handling ops
for op in ops:
    #convert bytes to hex
    if op == 'h':
        byte_mode = False

    #convert hex to bytes
    if op == 'b':
        byte_mode = True
        
    # revert
    if op == 'r':
        output = bytes_reverse(output)
   
    # xor
    if op == 'x':
        output = bytes_xor(output)

    # add
    if op == 'a':
        output = bytes_add(output)

    # mul
    if op == 'm':
        output = bytes_mul(output)

# always print modified file
if not byte_mode:
    output = tohex(output)
for line in output:
    print(line)
