"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Program Counter
        # Holds address of currently executing instruction
        self.pc = 0

        # Instruction Register
        # Holds currently executing instruction
        self.ir = 0

        # Memory Address Register
        # Holds address of memory to read from / write to
        # self.mar = 0

        # Memory Data Register
        # Holds data to write / just read
        # self.mdr = 0

        # Flag register
        # Holds current flags status, changed on CMP
        # Format: 00000LGE - Less Than, Greater Than, Equal
        # AAA -> BBB comparison
        self.fl = 0

        # RAM - LS8 has 1 byte addressing so only 256 possible locations to read from / write to
        self.ram = [0] * 256

        # General Purpose Registers
        # The following are reserved:
        # R5 - Interrupt Mask (IM)
        # R6 - Interrupt Status (IS)
        # R7 - Stack Pointer (SP)
        self.reg = [0] * 8

        self.imr = 5
        self.isr = 6
        self.spr = 7

        self.reg[7] = 0xF4

        # All non-alu instructions understood by the CPU
        self.instructions = {
            # HLT
            0x01: lambda: exit(),
            # LDI
            0x82: lambda: self._LDI(self._operand_a, self._operand_b),
            # PUSH
            0x45: lambda: self._PUSH(self._operand_a),
            # POP
            0x46: lambda: self._POP(self._operand_a),
            # PRN
            0x47: lambda: self._PRN(self._operand_a),
        }

        # All alu instructions
        self.alu_instructions = {
            # MUL
            0xA2: lambda: self._ALU_MUL(self._operand_a, self._operand_b),
        }

    @property
    def _operand_a(self):
        return self.ram[self.pc + 1]

    @property
    def _operand_b(self):
        return self.ram[self.pc + 2]

    def load(self, input_file):
        """Loads a program from a file into memory."""
        address = 0

        # Open program file, loop -> parse line (ignore comments), store into memory at address, inc address
        program_file = open(input_file, "r")

        for line in program_file:
            # Remove whitespace
            line = line.strip()

            # Ignore blank lines
            if not line:
                continue

            # Ignore lines that start with comments
            if line[0] == "#":
                continue

            # All instructions are 1 byte so just
            # take the first 8 chars and convert
            # to a binary number
            instruction = int(line[:8], 2)

            # Insert instruction into memory
            self.ram[address] = instruction

            # Inc to next pos in memory
            address += 1

        program_file.close()

    def _ram_read(self, mar):
        """
        Reads and returns data from RAM at address specified by the MAR
        """
        return self.ram[mar]

    def _ram_write(self, mar, mdr):
        """
        Writes data from MDR into RAM at address specified by the MAR
        """
        self.ram[mar] = mdr

    def _alu(self, op):
        """Executes ALU operations"""

        # This will pull the correct function for the provided alu instruction
        execute = self.alu_instructions.get(op, None)

        # Check if valid instruction
        if execute is not None:
            execute()
        else:
            print("Unsupported ALU operation.")
            self._trace()
            exit(1)

    def _trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self._ram_read(self.pc),
                self._ram_read(self.pc + 1),
                self._ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def _read_instruction(self):
        """
        Load instruction from RAM[pc] into the IR 
        """
        self.ir = self._ram_read(self.pc)

    def _execute_instruction(self):
        """
        Executes instruction located in the IR
        """
        # Get instruction from IR
        instruction = self.ir

        # How many operands does this instruction require?
        # Used for incrementing the PC by correct amount
        operands = (0b11000000 & self.ir) >> 6

        # Is this an ALU operation?
        is_alu_op = True if 0b00100000 & self.ir else False

        # Make the ALU handle instruction if this is an ALU operation
        if is_alu_op:
            self._alu(instruction)
        else:
            # This will pull the correct function for the provided non-alu instruction
            execute = self.instructions.get(self.ir, None)

            # Check if valid instruction
            if execute is not None:
                execute()
            else:
                print("Unknown instruction encountered.")
                self._trace()
                exit(1)

        # Increment program counter by instruction length
        # Determined by last 2 bits of instruction for the operands + 1 for the instruction itself
        self.pc += 1 + operands

    def run(self, trace_cycle=False):
        """Starts the emulator execution loop"""
        while True:
            # Load instruction from RAM at address PC into IR
            self._read_instruction()

            # Print trace if param set
            if trace_cycle:
                self._trace()

            # Execute instruction loaded in IR
            self._execute_instruction()

    """
    ******************************************************
    INSTRUCTION DEFINITIONS
    ******************************************************
    """

    def _HLT(self):
        """
        Halts program execution
        """
        exit()

    def _LDI(self, r, i):
        """
        Stores immediate i into register r
        """
        self.reg[r] = i

    def _PRN(self, r):
        """
        Prints value stored in register r
        """
        print(self.reg[r])

    def _PUSH(self, r):
        """
        Push value in register r onto stack
        """
        # Decrement stack pointer
        self.reg[self.spr] -= 1
        # Copy value from register r to stack at address from SP
        self.ram[self.reg[self.spr]] = self.reg[r]

    def _POP(self, r):
        """
        Pop value at top of stack into register r
        """
        # Copy value from address pointed to by SP into register r
        self.reg[r] = self.ram[self.reg[self.spr]]

        # Increment SP
        self.reg[self.spr] += 1

    """
    ******************************************************
    ALU INSTRUCTION DEFINITIONS
    ******************************************************
    """

    def _ALU_MUL(self, ra, rb):
        """
        Multiplies registerA with registerB, stores result in registerA
        """
        self.reg[ra] *= self.reg[rb]
