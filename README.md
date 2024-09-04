### Running Instructions

1. **Run the Sender Code**:
    - Use the following command to execute the `sender.py` file:
      ```bash
      python3 sender.py
      ```
    - You will be prompted to enter a bitstring message (maximum length of 20 characters).
    - After entering the message, you will be asked to specify indices for flipping bits (using 0-based indexing).

2. **Run the Receiver Code**:
    - Execute the `receiver.py` file with the command:
      ```bash
      python3 receiver.py
      ```
    - The receiver will start listening for sound signals.

3. **Trigger the Transmission**:
    - Press `Enter` in the sender code to generate the sound signal.
    - The receiver will capture the signal, decode it, and display the correct message.
