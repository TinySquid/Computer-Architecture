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
            # NOP
            0x00: lambda: self._NOP(),
            # HLT
            0x01: lambda: exit(),
            # PRA
            0x48: lambda: self._PRA(self._operand_a),
            # PRN
            0x47: lambda: self._PRN(self._operand_a),
            # LD
            0x83: lambda: self._LD(self._operand_a, self._operand_b),
            # LDI
            0x82: lambda: self._LDI(self._operand_a, self._operand_b),
            # ST
            0x84: lambda: self._ST(self._operand_a, self._operand_b),
            # PUSH
            0x45: lambda: self._PUSH(self._operand_a),
            # POP
            0x46: lambda: self._POP(self._operand_a),
            # CALL
            0x50: lambda: self._CALL(self._operand_a),
            # RET
            0x11: lambda: self._RET(),
            # INT
            0x52: lambda: self._INT(self._operand_a),
            # IRET
            0x13: lambda: self._IRET(),
            # JMP
            0x54: lambda: self._JMP(self._operand_a),
            # JLT
            0x58: lambda: self._JLT(self._operand_a),
            # JGT
            0x57: lambda: self._JGT(self._operand_a),
            # JEQ
            0x55: lambda: self._JEQ(self._operand_a),
            # JLE
            0x59: lambda: self._JLE(self._operand_a),
            # JGE
            0x5A: lambda: self._JGE(self._operand_a),
            # JNE
            0x56: lambda: self._JNE(self._operand_a)
        }

        # All alu instructions
        self.alu_instructions = {
            # ADD
            0xA0: lambda: self._ALU_ADD(self._operand_a, self._operand_b),
            # SUB
            0xA1: lambda: self._ALU_SUB(self._operand_a, self._operand_b),
            # MUL
            0xA2: lambda: self._ALU_MUL(self._operand_a, self._operand_b),
            # DIV
            0xA3: lambda: self._ALU_DIV(self._operand_a, self._operand_b),
            # MOD
            0xA4: lambda: self._ALU_MOD(self._operand_a, self._operand_b),
            # INC
            0x65: lambda: self._ALU_INC(self._operand_a),
            # DEC
            0x66: lambda: self._ALU_DEC(self._operand_a),
            # SHL
            0xAC: lambda: self._ALU_SHL(self._operand_a, self._operand_b),
            # SHR
            0xAD: lambda: self._ALU_SHR(self._operand_a, self._operand_b),
            # AND
            0xA8: lambda: self._ALU_AND(self._operand_a, self._operand_b),
            # OR
            0xAA: lambda: self._ALU_OR(self._operand_a, self._operand_b),
            # XOR
            0xAB: lambda: self._ALU_XOR(self._operand_a, self._operand_b),
            # NOT
            0x69: lambda: self._ALU_NOT(self._operand_a),
            # CMP
            0xA7: lambda: self._ALU_CMP(self._operand_a, self._operand_b),
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

        # Does this instruction set the PC directly?
        updates_pc = True if 0b00010000 & self.ir else False

        # If the instruction doesn't set the PC itself, then we must increment it ourselves
        if not updates_pc:
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

    def _NOP(self):
        # Do nothing
        pass

    def _HLT(self):
        """
        Halts program execution
        """
        exit()

    def _PRA(self, r):
        """
        Prints register r contents as an ASCII character
        """
        print(chr(self.reg[r]))

    def _PRN(self, r):
        """
        Prints value stored in register r
        """
        print(self.reg[r])

    def _LD(self, ra, rb):
        """
        Loads registerA with value at memory address stored in registerB
        """
        self.reg[ra] = self.ram[self.reg[rb]]

    def _LDI(self, r, i):
        """
        Stores immediate i into register r
        """
        self.reg[r] = 0b11111111 & i

    def _ST(self, ra, rb):
        """
        Stores value from registerB into memory at address stored in registerA
        """
        self.ram[self.reg[ra]] = self.reg[rb]

    def _PUSH(self, r):
        """
        Push value in register r onto stack
        """
        # Decrement stack pointer
        self.reg[self.spr] -= 1

        # Copy value from register r to stack at address SP
        self.ram[self.reg[self.spr]] = self.reg[r]

    def _POP(self, r):
        """
        Pop value at top of stack into register r
        """
        # Copy value from address pointed to by SP into register r
        self.reg[r] = self.ram[self.reg[self.spr]]

        # Increment SP
        self.reg[self.spr] += 1

    def _CALL(self, r):
        """
        Pushes PC + 2 onto stack and then jumps to address in register r
        """
        # Dec SP
        self.reg[self.spr] -= 1
        # Push next instruction address onto stack
        self.ram[self.reg[self.spr]] = self.pc + 2
        # Set PC to address stored in register r
        self.pc = self.reg[r]

    def _RET(self):
        """
        Pops address from previous CALL and stores it in PC
        """
        # Pop ram[SP] into PC
        self.pc = self.ram[self.reg[self.spr]]
        # Inc SP
        self.reg[self.spr] += 1

    def _INT(self, r):
        """
        Issue interrupt number stored in register r
        Sets nth_bit in register IS
        """
        pass

    def _IRET(self):
        """
        Returns from interrupt (Restores processor state)
        """
        pass

    def _JMP(self, r):
        """
        Jumps to address in register r
        """
        self.pc = self.reg[r]

    def _JLT(self, r):
        """
        Jumps to address in register r if less-than flag is set
        """
        if self.fl & 0b00000100:
            self.pc = self.reg[r]
        else:
            self.pc += 2

    def _JGT(self, r):
        """
        Jumps to address in register r if greater-than flag is set
        """
        if self.fl & 0b00000010:
            self.pc = self.reg[r]
        else:
            self.pc += 2

    def _JEQ(self, r):
        """
        Jumps to address in register r if equal flag is set
        """
        if self.fl & 0b00000001:
            self.pc = self.reg[r]
        else:
            self.pc += 2

    def _JLE(self, r):
        """
        Jumps to address in register r if less-than or equal flag is set
        """
        if self.fl & 0b00000101:
            self.pc = self.reg[r]
        else:
            self.pc += 2

    def _JGE(self, r):
        """
        Jumps to address in register r if equal flag or greater-than flag is set
        """
        if self.fl & 0b00000011:
            self.pc = self.reg[r]
        else:
            self.pc += 2

    def _JNE(self, r):
        """
        If equal flag not set, jump to address in register r
        """
        if self.fl ^ 0b00000001:
            self.pc = self.reg[r]
        else:
            self.pc += 2

    """
    ******************************************************
    ALU INSTRUCTION DEFINITIONS
    ******************************************************
    """
    def _ALU_ADD(self, ra, rb):
        """
        Adds registerA with registerB, stores result in registerA
        """
        self.reg[ra] = (self.reg[ra] + self.reg[rb]) & 0b11111111

    def _ALU_SUB(self, ra, rb):
        """
        Subtracts registerB from registerA, stores result in registerA        
        """
        self.reg[ra] = (self.reg[ra] - self.reg[rb]) & 0b11111111
    
    def _ALU_MUL(self, ra, rb):
        """
        Multiplies registerA with registerB, stores result in registerA
        """
        self.reg[ra] = (self.reg[ra] * self.reg[rb]) & 0b11111111

    def _ALU_DIV(self, ra, rb):
        """
        Divides registerA with registerB, stores value in registerA
        Halts on division by 0
        """
        if self.reg[rb] == 0:
            print("Cannot divide by 0!")
            exit()
        else:
            self.reg[ra] = self.reg[ra] // self.reg[rb]
    
    def _ALU_MOD(self, ra, rb):
        """
        Divides registerA with registerB, stores remainder in registerA
        Halts on division by 0
        """
        if self.reg[rb] == 0:
            print("Cannot divide by 0!")
            exit()
        else:
            self.reg[ra] = int(self.reg[ra] % self.reg[rb])

    def _ALU_INC(self, r):
        """
        Increments register r        
        """
        self.reg[r] = (self.reg[r] + 1) & 0b11111111
        
    def _ALU_DEC(self, r):
        """
        Decrements register r        
        """
        self.reg[r] = (self.reg[r] - 1) & 0b11111111

    def _ALU_AND(self, ra, rb):
        """
        Bitwise AND the values in registerA with registerB, stores result in registerA
        """
        self.reg[ra] = self.reg[ra] & self.reg[rb]

    def _ALU_OR(self, ra, rb):
        """
        Bitwise OR the values in registerA with registerB, stores result in registerA
        """
        self.reg[ra] = self.reg[ra] | self.reg[rb]

    def _ALU_XOR(self, ra, rb):
        """
        Bitwise XOR between values in registerA and registerB, stores result in registerA
        """
        self.reg[ra] = self.reg[ra] ^ self.reg[rb]

    def _ALU_NOT(self, r):
        """
        Bitwise NOT the value in register r
        """
        self.reg[r] = ~self.reg[r]

    def _ALU_SHL(self, ra, rb):
        """
        Shifts value in registerA left by number of bits in registerB
        """
        self.reg[ra] = (self.reg[ra] << self.reg[rb]) & 0b11111111
    
    def _ALU_SHR(self, ra, rb):
        """
        Shifts value in registerA right by number of bits in registerB
        """
        self.reg[ra] = self.reg[ra] >> self.reg[rb]

    def _ALU_CMP(self, ra, rb):
        """
        Flag register format:
        00000LGE
        L: Less Than
        G: Greater Than
        E: Equal To

        """
        if self.reg[ra] > self.reg[rb]:
            self.fl = 0b00000010
        elif self.reg[ra] < self.reg[rb]:
            self.fl = 0b00000100
        else: # ==
            self.fl = 0b00000001