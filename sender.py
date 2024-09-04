import numpy as np
import pyaudio
import time

total = 0
factor = 100
polynomial = "10101110011"
factor = 100
offset = 1000
packet_size = 5
def binaryToDecimal(n):
    return int(n, 2)

def decimalToBinary(n):
    return '{0:05b}'.format(n) # 5 bits

def bitstring_to_frequency(bitstring):
    frequencies = []
    
    bitstring1 = bitstring[:5] # 5 bits
    decimal = binaryToDecimal(bitstring1)
    frequencies.append(decimal * factor + offset)
    
    num_segments = int((decimal-1)/ packet_size)+1
    bitstring_length = len(bitstring)
    
    for i in range(num_segments):
        start_index = 5 + i * packet_size
        end_index = 5 + (i+1) * packet_size
        
        if end_index <= bitstring_length:
            new_d = binaryToDecimal(bitstring[start_index:end_index])
            frequencies.append(new_d*factor+offset)
        else:
            print("Warning: Bitstring too short for the expected segments.")
            break
    
    return frequencies

def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    return wave

def play_sound(frequencies, duration=4, sample_rate=44100):
    global total
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, output=True)

    for freq in frequencies:
        start_time = time.perf_counter()
        wave = generate_sine_wave(freq, duration)
        stream.write(np.ascontiguousarray(wave, dtype=np.float32))
        end_time = time.perf_counter()
        
        playback_duration = end_time - start_time
        print(f"Frequency: {freq} Hz (Decimal: {int((freq-offset)/factor)}, Binary: {decimalToBinary(int((freq-offset)/factor))}) time: {playback_duration:.4f}")
        total += playback_duration

    stream.stop_stream()
    stream.close()
    p.terminate()

#crc part

def crc_remainder(input_bitstring, polynomial_bitstring, initial_filler='0'):
    """Calculate the CRC remainder of a string of bits using a chosen polynomial."""
    polynomial_bitstring = polynomial_bitstring.lstrip('0')
    len_polynomial = len(polynomial_bitstring)
    input_padded_array = list(input_bitstring + initial_filler * (len_polynomial - 1))
    
    while '1' in input_padded_array[:len(input_bitstring)]:
        cur_shift = input_padded_array.index('1')
        for i in range(len_polynomial):
            input_padded_array[cur_shift + i] = str(int(polynomial_bitstring[i] != input_padded_array[cur_shift + i]))
    
    return ''.join(input_padded_array)[len(input_bitstring):]

def sender(message, polynomial):
    """Simulates the sender by creating a message with CRC."""
    crc_checksum = crc_remainder(message, polynomial)
    return message + crc_checksum

def flip_bits(bitstring, positions):
    """Flip bits in the bitstring at the specified positions."""
    bitstring = list(bitstring)
    for pos in positions:
        bitstring[pos] = '1' if bitstring[pos] == '0' else '0'
    return ''.join(bitstring)





message = str(input("Enter message : "))
bits_to_flip = list(map(int,input("Enter bits to flip (at max 2) : ").split()))
# bits_to_flip = [i-1 for i in bits_to_flip] #making it 0 indexed
# Sender appends CRC to the message
message_with_crc = sender(message, polynomial)
print(f"Sent message with CRC: {message_with_crc}")
# Simulate bit flipping at the sender
flipped_message = flip_bits(message_with_crc, bits_to_flip)
final_len = len(flipped_message)  #message length without offset
print(f"Message with flipped bits: {flipped_message}")
packet_size = 5 #length of the final message will be a multiple of this as we are sending bits in packets of this number
remainder = final_len % packet_size
preamble = decimalToBinary(final_len)
if remainder != 0:
    final_message = preamble + '0' * (packet_size - remainder) + flipped_message
else :
    final_message = preamble + flipped_message
print(f"Final message: {final_message}")


frequencies = bitstring_to_frequency(final_message)
play_sound(frequencies)
