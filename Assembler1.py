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

def bfN(value,bits):
 if value < 0:
  value=(1<<bits)+value
 return format(value,"0{}b".format(bits))

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
 
def parse(instructions,labels):

 out=[]

 for ln,addr,text in instructions:

  parts=text.split()
  op=parts[0]

  if op not in ft:
   error(f"Line {ln}: Unknown instruction '{op}'")

  operands=[]
  if len(parts)>1:
   operands=" ".join(parts[1:]).split(",")

  operands=[x.strip() for x in operands]

  ir={"mnemonic":op,"format":ft[op],"address":addr,"line":ln}

  #for R TYPE
  if ft[op]=="R":

   if len(operands)!=3:
    error(f"Line {ln}: '{op}' expects 3 operands")

   ir["rd"]=reg(operands[0],ln)
   ir["rs1"]=reg(operands[1],ln)
   ir["rs2"]=reg(operands[2],ln)

  #for I TYPE
  elif ft[op]=="I":

   if op=="lw":

    if len(operands)!=2:
     error(f"Line {ln}: lw syntax is lw rd,imm(rs1)")

    rd=reg(operands[0],ln)
    p=operands[1]

    off=p[:p.index("(")]
    r=p[p.index("(")+1:-1]

    im=imm(off)
    check_range(im,12,ln)

    ir["rd"]=rd
    ir["rs1"]=reg(r,ln)
    ir["imm"]=im

   else:

    if len(operands)!=3:
     error(f"Line {ln}: '{op}' expects 3 operands")

    im=imm(operands[2])
    check_range(im,12,ln)

    ir["rd"]=reg(operands[0],ln)
    ir["rs1"]=reg(operands[1],ln)
    ir["imm"]=im

  #fro S TYPE
  elif ft[op]=="S":

   if len(operands)!=2:
    error(f"Line {ln}: sw syntax is sw rs2,imm(rs1)")

   rs2=reg(operands[0],ln)

   p=operands[1]
   off=p[:p.index("(")]
   r=p[p.index("(")+1:-1]

   im=imm(off)
   check_range(im,12,ln)

   ir["rs2"]=rs2
   ir["rs1"]=reg(r,ln)
   ir["imm"]=im

  #for B TYPE
  elif ft[op]=="B":

   if len(operands)!=3:
    error(f"Line {ln}: '{op}' expects 3 operands")

   ir["rs1"]=reg(operands[0],ln)
   ir["rs2"]=reg(operands[1],ln)

   t=operands[2]

   if t in labels:
    im=labels[t]-addr
   else:
    if t.isalpha():
     error(f"Line {ln}: Undefined label '{t}'")
    im=imm(t)

   if im%2!=0:
    error(f"Line {ln}: Branch offset must be multiple of 2")

   check_range(im,13,ln)

   ir["imm"]=im

  #for U TYPE
  elif ft[op]=="U":

   if len(operands)!=2:
    error(f"Line {ln}: '{op}' expects 2 operands")

   im=imm(operands[1])
   check_range(im,20,ln)

   ir["rd"]=reg(operands[0],ln)
   ir["imm"]=im

  #for J TYPE
  elif ft[op]=="J":

   if len(operands)!=2:
    error(f"Line {ln}: jal syntax is jal rd,label")

   ir["rd"]=reg(operands[0],ln)

   t=operands[1]

   if t in labels:
    im=labels[t]-addr
   else:
    if t.isalpha():
     error(f"Line {ln}: Undefined label '{t}'")
    im=imm(t)

   if im%2!=0:
    error(f"Line {ln}: Jump offset must be multiple of 2")

   check_range(im,21,ln)

   ir["imm"]=im

  out.append(ir)

 return out
def encode(ir):
    #this follow the general format as listed in the readme file in the assignment 
    m=ir["mnemonic"]
    if ir["format"]=="R":
        return (
        funct7[m]+
        binN(ir["rs2"],5)+
        binN(ir["rs1"],5)+
        funct3[m]+
        binN(ir["rd"],5)+
        opcode["R"]
        )
    if ir["format"]=="I":
        op=opcode[m] if m in opcode else opcode["addi"]
        return (
        binN(ir["imm"],12)+
        binN(ir["rs1"],5)+
        funct3[m]+
        binN(ir["rd"],5)+
        op
        )
    if ir["format"]=="S":
        imm=binN(ir["imm"],12)
        return (
        imm[:7]+
        binN(ir["rs2"],5)+
        binN(ir["rs1"],5)+
        funct3[m]+
        imm[7:]+
        opcode["sw"]
        )
    if ir["format"]=="B":
        imm=binN(ir["imm"],13)
        return (
        imm[0]+
        imm[2:8]+
        binN(ir["rs2"],5)+
        binN(ir["rs1"],5)+
        funct3[m]+
        imm[8:12]+
        imm[1]+
        opcode["B"]
        )
    if ir["format"]=="U":
        return (
        binN(ir["imm"],20)+
        binN(ir["rd"],5)+
        opcode[m]
        )
    if ir["format"]=="J":
        imm=binN(ir["imm"],21)
        return (
        imm[0]+
        imm[10:20]+
        imm[9]+
        imm[1:9]+
        binN(ir["rd"],5)+
        opcode["jal"]
        )
