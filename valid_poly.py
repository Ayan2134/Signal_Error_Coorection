import numpy as np
import pyaudio
from scipy.fft import fft

def crc_remainder(input_bitstring, polynomial_bitstring, initial_filler='0'):
    """Calculate the CRC remainder of a string of bits using a chosen polynomial."""
    polynomial_bitstring = polynomial_bitstring.lstrip('0')
    len_polynomial = len(polynomial_bitstring)
    
    # Append initial filler bits to input_bitstring
    input_padded = input_bitstring + initial_filler * (len_polynomial - 1)
    
    # Convert to a list for easier manipulation
    input_padded_array = list(input_padded)
    
    for i in range(len(input_bitstring)):
        if input_padded_array[i] == '1':
            # Perform XOR with the polynomial at the current position
            for j in range(len_polynomial):
                input_padded_array[i + j] = str(int(input_padded_array[i + j] != polynomial_bitstring[j]))
    
    # The remainder is the last len_polynomial-1 bits of input_padded_array
    remainder = ''.join(input_padded_array[-(len_polynomial - 1):])
    
    return remainder

def generate_crc_lookup_table(polynomial, message_length):
    """Generate a lookup table mapping CRC remainders to error positions."""
    lookup_table = {}
    total_length = message_length + len(polynomial) - 1

    # Iterate over all possible pairs of bit positions
    for i in range(total_length):
        for j in range(i, total_length):
            # Flip bits at positions i and j
            bitstring = ['0'] * total_length
            bitstring[i] = '1'
            if j != i:
                bitstring[j] = '1'
            bitstring = ''.join(bitstring)

            remainder = crc_remainder(bitstring, polynomial)

            if remainder in lookup_table:
                lookup_table[remainder].append((i, j))
            else:
                lookup_table[remainder] = [(i, j)]

    return lookup_table

def generate_bitstrings(n):
    # There are 2^n possible bitstrings of length n
    bitstrings = []
    for i in range(2**n):
        # Convert each number to its binary representation and pad with leading zeros
        bitstring = bin(i)[2:].zfill(n)
        bitstrings.append(bitstring)
    return bitstrings

def check_for_collisions(lookup_table):
    """Check for collisions in the CRC lookup table."""
    for remainder, positions_list in lookup_table.items():
        if len(positions_list) > 1:
            return False

    return True

message_length = 20
bitstrings = generate_bitstrings(11)
valid_polynomial = []

for bitstring in bitstrings:
    table = generate_crc_lookup_table(bitstring,message_length)
    if(check_for_collisions(table)) :
        valid_polynomial.append(bitstring)

with open("valid_polynomials.txt", "w") as file:
    for polynomial in valid_polynomial:
        file.write(polynomial + "\n")

print("Total found : ",len(valid_polynomial)," polynomials")
