#*******************************************************************
# Handy Python Reference
#*******************************************************************
# ord('a') -- ASCII string to int 
# chr(97) -- int to ASCII string
# Could call functions dynamically with getattr
# 	for when you have a choice of which functions to call and it depends on something else when to call it. 


#*******************************************************************
# Imports
#*******************************************************************
import re # Regex Library
import sys # for sys.exit()
import enum # for enumerations
from frozendict import frozendict # for an immutable dictionary 


#*******************************************************************
# Global Variables
#*******************************************************************
count = 0

MEM_INST = 30000
MEM_STACK = 30000
MEM_SIZE = MEM_INST + MEM_STACK

# Multi threading tools
MAX_THREADS = 5								# !! determine number of possible threads
THREAD_SIZE = (MEM_STACK // MAX_THREADS) - 1 
MAIN_THREAD = 0								# main thread id
activeThreads = [False] * MAX_THREADS 		# all threads off 
mutexLocks = {}								# will fill with dict values: labelPos => threadId
blockedThreads = [False] * MAX_THREADS 		# all threads off
blocks = []									# queue. Oldest values have smallest indeces
											# will fill with [labelPos,threadId]

mem = bytearray(MEM_SIZE)
reg = [0,0,0,0,0,0,0,0,0,0,0,0,0] # [R0 - R7] general registers.  [R8] PC pointer.  [R9 - R12] Stack Pointers.
PC = 8					  # This is used to easily reference PC register.  
SL = 9
SP = 10
FP = 11
SB = 12
symbolTable = {}

CONST = 0
globalVarsStart = 0
codeStart = 0
assemblyLine = 1
BYT = 1 # 1 byte
INT = 4 # 4 bytes

REGISTER = 0
LABEL = 1
IMMVAL = 2

stackWordSize = 4 #4 Bytes per word on the stack. 

#*******************************************************************
# Functions
#*******************************************************************
# MULTITHREADING HANDLERS ------------------------------------------
# save PC registers into current thread's stack
def save_context():
	stackBase = MEM_SIZE - (currentThread * THREAD_SIZE)
	for index in range(len(reg)):
		valueToSave = reg[index]
		positionToSaveAt = stackBase - INT - (INT * index)
		setIntAt(positionToSaveAt, valueToSave)

# save PC registers into given thread's stack
def duplicate_context(threadId):
	stackBase = MEM_SIZE - (threadId * THREAD_SIZE)
	for index in range(len(reg)):
		valueToSave = reg[index]
		positionToSaveAt = stackBase - INT - (INT * index)
		setIntAt(positionToSaveAt, valueToSave)
	

# load into CPU registers the register values from threadId
# threadId and currentIndex will be the same when we use this
def load_context():
	global reg

	# loop through reg and place into currentThread's stack
	stackBase = MEM_SIZE - (currentThread * THREAD_SIZE)
	for index in range(len(reg)):
		positionToLoadFrom = stackBase - INT - (INT * index)
		reg[index] = getIntAt(positionToLoadFrom) 


def isInBlocks(threadId):
	for index in range(len(blocks)):
		if blocks[index][1] == threadId:
			return index

def tellWaitingThread(label):
	for index in range(len(blocks)):
		# if a thread IS waiting for the label...
		if blocks[index][0] == label:
			# take that block out of the list, but save info in variables
			labelWaitedFor = blocks[index][0]
			waitingThreadId = blocks[index][1]
			blocks.pop(index)

			# unblock the waiting thread
			blockedThreads[waitingThreadId] = False

			# add a mutex lock for the waiting thread (give waiting thread the label)
			mutexLocks[label] = waitingThreadId

			break
		else:
			# if there is no thread waiting for the label
			return

def cleanUp(threadId):
	# clear out mutexLocks associated with curentIndex
	while threadId in mutexLocks.values():
		for label, value in mutexLocks.items():
			# if threadId has this mutex locked, 
			# unlock it (take it out of mutexLocks)
			# and inform any waiting thread the label is available
			if value == threadId:
				mutexLocks.pop(label)
				tellWaitingThread(label)
				break

	# clear out blocks associated to threadId
	while True:
		x = isInBlocks(threadId)
		if x is not None:
			blocks.pop(x)
		else:
			break

# if the current thread tries to read/change something that they did not lock, tell em.  
def isLocked(labelPos):
	if labelPos in mutexLocks: 
		lockingThreadId = mutexLocks[labelPos]
		if currentThread != lockingThreadId:
			return True
	return False



# ================================================================

# MEMEORY HANDLING -------------------------------------------------
# Place a char into the byte array
def setCharAt(pos, asciiCode):
	global mem
	if not inBounds(pos):
		kill('out of bounds')
	if pos < globalVarsStart:
		kill('Cannot change a constant variable')
	mem[pos] = asciiCode

# Pull out an int from the byte array
def getIntAt(pos):
	if not inBounds(pos) or not inBounds(pos + 3):
		kill('out of bounds')
	myIntInBytes = mem[pos:pos+4]
	return int.from_bytes(myIntInBytes, byteorder='little', signed=True)

# Place an int into the byte array
def setIntAt(pos, num):
	global mem
	if not inBounds(pos) or not inBounds(pos + 3):
		kill('out of bounds')
	if pos < globalVarsStart:
		kill('Cannot change a constant variable')
	numBytes = num.to_bytes(4, byteorder='little', signed=True)
	mem[pos:pos + 4] = numBytes

# pull out a char from the byte array
def getCharAt(pos):
	if not inBounds(pos):
		kill('out of bounds')
	return chr(mem[pos])
# ========================================================================


# VALIDATIONS -----------------------------------------------------------
# check if a memory address is in bounds
def inBounds(pos): 
	return (0 <= pos < MEM_SIZE)

def isDirective(token): 
	directives = ['.BYT', '.INT']
	return token in directives

def isInstruction(token): 
	for x in InstructionDic.keys(): 
		if x == token and not isDirective(x): 
			return True
	return False

def isLabel(token): 
	if not token[0].isalpha():
		return False
	if not token.isalnum():
		return False
	return not isDirective(token) and not isInstruction(token)

def isRegister(token): 
	return re.search("R[0-7]|PC|SL|SP|FP|SB", token)
# ========================================================================


# OTHER HELPERS  -------------------------------------------------------------
# end the program with a last message
def kill(message):
	print(message)	
	sys.exit()

# increment global PC variable by passed in value
def incrementPC(byteCount):
	global reg 
	reg[PC] += byteCount

def printRegisters(message):
	print(message)
	for i in range(len(reg)):
		print('    R', i, ': ', reg[i])
# ========================================================================

# ASSEMBLER -------------------------------------------------------------
def assembler(passNum):
	global codeStart
	global assemblyLine
	global globalVarsStart
	global globalsHaveBegun
	global reg
	reg[PC] = 0
	reg[SL] = MEM_SIZE - MEM_STACK
	reg[SP] = MEM_SIZE
	reg[FP] = 0	# null
	reg[SB] = MEM_SIZE
	globalVarsStart = 0
	assemblyLine = 0
	multiLineComment = False

	# open the file
	try:
		f = open(sys.argv[1], "r");
	except IOError: 
		kill('Failed to open assembly file for parsing.') 

	# read file line by line
	codeHasBegun = False
	globalsHaveBegun = False
	for x in f:
		# keep track of which assembly code line we're on for error reporting
		assemblyLine += 1

		# Handle Multiline Comments
		if multiLineComment == False: 
			if "/*" in x:
				multiLineComment = True
				x = x[0:x.index("/*")]
		else:
			if "*/" in x:
				multiLineComment = False
				x = x[x.index("*/") + 2:len(x)]
			else: 
				continue

		# handle single line comments
		if ';' in x: 
			x = x[0:x.index(';')]

		# Split line into tokens (Get rid of empty space tokens and empty arrays)
		tokens = re.split("[\s,]", x)
		while "" in tokens:
			tokens.remove("")
		if tokens == []: 
			continue

		# Mark where constant variables end for making sure constant variables are not changed
		if globalsHaveBegun == False and 'CONST' not in tokens[0]: 
			globalsHaveBegun = True
			globalVarsStart = reg[PC]

		# Check for optional label - if there is a label, place it and current PC into symbolTable and remove the label from the token list.  
		if isLabel(tokens[0]):
			if passNum == 1:
				if tokens[0] in symbolTable:
					kill('DUPLICATE LABEL - ' + str(assemblyLine) + ' label: ' + tokens[0])
				if tokens[0] == 'CONST': 
					kill('INVALID LABEL - ' + str(assemblyLine) + ' - CONST keyword cannot be a label')
				if globalsHaveBegun and 'CONST' in tokens[0]: 
					kill('INVALID CONST VARIABLE - ' + str(assemblyLine) + ' - Declare all constant variables before global variables')
				
				symbolTable[tokens[0]] = reg[PC]
			tokens.pop(0) 
			if tokens == []: 
				continue

		# Save the reg[PC] address where instructions start (directly after directives) and make sure no directives are declared after code begins
		if codeHasBegun == False: 
			if isInstruction(tokens[0]): 
				codeHasBegun = True
				codeStart = reg[PC]
		else: 
			if isDirective(tokens[0]): 
				kill('INVALID DIRECTIVE - ' + str(assemblyLine) + ' - tried to declare directives after code began. Directive: ' + tokens[0]) 


		# Process Tokens
		if '.BYT' in x: 
			dirByt(passNum, tokens)
		elif '.INT' in x: 
			dirInt(passNum, tokens)
		else: 
			assemblerHelper(passNum, tokens) 


		# kill if static data OR instructions have bled into the heap
		if reg[PC] > MEM_INST - 1:
			kill('INSUFFICIENT MEMORY - ' + str(assemblyLine) + ' - Current PC: ' + str(reg[PC]) + ' - Code Memory Size: ' + str(MEM_INST)) 

	# Close the file
	f.close()
# ========================================================================

# ASSEMBLER HELPERS -------------------------------------------------------------
def dirInt(passNum, tokens): 
	# validate token count
	if len(tokens) != 2: 
		kill('INVALID DIRECTIVE - ' + str(assemblyLine))

	number = tokens[1]
	if passNum == 1:
		if not number.lstrip('-').isdigit(): 
			kill('INVALID DIRECTIVE - ' + str(assemblyLine) + ' - data given is not a number.  Data: ' + number)
		incrementPC(INT)
	elif passNum == 2:
		setIntAt(reg[PC], int(number))
		incrementPC(INT)
	else: 
		kill('INVALID PASS NUMBER - dirInt(passNum, tokens) - no fault of programmer')

def dirByt(passNum, tokens): 
	global reg

	# validate token count
	if len(tokens) != 2: 
		kill('INVALID DIRECTIVE - ' + str(assemblyLine))

	# Make sure given data is actually a character
	character = tokens[1]
	x = re.search("^('[\w\W]')$", character)
	y = re.search("^([\d]+)$", character)
	if x: 
		character = ord(character[1]) # strip the quotations and convert to ascii code equivalent
	elif y: 
		character = int(character) # convert to integer ('10' -> 10)
	else: 
		kill('INVALID BYTE DATA - ' + str(assemblyLine) + ' - data: ' + character)

	if passNum == 1:	
		incrementPC(BYT)
	elif passNum == 2:
		setCharAt(reg[PC], character)
		incrementPC(BYT)
	else: 
		kill('INVALID PASS NUMBER - dirByt(passNum, tokens) - no fault of programmer')

def setOperandMemory(op, opType):
	global reg

	if opType == REGISTER: 
		if op == 'PC':
			setIntAt(reg[PC], PC)
		elif op == 'SL':
			setIntAt(reg[PC], SL)
		elif op == 'SP':
			setIntAt(reg[PC], SP)
		elif op == 'FP':
			setIntAt(reg[PC], FP)
		elif op == 'SB':
			setIntAt(reg[PC], SB)
		else:
			setIntAt(reg[PC], int(op[1]))
	elif opType == LABEL: 
		if op not in symbolTable:  
			kill('INVALID LABEL - ' + str(assemblyLine) + ' - "' + str(op) + '" - undeclared label.')
		setIntAt(reg[PC], symbolTable[op])
	elif opType == IMMVAL: 
		setIntAt(reg[PC], int(op))

def validateOperand(op, opType, opcodeName, position):
	if opType == REGISTER: 
		if not isRegister(op):
			kill('INVALID ' + opcodeName + ' - ' + str(assemblyLine) + ' - first operand is not a valid register. op: ' + op)
		if position == 1 and (op == 'PC' ''' or op == 'SL' ''' or op == 'SB'): 
				kill('INVALID ' + opcodeName + ' - ' + str(assemblyLine) + ' - cannot directly modify ' + op + ' register')
	elif opType == LABEL: 
		if not isLabel(op):
			kill('INVALID ' + opcodeName + ' - ' + str(assemblyLine) + ' - first operand is not a valid label. op: ' + op)
	elif opType == IMMVAL: 
		if op[0] == '-': # allow for negatives	
			op = op[1:]
		if not op.isdigit():
			kill('INVALID ' + opcodeName + ' - ' + str(assemblyLine) + ' - data given is not a number. Data: ' + op)

def assemblerHelper(passNum, tokens):
	global count
	global reg

	# Handle Register Indirect
	ftok = tokens[0]
	if (ftok == 'STR' or ftok == 'STB' or ftok == 'LDR' or ftok == 'LDB') and isRegister(tokens[1]) and isRegister(tokens[2]):
		# Then it's a Register Indirect 
		tokens[0] = tokens[0] + 'I'

	ops = InstructionDic[tokens[0]]['ops']

	if len(tokens) != len(ops) + 1: 
		kill('INVALID NUMBER OF OPERANDS - '+ str(assemblyLine))

	# Handle Passes
	opcodeName = tokens[0]
	if passNum == 1: 
		incrementPC(INT)
		if len(ops) > 0:
			validateOperand(tokens[1], ops[0], opcodeName, 1) 
		incrementPC(INT)
		if len(ops) > 1: 
			validateOperand(tokens[2], ops[1], opcodeName, 2)
		incrementPC(INT)
	elif passNum == 2: 
		dictionary = InstructionDic[opcodeName]
		opcode = dictionary['opcode']
		setIntAt(reg[PC], opcode)
		incrementPC(INT)
		if len(ops) > 0:
			setOperandMemory(tokens[1], ops[0])
		incrementPC(INT)
		if len(ops) > 1: 
			setOperandMemory(tokens[2], ops[1])
		incrementPC(INT)
	else: 
		kill('INVALID PASS NUMBER - ' + str(assemblyLine))
# ===============================================================================


# VIRTUAL MACHINE HELPERS -------------------------------------------------------------
# Jump Instructions *****************************
def _jmp(labelPos, wastedSpace): 
	global reg
	reg[PC] = labelPos

def _jmr(rs, wastedSpace):  
	global reg
	reg[PC] = reg[rs]

def _bnz(rs, labelPos): 
	global reg
	if reg[rs] != 0:
		reg[PC] = labelPos

def _bgt(rs, labelPos): 
	global reg
	if reg[rs] > 0:
		reg[PC] = labelPos

def _blt(rs, labelPos): 
	global reg
	if reg[rs] < 0:
		reg[PC] = labelPos

def _brz(rs, labelPos): 
	global reg
	if reg[rs] == 0:
		reg[PC] = labelPos
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# Move Instructions ****************************
def _mov(rd, rs): 
	reg[rd] = reg[rs]

def _lda(rd, labelPos): 
	if labelPos >= codeStart: 
		kill('Tried to use LDA on an instruction. Boo you.')
	reg[rd] = labelPos 

def _str(rs, pos): 
	if isLocked(pos):
		kill('WRITING TO LOCKED MUTEX - tried to write to data that is locked by a different thread')
	setIntAt(pos, reg[rs])

def _ldr(rd, pos): 
	if isLocked(pos):
		kill('WRITING TO LOCKED MUTEX - tried to read data that is locked by a different thread')
	reg[rd] = getIntAt(pos)

def _stb(rs, pos): 
	if isLocked(pos):
		kill('WRITING TO LOCKED MUTEX - tried to write to data that is locked by a different thread')
	setCharAt(pos, reg[rs])

def _ldb(rd, pos):
	if isLocked(pos):
		kill('WRITING TO LOCKED MUTEX - tried to read data that is locked by a different thread') 
	reg[rd] = ord(getCharAt(pos))
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# Arithmatic Instructions **********************
def _add(rd, rs): 
	reg[rd] = reg[rd] + reg[rs]

def _adi(rd, immVal): 
	reg[rd] = reg[rd] + immVal

def _sub(rd, rs): 
	reg[rd] = reg[rd] - reg[rs]	

def _mul(rd, rs): 
	reg[rd] = reg[rd] * reg[rs]

def _div(rd, rs): 
	if reg[rs] == 0: 
		kill('ERROR - Cannot divide by zero')
	reg[rd] = int(reg[rd] / reg[rs])
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# Logical Instructions *************************
def _and(rd, rs): 
	if reg[rd] and reg[rs]: 
		reg[rd] = 1
	else:
		reg[rd] = 0

def _or(rd, rs): 
	if reg[rd] or reg[rs]:
		reg[rd] = 1
	else: 
		reg[rd] = 0
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# Compare Instruction *************************
def _cmp(rd, rs): 
	if reg[rd] > reg[rs]: 
		reg[rd] = 1
	elif reg[rd] < reg[rs]: 
		reg[rd] = -1
	elif reg[rd] == reg[rs]:
		reg[rd] = 0

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def printMem(what):
	global mem
	if what == 'static': 
		print(mem[0:codeStart])

		print(getIntAt(codeStart - 4))
	elif what == 'inst':
		count = 0
		ack = mem[codeStart:MEM_INST - 1]
		for a in ack: 
			print(a, end = ' ')
			count = count + 1
			if count % 4 == 0:
				print('\n', end = '')
			if count % 12 == 0:
				print('\n', end = '')
				
				if ack[count - 12] == 0:
					print((count / 4) / 3)
					return
		print((count / 4) / 3)
	elif what == 'stack':
		print(mem[MEM_SIZE - MEM_STACK:MEM_SIZE - 1])
	else:
		print('derp')

# Traps ****************************************
def _trp(value, wastedSpace): 
	if value == 0: 
		# printMem('stack')
		sys.exit(0)
	elif value == 1: 
		print(reg[3], end = '')
	elif value == 2:
		reg[3] = int(input())
	elif value == 3: 
		# print('currentThread: ', currentThread, ' - ', chr(reg[3]))
		print(chr(reg[3]), end = '')
	elif value == 4:
		firstChar = sys.stdin.read(1)
		if firstChar == '\\':
			secondChar = sys.stdin.read(1)
			if secondChar == 'n':
				reg[3] = ord('\n')
			elif secondChar == 't':
				reg[3] = ord('\t')
			elif secondChar == 'v':
				reg[3] = ord('\v')
			elif secondChar == 'f':
				reg[3] = ord('\f')
			elif secondChar == 'r':
				reg[3] = ord('\r')
		else: 
			reg[3] = ord(firstChar)
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



# Register Indirect ****************************************
def _str_i(rs, rg): 
	if isLocked(reg[rg]):
		kill('WRITING TO LOCKED MUTEX - tried to write to data that is locked by a different thread')
	setIntAt(reg[rg], reg[rs])

def _ldr_i(rd, rg): 
	if isLocked(reg[rg]):
		kill('WRITING TO LOCKED MUTEX - tried to read data that is locked by a different thread')
	reg[rd] = getIntAt(reg[rg])

def _stb_i(rs, rg): 
	if isLocked(reg[rg]):
		kill('WRITING TO LOCKED MUTEX - tried to write to data that is locked by a different thread')
	setCharAt(reg[rg], reg[rs])

def _ldb_i(rd, rg): 
	if isLocked(reg[rg]):
		kill('WRITING TO LOCKED MUTEX - tried to read data that is locked by a different thread')
	reg[rd] = ord(getCharAt(reg[rg]))
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# Multi Threading ********************************************
def _run(rd, labelPos):
	global activeThreads
	global reg 

	foundThreadId = 0
	for threadId in range(len(activeThreads)):
		# find an available thread
		if activeThreads[threadId] == False:
			foundThreadId = threadId
			break
		
	# More than MAX_THREADS threads cannot be spwned 
	if foundThreadId == 0:
		kill('THREAD LIMIT REACHED - Tried to spawn more than ' + str(MAX_THREADS) + ' threads')

	# place found thread in destination register
	reg[rd] = foundThreadId

	# turn on found thread
	activeThreads[foundThreadId] = True

	# copy current thread's registers over to found thread's stack
	duplicate_context(foundThreadId)

	# initialize the found threads special purpose registers
	stackBase = MEM_SIZE - (foundThreadId * THREAD_SIZE)
	stackLimit = MEM_SIZE - (foundThreadId * THREAD_SIZE) - THREAD_SIZE  
	for index in range(len(reg)):
		positionToSaveAt = stackBase - INT - (index * INT)
		value = -1
		if index == PC: 
			value = labelPos
		elif index == SL:
			value = stackLimit
		elif index == SP:
			value = stackBase - (INT * 13) # this accounts for us saving registers at bottom
		elif index == FP:
			value = 0
		elif index == SB:
			value = stackBase - (INT * 13)
		else:	
			continue

		setIntAt(positionToSaveAt, value)





def _end(wastedSpace, wastedSpace2):
	global mutexLocks
	
	# turn off current thread, if it's not the main thread
	if currentThread != MAIN_THREAD:
		activeThreads[currentThread] = False

	cleanUp(currentThread)


def _blk(wastedSpace, wastedSpace2):
	global blockedThreads
	if currentThread == MAIN_THREAD:
		blockedThreads[MAIN_THREAD] = True


def _lck(label, wastedSpace):
	if label in mutexLocks:
		# block currentThread
		blockedThreads[currentThread] = True
		# add block to blocks
		blocks.append([label, currentThread])
	else:
		mutexLocks[label] = currentThread


def _ulk(label, wastedSpace):
	if label not in mutexLocks:
		return # do nothing.  The label is not locked, so no need to unlock it.  
	else:
		if mutexLocks[label] != currentThread:
			return  # do nothing. The label was locked by another thread.  
					# this thread is not allowed to unlock it.  
		else: 
			# since we are the thread that locked the mutex, we are allowed to unlock it. 

			# remove the lock from mutexLocks
			mutexLocks.pop(label)

			# inform any thread waiting for the label that they can have the lock now.  
			tellWaitingThread(label)
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# ========================================================================

InstructionDic = frozendict( {
	".INT" : {
		"mode" : dirInt
	},
	".BYT" : {
		"mode" : dirByt
	},
	"JMP" : {
		"opcode" : 1, 
		"ops" : [LABEL], 
		"method" : _jmp
	}, 
	"JMR" : {
		"opcode" : 2, 
		"ops" : [REGISTER], 
		"method" : _jmr
	},
	"BNZ" : {
		"opcode" : 3, 
		"ops" : [REGISTER, LABEL], 
		"method" : _bnz
	},
	"BGT" : {
		"opcode" : 4, 
		"ops" : [REGISTER, LABEL], 
		"method" : _bgt
	},
	"BLT" : {
		"opcode" : 5, 
		"ops" : [REGISTER, LABEL], 
		"method" : _blt
	}, 
	"BRZ" : {
		"opcode" : 6, 
		"ops" : [REGISTER, LABEL], 
		"method" : _brz
	},
	"MOV" : {
		"opcode" : 7,  
		"ops" : [REGISTER, REGISTER],
		"method" : _mov
	},
	"LDA" : {
		"opcode" : 8,   
		"ops" : [REGISTER, LABEL],
		"method" : _lda
	},
	"STR" : {
		"opcode" : 9, 
		"ops" : [REGISTER, LABEL], 
		"method" : _str
	},
	"LDR" : {
		"opcode" : 10, 
		"ops" : [REGISTER, LABEL], 
		"method" : _ldr
	},
	"STB" : {
		"opcode" : 11, 
		"ops" : [REGISTER, LABEL], 
		"method" : _stb
	},
	"LDB" : {
		"opcode" : 12, 
		"ops" : [REGISTER, LABEL], 
		"method" : _ldb
	},
	"ADD" : {
		"opcode" : 13, 
		"ops" : [REGISTER, REGISTER], 
		"method" : _add
	},
	"ADI" : {
		"opcode" : 14,
		"ops" : [REGISTER, IMMVAL], 
		"method" : _adi
	},
	"SUB" : {
		"opcode" : 15, 
		"ops" : [REGISTER, REGISTER], 
		"method" : _sub
	},
	"MUL" : {
		"opcode" : 16, 
		"ops" : [REGISTER, REGISTER], 
		"method" : _mul
	},
	"DIV" : {
		"opcode" : 17, 
		"ops" : [REGISTER, REGISTER], 
		"method" : _div
	},
	"AND" : {
		"opcode" : 18, 
		"ops" : [REGISTER, REGISTER], 
		"method" : _and
	},
	"OR" : {
		"opcode" : 19, 
		"ops" : [REGISTER, REGISTER], 
		"method" : _or
	},
	"CMP" : {
		"opcode" : 20, 
		"ops" : [REGISTER, REGISTER], 
		"method" : _cmp
	},
	"TRP" : {
		"opcode" : 21, 
		"ops" : [IMMVAL], 
		"method" : _trp
	},
	"STRI" : {
		"opcode" : 22, 
		"ops" : [REGISTER, REGISTER], 
		"method" : _str_i
	},
	"LDRI" : {
		"opcode" : 23, 
		"ops" : [REGISTER, REGISTER], 
		"method" : _ldr_i
	},
	"STBI" : {
		"opcode" : 24, 
		"ops" : [REGISTER, REGISTER], 
		"method" : _stb_i
	},
	"LDBI" : {
		"opcode" : 25, 
		"ops" : [REGISTER, REGISTER], 
		"method" : _ldb_i
	},
	"RUN" : {
		"opcode" : 26,
		"ops" : [REGISTER, LABEL],
		"method" : _run
	},
	"END" : {
		"opcode" : 27,
		"ops" : [],
		"method" : _end 
	},
	"BLK" : {
		"opcode" : 28,
		"ops" : [],
		"method" : _blk 
	},
	"LCK" : {
		"opcode" : 29,
		"ops" : [LABEL],
		"method" : _lck
	},
	"ULK" : {
		"opcode" : 30,
		"ops" : [LABEL],
		"method" : _ulk
	}
})



#*******************************************************************
# Main Program
#*******************************************************************

# Check if user entered a second command line argument
if len(sys.argv) != 2: 
	kill('INVALID CMD ARGS - Incorrect number of command line arguments given to the program.  Usage: <application> <asm file to process>')

# FIRST PASS ----------------------------------------------------------------------
assembler(1)

# SECOND PASS ---------------------------------------------------------------------
assembler(2)

# VIRTUAL MACHINE ------------------------------------------------------------------

# Initialize all threads
for threadId in range(MAIN_THREAD, MAX_THREADS):
	# Figure the thread's stack base and stack limite based on the thread's Id
	stackBase = MEM_SIZE - (threadId * THREAD_SIZE)
	stackLimit = MEM_SIZE - (threadId * THREAD_SIZE) - THREAD_SIZE

	# initialize the thread's registers.  
	for index in range(len(reg)):
		positionToSaveAt = stackBase - INT - (index * INT)
		value = -1
		if index == PC: 
			value = codeStart
		elif index == SL:
			value = stackLimit
		elif index == SP:
			value = stackBase - (INT * 13) # this accounts for us saving registers at bottom
		elif index == FP:
			value = 0
		elif index == SB:
			value = stackBase - (INT * 13)
		else:	
			value = 0

		setIntAt(positionToSaveAt, value)

# Turn on main thread
activeThreads[MAIN_THREAD] = True 
currentThread = MAIN_THREAD



while reg[PC] < MEM_INST: 
	# if the thread is turned off, ignore it. 
	if (currentThread >= MAX_THREADS): 
		currentThread = 0
	if activeThreads[currentThread] == False:
		currentThread += 1
		continue

	# Block main thread, if applicable
		

	# if currentThread is blocked
	if blockedThreads[currentThread] == True:
		if currentThread == MAIN_THREAD:
			# If main is blocked, but there are no other active threads, turn off the block
			blockedThreads[MAIN_THREAD] = False
			for threadId in range(MAIN_THREAD + 1, MAX_THREADS):
				if activeThreads[threadId] == True: 
					blockedThreads[MAIN_THREAD] = True
		
		currentThread += 1
		continue

	# Load currentThread's context **************************
	load_context() 

	# run one instruction
	opcode = getIntAt(reg[PC])
	incrementPC(INT)
	op1 = getIntAt(reg[PC])
	incrementPC(INT)
	op2 = getIntAt(reg[PC])
	incrementPC(INT)


	
	# print('Thread: ', currentThread, ' - PC: ', reg[PC] - 12, ' - ', opcode, op1, op2)
	# if opcode == 22: 
	# 	print(' ')

	# Figure out what instruction the opcode relates to and call the corresponding function
	for key, values in InstructionDic.items(): 
		if 'opcode' in values and values['opcode'] == opcode: 
			values['method'](op1, op2)

	# if we hit empty instruction space, we hit the end with no TRP function called.  
	if opcode == 0: 
		break

	# save currentThread's context **********************************
	save_context()


	# increment current thread
	currentThread += 1

# if the PC bleeds into the Heap, we hit the end with no TRP function called
kill('ERROR - No TRP 0 command at program end')
# ==================================================================================
