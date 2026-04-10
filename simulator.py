#Dhruv's Part#
import sys
#converts input number to 32 bit binary no.
def converttobin(x):
    return "0b"+format(x & ((1<<32)-1), '032b')

#takes the encoded binary file and reads the 32 bit instructions and returns them
def loadprogram(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip()]
    
def tosignedbinary(x):
    if x & (1 << 31):
        return x - (1 << 32)
    return x

def signext(value, nbits):
    if (value&(1<< (nbits - 1))):
        value=value -(1<< nbits)
    return value

#the purpose of this function is to take the binary 32 bit string break it down and further segregate on the basis of opcode then accordingly
#update values of registers 
def decode(binaryinput):
    if len(binaryinput)!=32:
        return {"mnemonic":"UNKNOWN","format":"?","error":True}
    opcode =  binaryinput[25:32]
    if opcode =="0110011":
        funct7=binaryinput[0:7]
        rs2=int(binaryinput[7:12],2)
        rs1 =int(binaryinput[12:17],2)
        funct3=binaryinput[17:20]
        rd=int(binaryinput[20:25], 2)
        operator_codes ={
            ("000","0000000"): "add",
            ("000","0100000"): "sub",
            ("001","0000000"): "sll",
            ("010","0000000"): "slt",
            ("011","0000000"): "sltu",
            ("100","0000000"): "xor",
            ("101","0000000"): "srl",
            ("110","0000000"): "or",
            ("111","0000000"): "and",
        }
        key= (funct3, funct7)
        if key not in operator_codes:
            return {"mnemonic":"UNKNOWN", "format":"R", "error":True}
        return{
            "format": "R",
            "mnemonic": operator_codes[key],
            "rs1": rs1,
            "rd": rd,
            "rs2": rs2
        }
    elif opcode =="0000011":
        imm_raw= int(binaryinput[0:12],2)
        funct3  = binaryinput[17:20]
        rs1      = int(binaryinput[12:17], 2)
        rd =int(binaryinput[20:25],2)
        if funct3 != "010":
            return {"mnemonic":"UNKNOWN", "format":"I", "error":True}
        return{
            "rd":rd,
            "mnemonic":"lw",
            "rs1":rs1,
            "format":  "I",
            "imm":signext(imm_raw, 12)
        }
    elif opcode =="0010011":
        imm_raw= int(binaryinput[0:12], 2)
        rs1= int(binaryinput[12:17], 2)
        funct3= binaryinput[17:20]
        rd= int(binaryinput[20:25], 2)
        icodes={
            "000":"addi",
            "011": "sltiu",
        }
        if funct3 not in icodes:
            return {"mnemonic":"UNKNOWN", "format":"I", "error":True}
        return{
            "rd": rd,
            "format": "I",
            "rs1": rs1,
            "imm": signext(imm_raw, 12),
            "mnemonic": icodes[funct3]
        }
    elif opcode =="1100111":
        imm_raw =int(binaryinput[0:12],2)
        rs1    = int(binaryinput[12:17], 2)
        funct3=binaryinput[17:20]
        rd=int(binaryinput[20:25],2)
        if funct3 != "000":
            return {"mnemonic":"UNKNOWN", "format":"I", "error":True}
        return {
            "mnemonic": "jalr",
            "format": "I",
            "rd": rd,
            "imm": signext(imm_raw, 12),
            "rs1": rs1
        }
    elif opcode== "0100011":
        immu=binaryinput[0:7]
        rs2=int(binaryinput[7:12], 2)
        rs1=int(binaryinput[12:17], 2)
        funct3=binaryinput[17:20]
        imml=binaryinput[20:25]
        if funct3 !="010":
            return {"mnemonic":"UNKNOWN", "format":"S", "error":True}
        imm_raw =int(immu + imml, 2)
        return{
            "mnemonic": "sw",
            "rs1": rs1,
            "rs2": rs2,
            "imm": signext(imm_raw, 12),
            "format": "S"
        }
    elif opcode == "1100011":
        imm12=binaryinput[0]
        imm10_5 =binaryinput[1:7]
        rs2=int(binaryinput[7:12], 2)
        rs1=int(binaryinput[12:17], 2)
        funct3=binaryinput[17:20]
        imm4_1=binaryinput[20:24]
        imm11 =binaryinput[24]
        imm_bin = imm12 + imm11 + imm10_5 + imm4_1 + "0"
        imm_val=signext(int(imm_bin, 2), 13)
        bcodes ={
            "000":"beq",
            "001": "bne",
            "100":"blt",
            "101":"bge",
            "110" :"bltu",
            "111":"bgeu",
        }
        if funct3 not in bcodes:
            return {"mnemonic":"UNKNOWN", "format":"B", "error":True}
        return {
            "mnemonic": bcodes[funct3],
            "rs1": rs1,
            "format": "B",
            "rs2": rs2,
            "imm": imm_val
        }
    elif opcode =="0110111":
        imm_raw=int(binaryinput[0:20],2)
        rd =int(binaryinput[20:25],2)
        return{
            "format": "U",
            "rd": rd,
            "mnemonic": "lui",
            "imm": signext(imm_raw, 20)*4096
        }
    elif opcode =="0010111":
        imm_raw=int(binaryinput[0:20], 2)
        rd=int(binaryinput[20:25], 2)
        return{
            "mnemonic": "auipc",
            "rd": rd,
            "imm": signext(imm_raw, 20)*4096,
            "format": "U"
        }
    elif opcode =="1101111":
        rd=int(binaryinput[20:25], 2)
        imm20= binaryinput[0]
        imm10_1= binaryinput[1:11]
        imm11= binaryinput[11]
        imm19_12 =binaryinput[12:20]
        imm_bin =imm20 +imm19_12 +imm11 +imm10_1 +"0"
        imm_val =signext(int(imm_bin, 2), 21)
        return{
            "mnemonic": "jal",
            "format": "J",
            "rd": rd,
            "imm": imm_val
        }
    else:
        return {"mnemonic":"UNKNOWN","format":"?","opcode":opcode,"error":True}
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
def main():
    if len(sys.argv)<3:
        print("Correct Format: python simulator.py input.txt output.txt")
        sys.exit(1)

    encodedfile=sys.argv[1]
    outputfile=sys.argv[2]
    print("\n") #just added this to make the output results less cramped up for test cases
    program=loadprogram(encodedfile)
    run(program, outputfile)

if __name__=="__main__":
    main()
#Nirney's Part#
