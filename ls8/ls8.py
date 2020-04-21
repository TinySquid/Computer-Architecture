#!/usr/bin/env python

"""Main."""

import sys
from os import path

from cpu import *


def print_usage(error):
    """
    Prints usage statement along with any error if provided
    """
    if error:
        print("error: " + error)
    print("usage: ls8.py input_file")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        # Valid arguments supplied, but does the input_file exist?
        input_file = sys.argv[1]
        if path.exists():
            # Create instance
            cpu = CPU()
            # Load program into RAM
            cpu.load(input_file)
            # Start execution loop
            cpu.run()
        else:
            print_usage("input_file not found")
    else:
        print_usage("missing required arguments")
