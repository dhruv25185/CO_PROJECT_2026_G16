#Dhruv's Part#
#Dhruv's Part#

#Aryan's Part#
data_base  = 0x00010000   #data memory starts at this address
stack_base = 0x00000100   #stack memory starts at this address

#reads value from mmemory based on address 
def mem_read(addr, data_mem, stack_mem):
    if addr % 4 != 0:
        return None, "unaligned" #address is not a multiple of 4
    if data_base <= addr < data_base + 32*4:
        return data_mem[(addr - data_base)//4], None
    if stack_base <= addr < stack_base + 32*4:
        return stack_mem[(addr - stack_base)//4], None
    return None, "oob"
#writes value from memory based on adress
def mem_write(addr, value, data_mem, stack_mem):
    if addr % 4 != 0:
        return "unaligned"
    if data_base <= addr < data_base + 32*4:
        data_mem[(addr - data_base)//4] = value & ((1<<32)-1)
        return None
    if stack_base <= addr < stack_base + 32*4:
        stack_mem[(addr - stack_base)//4] = value & ((1<<32)-1)
        return None
    return "oob" #addressnot in allowed mem range
#note-alignment and range validation also happen in memread and memwrite

#main driver function execute which does the ALU operations and branching and basically the logical operations and updation of the registers with corresponding values and also updates prog counter after carrying out instructions
def execute(decoded, registers, data_mem, stack_mem, PC):
    m=decoded["mnemonic"]
    fmt=decoded["format"]
    new_PC=PC+4

    if fmt=="R":
        if m=="add":
            registers[decoded["rd"]]=(registers[decoded["rs1"]]+registers[decoded["rs2"]]) & ((1<<32)-1)
        elif m=="sub":
            registers[decoded["rd"]]=(registers[decoded["rs1"]]-registers[decoded["rs2"]]) & ((1<<32)-1)
        elif m=="sll":
            registers[decoded["rd"]]=(registers[decoded["rs1"]]<<(registers[decoded["rs2"]] & 0x1F)) & ((1<<32)-1)
        elif m=="slt":
            registers[decoded["rd"]] = int(tosignedbinary(registers[decoded["rs1"]]) < tosignedbinary(registers[decoded["rs2"]]))
        elif m=="sltu":
            registers[decoded["rd"]]=int((registers[decoded["rs1"]]&((1<<32)-1)) < (registers[decoded["rs2"]]&((1<<32)-1)))
        elif m=="xor":
            registers[decoded["rd"]]=(registers[decoded["rs1"]]^registers[decoded["rs2"]]) & ((1<<32)-1)
        elif m=="srl":
            registers[decoded["rd"]]=((registers[decoded["rs1"]]&((1<<32)-1))>>(registers[decoded["rs2"]]& 0x1F)) & ((1<<32)-1)
        elif m=="or":
            registers[decoded["rd"]]=(registers[decoded["rs1"]] | registers[decoded["rs2"]]) & ((1<<32)-1)
        elif m=="and":
            registers[decoded["rd"]]=(registers[decoded["rs1"]] & registers[decoded["rs2"]]) & ((1<<32)-1)

    elif fmt=="I":
        if m=="addi":
            registers[decoded["rd"]]=(registers[decoded["rs1"]]+decoded["imm"]) & ((1<<32)-1)
        elif m=="sltiu":
            registers[decoded["rd"]]=int((registers[decoded["rs1"]]&((1<<32)-1)) < (decoded["imm"]&((1<<32)-1)))
        elif m=="lw":
            addr=(registers[decoded["rs1"]]+decoded["imm"]) & ((1<<32)-1)
            val, err = mem_read(addr, data_mem, stack_mem)
            if err == "unaligned":
                print("Error: Unaligned memory access")
                return None
            if err == "oob":
                print("Error: Memory access out of bounds")
                return None
            registers[decoded["rd"]] = val & ((1<<32)-1)
        elif m=="jalr":
            temp=PC+4
            new_PC=(((registers[decoded["rs1"]]+decoded["imm"]) & ((1<<32)-1))& (~1))
            registers[decoded["rd"]]=temp

    elif fmt=="S":
        if m=="sw":
            addr=(registers[decoded["rs1"]]+decoded["imm"]) & ((1<<32)-1)
            err = mem_write(addr, registers[decoded["rs2"]], data_mem, stack_mem)
            if err == "unaligned":
                print("Error: Unaligned memory access")
                return None
            if err == "oob":
                print("Error: Memory access out of bounds")
                return None

    elif fmt=="B":
        if m=="beq":
            if registers[decoded["rs1"]]==registers[decoded["rs2"]]:
                new_PC=(PC+decoded["imm"])& ((1<<32)-1)
        elif m=="bne":
            if registers[decoded["rs1"]]!=registers[decoded["rs2"]]:
                new_PC=(PC+decoded["imm"])& ((1<<32)-1)
        elif m=="blt":
            if tosignedbinary(registers[decoded["rs1"]]) < tosignedbinary(registers[decoded["rs2"]]):
                new_PC=(PC+decoded["imm"]) & ((1<<32)-1)
        elif m=="bge":
            if tosignedbinary(registers[decoded["rs1"]]) >= tosignedbinary(registers[decoded["rs2"]]):
                new_PC=(PC+decoded["imm"]) & ((1<<32)-1)
        elif m=="bltu":
            if (registers[decoded["rs1"]]&((1<<32)-1))<(registers[decoded["rs2"]]&((1<<32)-1)):
                new_PC=(PC+decoded["imm"]) & ((1<<32)-1)
        elif m=="bgeu":
            if (registers[decoded["rs1"]]&((1<<32)-1))>=(registers[decoded["rs2"]]&((1<<32)-1)):
                new_PC=(PC+decoded["imm"]) & ((1<<32)-1)

    elif fmt=="U":
        if m=="lui":
            registers[decoded["rd"]]=decoded["imm"] & ((1<<32)-1)
        elif m=="auipc":
            registers[decoded["rd"]]=(PC+decoded["imm"]) & ((1<<32)-1)

    elif fmt=="J":
        if m=="jal":
            registers[decoded["rd"]]=PC+4
            new_PC=(PC+decoded["imm"]) & ((1<<32)-1)

    registers[0]=0
    return new_PC
#Aryan's Part#

#Astu's Part#
#Astu's Part#

#Nirney's Part#
#Nirney's Part#
