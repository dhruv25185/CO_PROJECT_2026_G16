rt={
"x0":0,"x1":1,"x2":2,"x3":3,"x4":4,"x5":5,"x6":6,"x7":7,
"x8":8,"x9":9,"x10":10,"x11":11,"x12":12,"x13":13,"x14":14,"x15":15,
"x16":16,"x17":17,"x18":18,"x19":19,"x20":20,"x21":21,"x22":22,"x23":23,
"x24":24,"x25":25,"x26":26,"x27":27,"x28":28,"x29":29,"x30":30,"x31":31,
"zero":0,"ra":1,"sp":2,"gp":3,"tp":4,
"t0":5,"t1":6,"t2":7,
"s0":8,"fp":8,"s1":9,
"a0":10,"a1":11,"a2":12,"a3":13,"a4":14,"a5":15,"a6":16,"a7":17,
"s2":18,"s3":19,"s4":20,"s5":21,"s6":22,"s7":23,"s8":24,"s9":25,"s10":26,"s11":27,
"t3":28,"t4":29,"t5":30,"t6":31
}
ft={
"add":"R","sub":"R","slt":"R","sltu":"R","xor":"R","sll":"R","srl":"R","or":"R","and":"R",
"lw":"I","addi":"I","sltiu":"I","jalr":"I",
"sw":"S",
"beq":"B","bne":"B","blt":"B","bge":"B","bgeu":"B","bltu":"B",
"lui":"U","auipc":"U",
"jal":"J"
}
opcode={
"R":"0110011",
"lw":"0000011",
"addi":"0010011",
"sltiu":"0010011",
"jalr":"1100111",
"sw":"0100011",
"B":"1100011",
"lui":"0110111",
"auipc":"0010111",
"jal":"1101111"
}
funct3={
"add":"000","sub":"000","sll":"001","slt":"010","sltu":"011",
"xor":"100","srl":"101","or":"110","and":"111",
"lw":"010","addi":"000","sltiu":"011","jalr":"000",
"sw":"010",
"beq":"000","bne":"001","blt":"100","bge":"101","bltu":"110","bgeu":"111"
}
funct7={
"add":"0000000",
"sub":"0100000",
"sll":"0000000",
"slt":"0000000",
"sltu":"0000000",
"xor":"0000000",
"srl":"0000000",
"or":"0000000",
"and":"0000000"
}

binN @nirney

def error(message):
    print(message)
    sys.exit(1)

def reg(reg,line_num):
    if reg.lower() not in rt:
        error(f"Line {line_num}: Invalid register '{reg}'")
    return rt[reg.lower()]

def imm(hex):
    try:
        if hex.startswith("0x"):
            return int(hex,16)
        if hex.startswith("0b"):
            return int(hex,2)
        return int(hex)
    except:
        error(f"Invalid immediate '{hex}'")

def check_range(value,bits,line_num):
    low=-(1<<(bits-1))
    high=(1<<(bits-1))-1
    if value<low or value>high:
        error(f"Line {line_num}: Immediate {value} out of range for {bits}-bit field")

def check_label(name,line_num):
    if not name[0].isalpha():
        error(f"Line {line_num}: Invaild label '{name}'")
    if name in rt or name in ft:
        error(f"Line {line_num}: Label cannot be register or instruction name")

def first_pass(lines):

    labels={}
    instructions=[]
    addr=0

    for i,line in enumerate(lines):

        line=line.strip()

        if line=="":
            continue

        if ":" in line:

            name=line[:line.index(":")].strip()
            check_label(name,i+1)

            if name in labels:
                error(f"Line {i+1}: Duplicate label '{name}'")

            labels[name]=addr

            rest=line[line.index(":")+1:].strip()

            if rest=="":
                continue

            line=rest

        instructions.append((i+1,addr,line))
        addr+=4

    return labels,instructions
