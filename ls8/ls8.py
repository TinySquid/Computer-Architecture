#!/usr/bin/env python

"""Main."""

import sys
from cpu import *


# For now, we've just hardcoded a program:
program = [
    # From print8.ls8
    0b10000010, # LDI R0,8
    0b00000000,
    0b00001000,
    0b01000111, # PRN R0
    0b00000000,
    0b00000001, # HLT
]

# HLT = 0b00000001
# LDI = 0b10000010
# PRN = 0b01000111

# Create instance
cpu = CPU()
# Load program into RAM
cpu.load(program)
# Start execution loop
cpu.run()