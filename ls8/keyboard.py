"""
Keyboard

1. Has access to CPU instance so it can call an interrupt, access memory (DMA)
2. Runs in its own thread to allow for simultaneous execution of CPU cycle and keyboard polling loop
"""

import sys
import threading
from time import sleep


class Keyboard:
    def __init__(self, emulator):
        # Get access to emulator as a 'peripheral'
        self._emulator = emulator
        # Create keyboard polling thread
        self._keyboard_thread = threading.Thread(target=self._poll)
        # Making thread a daemon will allow for auto cleanup on main program exit
        self._keyboard_thread.daemon = True

    def connect(self):
        # Start thread
        self._keyboard_thread.start()

    def _poll(self):
        # Enter keyboard polling loop
        while True:
            char = sys.stdin.read(1)  # Read one byte (char)
            if char:
                # Set char in memory
                self._emulator.ram[0xF4] = ord(char)
                # Raise keyboard interrupt
                self._emulator.reg[self._emulator.isr] = self._emulator._set_nth_bit(
                    self._emulator.reg[self._emulator.isr], 1
                )

            # Sleep 50 ms to keep cpu usage down
            # Technically this makes it poll the keyboard at 20hz
            sleep(0.05)
