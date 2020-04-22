; ALU TEST
; Runs through every ALU opcode except for CMP

; MAIN
    LDI R0, 0x05        ; Load 5 into R0
    LDI R1, 0x3         ; Load 3 into R1
    ADD R0, R1          ; R0 + R1 -> 8
    PRN R0              ; Should be 8
    LDI R3, 0x05        ; Load 5 into R3
    SUB R0, R3          ; R0 - R3 -> 3  
    PRN R0              ; Should be 3
    LDI R2, 0x0A        ; Load 10 into R2
    MUL R0, R2          ; R0 * R2 -> 30
    PRN R0              ; Should be 30
    DIV R0, R3          ; R0 / R3 -> 6
    PRN R0              ; Should be 6
    LDI R1, 0x05        
    MOD R0, R1          ; R0 % R1 -> 1
    PRN R0              ; Should be 1
    INC R0              ; Increment R0
    INC R0
    PRN R0              ; Should be 3
    DEC R0              ; Decrement R0
    PRN R0              ; Should be 2
    LDI R1, 0x02        ; Load 1 into R1
    SHL R0, R1          
    PRN R0              ; Should be 8
    SHR R0, R1          
    PRN R0              ; Should be 2
    LDI R0, 0x07
    LDI R1, 0x03
    AND R0, R1
    PRN R0              ; Should be 3
    LDI R1, 0x07
    OR R0, R1           
    PRN R0              ; Should be 7
    NOT R0
    PRN R0              ; Should be -8
    NOT R0
    PRN R0              ; Should be 7 again
    LDI R1, 0x02
    SHL R0, R1
    PRN R0              ; Should be 28
    LDI R1, 0x07
    XOR R0, R1
    PRN R0              ; Should be 27
    HLT                 ; Yay we're done! :) 