import numpy as np
import pyaudio
from scipy.fft import fft
import time

SAMPLE_RATE = 10000
DURATION = 0.85
factor = 100
offset = 1000
packet_size = 5
flg = 0
n1 = 0
bitstring = ''
polynomial = "10101110011" 

def binaryToDecimal(n):
    return int(n, 2)

def decimalToBinary(n):
    return '{0:05b}'.format(n)

def approximator(n):
    return (int(n/factor) * factor + (factor if n % factor > factor/2 else 0))

def record_sound(duration, sample_rate=SAMPLE_RATE):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=int(sample_rate * duration))
    frames = stream.read(int(sample_rate * duration))
    stream.stop_stream()
    stream.close()
    p.terminate()
    audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
    return audio_data

def detect_frequency(audio_data, sample_rate):
    global flg, n1, bitstring, factor, offset, packet_size
    n = len(audio_data)
    freq = np.fft.fftfreq(n, d=1/sample_rate)
    fft_data = np.abs(fft(audio_data))
    peak_freq = freq[np.argmax(fft_data)]
    appx = approximator(peak_freq) - offset
    int_freq = int(appx/factor)
    
    if flg == 1 and n1 != 0:
        bitstring += decimalToBinary(int_freq)
        n1 -= packet_size
        print("Remaining length: ", n1)
        if n1 == 0:
            flg = 5
    elif flg == 0 and int_freq >= 1 and int_freq <= 30:
        n1 = (int((int_freq+packet_size-1)/packet_size))*packet_size
        flg = 1
        bitstring += decimalToBinary(int_freq)
        print("Length was detected as: ", n1)

    print(f"Detected frequency: {appx} Hz and bitstring is ({decimalToBinary(int(appx/factor))})")
    return peak_freq

#crc part

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


def detect_and_correct_errors(received_message, polynomial, lookup_table):
    """Detect and correct errors in the received message using the lookup table."""
    remainder = crc_remainder(received_message, polynomial)
    
    if int(remainder) == 0:
        return received_message[:len(received_message) - len(polynomial) + 1], "No errors detected."
    
    if remainder in lookup_table:
        error_position = lookup_table[remainder]
        
        corrected_message = flip_bits(received_message, error_position)
        return corrected_message[:len(received_message) - len(polynomial) + 1], f"Error detected and corrected at position {error_position}."
    
    return received_message, "Unrecognized error pattern."


def flip_bits(bitstring, positions):
    """Flip bits in the bitstring at the specified positions."""
    bitstring = list(bitstring)
    positions = list(positions)
    positions = positions[0]
    for pos in positions:
        bitstring[pos] = '1' if bitstring[pos] == '0' else '0'
    return ''.join(bitstring)

def main():
    global flg, n1, bitstring
    num_bits = 10

    for i in range(num_bits):
        if flg == 5:
            break
            # with open('output.txt', 'a') as f:
            #     f.write(bitstring + '\n')
            # flg = 0
            # n1 = 0
            # bitstring = ''
        time1 = time.perf_counter()
        audio_data = record_sound(DURATION)
        freq = detect_frequency(audio_data, SAMPLE_RATE)
        time2 = time.perf_counter()
        print("Time taken: ", time2-time1)

    preamble = bitstring[:packet_size]
    len_message = binaryToDecimal(preamble)
    flipped_message = bitstring[packet_size : ] #first packet_size bits are for preamble
    final_message = flipped_message[-len_message:]
    len_without_error_message = len_message - (len(polynomial) -1)
    lookup_table = generate_crc_lookup_table(polynomial, len_without_error_message)
    corrected_message, result = detect_and_correct_errors(final_message, polynomial, lookup_table)
    print(f"Corrected message: {corrected_message}")
    print(result)

if __name__ == "__main__":
    main()
