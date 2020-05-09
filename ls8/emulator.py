#!/usr/bin/env python

"""Main."""

import sys
from os import path
from cpu import CPU
from keyboard import Keyboard


def print_usage(error: str) -> None:
    """
    Prints usage statement along with any error if provided
    """
    if error:
        print("error: " + error + "\n")
    print("usage: ls8.py input_file [-d] (debug trace)")


if __name__ == "__main__":
    args = sys.argv
    args_len = len(args)

    # Valid number of arguments
    if args_len > 1 and args_len < 4:
        # Must provide atleast input file
        input_file = args[1]
        # Is file valid
        if path.exists(input_file):
            # Create instance
            emulator = CPU()

            # Initialize keyboard
            keyboard = Keyboard(emulator)

            # Load program
            emulator.load(input_file)

            # Connect keyboard (starts polling thread)
            keyboard.connect()

            # Run without debug trace mode
            if args_len == 2:
                emulator.run()

            # Run with debug trace mode
            elif args_len == 3:
                if args[2] == "-d":
                    emulator.run(trace_cycle=True)
                else:
                    print_usage("Invalid flag set")

        else:
            print_usage("input_file not found")
    else:
        print_usage("Invalid number of arguments")
