import sys
import re
import inspect
import os
import enum # for enumerations
from frozendict import frozendict # for an immutable dictionary 



# token Type enumerations
tokenType = {
	"NUMBER" : 0, 
	"MATHEMATICAL" : 1, 
	"BOOLEAN" : 2, 
	"ASSIGNMENT" : 3, 
	"PUNCTUATION" : 4, 
	"ARRAY_BEGIN" : 5, 
	"ARRAY_END" : 6, 
	"BLOCK_BEGIN" : 7, 
	"BLOCK_END" : 8, 
	"PARENTHESES_OPEN" : 9, 
	"PARENTHESES_CLOSE" : 10, 
	"INPUT" : 11, 
	"OUTPUT" : 12, 
	"CHARACTER" : 13, 
	"LOGIC" : 14, 
	"KEYWORD" : 15, 
	"IDENTIFIER" : 16, 
	"UNKNOWN" : 17,
	"EOF" : 18,
	"TEMP" : 19,
	"REFERENCE" : 20
}

keywords = [
	"atoi", "and", "bool", "block", "break", "case", "class", "char", 
	"cin", "cout", "default", "else", "false", "if", "int", "itoa", 
	"kxi2020", "lock", "main", "new", "null", "object", "or", "public", 
	"private", "protected", "return", "release", "string", "spawn", 
	"sym", "set", "switch", "this", "true", "thread", "unprotected", 
	"unlock", "void", "while", "wait"
]

kindAbv = {
	'class': 'C', 
	'ivar': 'V', 
	'method': 'M', 
	'param': 'P', 
	'lvar': 'L', 
	'constructor': 'X', 
	'nlit': 'N', 
	'hlit': 'H',
	'temp': 'T', 
	'reference' : 'R'
}

onStackOperatorPrecedence = {
	'(' : -1, 
	'[' : -1, 

	')' : 0, 
	']' : 0, 

	'*' : 13,
	'/' : 13,

	'+' : 11,
	'-' : 11,

	'<' : 9,
	'>' : 9,
	'<=' : 9,
	'>=' : 9,

	'==' : 7,
	'!=' : 7,

	'and' : 5,

	'or' : 3,

	'=' : 1, 
}

inputOperatorPrecedence = {
	'(' : 15, 
	'[' : 15, 

	')' : 0, 
	']' : 0, 

	'*' : 13,
	'/' : 13,

	'+' : 11,
	'-' : 11,

	'<' : 9,
	'>' : 9,
	'<=' : 9,
	'>=' : 9,

	'==' : 7,
	'!=' : 7,

	'and' : 5,

	'or' : 3,

	'=' : 1, 
}

elementSize = {
	'int' : 4, 
	'char' : 1,  
	'bool' : 4, 
	'pointer' : 4,
	'functionElement' : 4, 
}



""" closure: Symid Factory **********************************************************
*********************************************************************************"""
def symidFactory():
    count = 0
    def inner(x):
        nonlocal count
        count += 1
        return x + str(count)
    return inner
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^	


""" closure: Label Factory **********************************************************
*********************************************************************************"""
def labelFactory():
    count = 0
    def inner():
        nonlocal count
        count += 1
        return 'LABEL' + str(count)
    return inner
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^	




""" iCode Containers **********************************************************
*********************************************************************************"""
class QuadTable():
	def __init__(self):
		super().__init__()
		self.QT = []
		self.SQUAD = []

	# points returns which quad list we should be adding to
	def which(self):
		if len(ST.scope.split('.')) == 2 and ST.popScope(ST.scope, returnRemoved=True) != 'main':
			return self.SQUAD
		else: 
			return self.QT 


	def add(self, label='', operator='', operand_1='', operand_2='', operand_3='', comment=''):
		# if we put None as one of our parameters, change it to '' so we can print it later. 
		if not label: 
			label = ''
		if not operator:  
			operator = ''
		if not operand_1: 
			operand_1 = ''
		if not operand_2: 
			operand_2 = ''
		if not operand_3:
			operand_3 = ''
		if not comment: 
			comment = ''


		# Figure out which list to add to
		tablePointer = self.which()


		# if the previous line does not have an operator, fill in this line. 
		# backpatch labels if you need to.  
		if len(tablePointer) != 0 and not tablePointer[len(tablePointer) - 1]['operator']:

			# Backpatch, if there's already a label and we have a new label to insert
			oldLabel = tablePointer[len(tablePointer) - 1]['label']
			if oldLabel and label: 
				self.backPatch(oldLabel, label)

			# Decide which label to insert
			theLabel = ''
			if label: 
				theLabel = label 
			elif oldLabel:
				theLabel = oldLabel

			# Edit the last quad
			tablePointer[len(tablePointer) - 1] = {
				'label': theLabel, 
				'operator': operator, 
				'operand_1': operand_1, 
				'operand_2': operand_2, 
				'operand_3': operand_3, 
				'comment': comment
			}
		else:
			# Insert new quad
			tablePointer.append({
					'label': label, 
					'operator': operator, 
					'operand_1': operand_1, 
					'operand_2': operand_2, 
					'operand_3': operand_3, 
					'comment': comment
				})

	def backPatch(self, labelToReplace, newLabel):
		# Figure out which list to add to
		tablePointer = self.which()

		# loop through self backwards. 
		for i in range(len(tablePointer) - 1, -1, -1):
			# label
			if tablePointer[i]['label'] == labelToReplace:
				tablePointer[i]['label'] = newLabel

			# op1
			if tablePointer[i]['operand_1'] == labelToReplace:
				tablePointer[i]['operand_1'] = newLabel

			# op2
			if tablePointer[i]['operand_2'] == labelToReplace:
				tablePointer[i]['operand_2'] = newLabel

			# op3
			if tablePointer[i]['operand_3'] == labelToReplace:
				tablePointer[i]['operand_3'] = newLabel

	def print(self):
		for item in self.QT: 
			print(item['label'].ljust(20) + item['operator'].ljust(10) + item['operand_1'].ljust(20) + item['operand_2'].ljust(10) + item['operand_3'].ljust(10) + item['comment'].strip().ljust(30))

	def printSquad(self):
		for item in self.SQUAD: 
			print(item['label'].ljust(20) + item['operator'].ljust(10) + item['operand_1'].ljust(20) + item['operand_2'].ljust(10) + item['operand_3'].ljust(10) + item['comment'].strip().ljust(30))		

	def toFile(self):
		icode_file = open('icode.txt', 'w')
		for item in self.QT:
			icode_file.write(item['label'].ljust(20) + item['operator'].ljust(10) + item['operand_1'].ljust(20) + item['operand_2'].ljust(10) + item['operand_3'].ljust(10) + item['comment'].strip().ljust(30) + '\n') 

class CommentMap(dict):
	def __init__(self):
		super().__init__()

	def print(self):
		for lineNumber in self: 
			print(str(lineNumber) + ': ' + self[lineNumber])

	# This returns the comment at lex's currentLineNumber and erases said line from our map. 
	def get(self, lineNumber=None):
		if not lineNumber:
			lineNumber = lex.currentLineNumber - 1
		line = self[lineNumber]
		self[lineNumber] = ''
		return line
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^	





""" class: Symbol Table ************************************************************
********************************************************************************"""
class SymbolTable(dict): 
	def __init__(self):
		self.globalOffsetTracker = 0

		self.scope = 'g'
		self.add(scope='g', symid='true', lexeme='true', kind='true', theType='bool', accessMod='public')
		self.add(scope='g', symid='false', lexeme='false', kind='false', theType='bool', accessMod='public')
		self.add(scope='g', symid='null', lexeme='null', kind='null', theType='null', accessMod='public')

		self.add(scope='g', symid='sizeOfPointer', lexeme='sizeOfPointer', kind='sizeOfPointer', theType='int', accessMod='public')
		self.add(scope='g', symid='sizeOfChar', lexeme='sizeOfChar', kind='sizeOfChar', theType='int', accessMod='public')
		self.add(scope='g', symid='sizeOfBool', lexeme='sizeOfBool', kind='sizeOfBool', theType='int', accessMod='public')
		self.add(scope='g', symid='sizeOfInt', lexeme='sizeOfInt', kind='sizeOfInt', theType='int', accessMod='public')

	# counts the size of the the locals and temps that are found in the given scope.  only used for function scopes.  
	def localTempSize(self, scopeToSearch):
		localTempList = ST.findAllInScope(scope=scopeToSearch, kindList=['lvar', 'temp'])
		return len(localTempList) * 4

	def appendScope(self, newScope):
		self.scope += '.' + newScope

		if TRACK_SCOPE:
			print('appendScope: ' + self.scope)

	def popScope(self, scope=None, returnRemoved=False):
		if scope == None: 
			scopeList = self.scope.split('.')
			if len(scopeList) - 1 > 0:
				scopeList.pop()
				self.scope = '.'.join(scopeList)
			else:
				print('error in popScope - the current scope was popped into nothingness')

			if TRACK_SCOPE:
				print('popScope: ' + self.scope)
		elif scope != None and not returnRemoved: 
			scopeList = scope.split('.')
			if len(scopeList) - 1 > 0:
				scopeList.pop()
				return '.'.join(scopeList)
			else: 
				return ''
		elif scope != None and returnRemoved:
			scopeList = scope.split('.')
			if len(scopeList) - 1 > 0:
				return scopeList.pop()
			else: 
				return ''


		
	''' 
	returns the symid of the first symbol that matches the given criteria
	searches in current scope first, an pops scope until it reaches empty scope OR finds a match 
	'''
	def findFirst(self, scope=None, symid=None, lexeme=None, kindList=None, theType=None, returnType=None, accessMod=None, params=None):
		if scope == None: 
			scope = self.scope[:]

		scopeToSearch = scope[:]

		while scopeToSearch != '': 

			result = self.findFirstInScope(scope=scopeToSearch, symid=symid, lexeme=lexeme, kindList=kindList, theType=theType, returnType=returnType, accessMod=accessMod, params=params)
			if result != None: 
				return result

			# Break the loop if the next scope to search is empty
			scopeToSearch = self.popScope(scopeToSearch)

	'''
	returns symid of the first symbol that matches the given criteria
	searches only the current scope

	default scope to current scope
	'''
	def findFirstInScope(self, scope=None, symid=None, lexeme=None, kindList=None, theType=None, returnType=None, accessMod=None, params=None):
		if scope == None: 
			scope = self.scope[:]

		for possibleMatch in self:
			if not self.isMatch(key=possibleMatch, scope=scope, symid=symid, lexeme=lexeme, kindList=kindList, theType=theType, returnType=returnType, accessMod=accessMod, params=params):
				continue
			return possibleMatch 
		return None

	def findAllInScope(self, scope=None, symid=None, lexeme=None, kindList=None, theType=None, returnType=None, accessMod=None, params=None):
		if scope == None: 
			scope = self.scope[:]

		items = []
		for possibleMatch in self:

			if not self.isMatch(key=possibleMatch, scope=scope, symid=symid, lexeme=lexeme, kindList=kindList, theType=theType, returnType=returnType, accessMod=accessMod, params=params):
				continue
			items.append(possibleMatch) 
		return items

	def isMatch(self, key, scope=None, symid=None, lexeme=None, kindList=None, theType=None, returnType=None, accessMod=None, params=None):
		if scope != None and scope != self[key]['scope']: 
			return False

		if symid != None and key != 'this' and symid != self[key]['symid']: 
			return False

		if lexeme != None and lexeme != self[key]['lexeme']:
			return False

		if kindList != None and self[key]['kind'] not in kindList:
			return False


		# handle searching for a nonArray and array type. 
		currentSymbolType = self[key]['data']['theType']

		if theType != None and ( \
			(currentSymbolType == None) or \
			(theType not in ['@', ''] and theType != currentSymbolType) or \
			(theType == '' and currentSymbolType[0] == '@') or \
			(theType == '@' and currentSymbolType[0] != '@') \
		):
			return False

		if returnType != None and returnType != self[key]['data']['returnType']:
			return False

		if accessMod != None and accessMod != self[key]['data']['accessMod']:
			return False

		# Check order, arity, and type of the given param list
		if params != None:
			# Check Arity 
			currentSymbolParams = self[key]['data']['params']
			if len(params) != len(currentSymbolParams):
				return False 

			# Check order and type
			for index in range(len(currentSymbolParams)):
				# if we cant find a symbol to go with the current symid from the passed in params OR the current symbol's params, no match
				if params[index] not in ST or currentSymbolParams[index] not in ST:
					return False

				# pull the symbols out of the symbol table
				passedInSymbol = ST[params[index]]
				currentSymbol = ST[currentSymbolParams[index]]

				# pull theType out of the symbols
				passedInType = passedInSymbol['data']['theType']
				currentSymbolType = currentSymbol['data']['theType']

				# Make sure the types exist in the symbols and that the types of the current params match
				if passedInType != currentSymbolType: 
					return False 

		return True

	def matchingType(self, symid, theType):

		# if the key is a 'this', get the type of what 'this' points to
		if symid == 'this':
			# get this's type
			typeToMatch = ST.popScope(ST.popScope(scope=ST.scope), returnRemoved=True)
		else:
			typeToMatch = ST[symid]['data']['theType']
			
		if theType != typeToMatch:
			return False
		
		return True


	# adds new symbol to symbol table
	def add(self, scope=None, symid=None, lexeme=None, kind=None, theType=None, returnType=None, accessMod=None, params=None):
		# do not allow for multiple hlit and nlit 's of the same lexeme to be created.  e.g. two symbols representing 7 is not allowed
		if kind in ['hlit', 'nlit'] and self.findFirst(scope='g', lexeme=lexeme, kindList=[kind]):
			return

		# populate scope with SymbolTable's current scope if not given
		if scope == None:
			scope = self.scope[:]

		# generate symid based off of kind if not given
		if symid == None: 
			if kind == None: 
				print('ERROR in SymbolTable.add - need a kind to generate symid inside this method')
				sys.exit(1)
			symid = generateSymid(kindAbv[kind])


		# create entry in symbol table with given information
		self[symid] = {
			'scope': scope, 
			'symid': symid, 
			'lexeme': lexeme, 
			'kind': kind, 
			'data': {
				'theType': theType, 
				'returnType': returnType, 
				'accessMod': accessMod, 
				'params': params 
			}
		}

		# inintialize the size variable in classes and functions
		if kind == 'class':
			self[symid]['size'] = 0
		elif kind in ['method', 'main', 'constructor']:
			# every method has a return address, this pointer, and a PFP. 
			self[symid]['size'] = elementSize['functionElement'] * 3 * -1

		# calculate offsets
		# global variable
		elif scope == 'g' and kind not in ['class', 'main']:

			# global variable

			# save global offset
			self[symid]['offset'] = self.globalOffsetTracker

			# add to globalOffsetTracker
			if lexeme[0] == '@' or not isBuiltInType(Token(lexeme=theType, lineNumber=1, tokenType='')):  
				self.globalOffsetTracker += elementSize['pointer']
			else: 
				self.globalOffsetTracker += elementSize[theType]
		
		# heap variable
		elif len(scope.split('.')) == 2 and ST.popScope(scope, returnRemoved=True) != 'main' and kind == 'ivar':

			# get the symid of the ST class this ivar belongs to
			class_name = ST.popScope(scope, returnRemoved=True)
			class_symid = ST.findFirst(lexeme=class_name, kindList=['class'])

			# save the class offset
			self[symid]['offset'] = self[class_symid]['size']

			# update the size of the class
			if lexeme[0] == '@' or not isBuiltInType(Token(lexeme=theType, lineNumber=1, tokenType='')): 
				self[class_symid]['size'] += elementSize['pointer']
			else: 
				self[class_symid]['size'] += elementSize[theType]	

		# stack variable inside main function
		elif len(scope.split('.')) == 2 and ST.popScope(scope, returnRemoved=True) == 'main' and kind in ['lvar', 'param', 'temp']:

			# get the symid of the ST function this variable belongs to
			func_symid = 'main'

			# increment funcOffsetTracker
			self[func_symid]['size'] -= elementSize['functionElement']

			# save this offset into the tracker. 
			self[symid]['offset'] = self[func_symid]['size']


		# stack variable inside a method
		elif len(scope.split('.')) == 3 and kind in ['lvar', 'param', 'temp']:

			# ST.print()

			# get the symid of the ST function this variable belongs to
			func_name = ST.popScope(scope, returnRemoved=True)
			func_scope = ST.popScope(scope)
			func_symid = ST.findFirst(scope=func_scope, lexeme=func_name, kindList=['method', 'constructor'])			

			# increment funcOffsetTracker
			self[func_symid]['size'] -= elementSize['functionElement']

			# save this offset into the tracker. 
			self[symid]['offset'] = self[func_symid]['size']
		
		# stack variable inside a staticInit method
		elif len(scope.split('.')) == 2 and ST.popScope(scope, returnRemoved=True) != 'main' and kind in ['lvar', 'param', 'temp']:

			# get the symid of the staticInitFunction 
			className = ST.popScope(scope, returnRemoved=True)
			func_symid = className + 'StaticInit'

			# add to funcOffsetTracker
			self[func_symid]['size'] -= elementSize['functionElement']

			# save function offset
			self[symid]['offset'] = self[func_symid]['size']

			# update the scope
			self[symid]['scope'] = self[symid]['scope'] + '.' + func_symid


		# unmatched
		else: 
			print('!!: ' + symid)




	def print(self):
		for i in self:
			print(i + ' ==> ')
			for k in self[i]:
				if k == 'data':
					print('    data:')
					for o in self[i][k]:	
						print('         ' + o + ': ', end='')
						if self[i][k][o] or (o == 'params' and self[i][k][o] and len(self[i][k][o]) == 0): 
							print(self[i][k][o], end='')
						print(' ')
				else:
					print('    ' + k + ': ' + str(self[i][k]))
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

 


""" class: Token ************************************************************
**************************************************************************"""
class Token: 
	# Constructor
	def __init__(self, lexeme, tokenType, lineNumber):
		self.lexeme = lexeme
		self.tokenType = tokenType
		self.lineNumber = lineNumber

	def toString(self):
		l = ('LEXEME: ' + self.lexeme).ljust(21)
		t = ('TOKENTYPE: ' + {value:key for key, value in tokenType.items()}[self.tokenType]).ljust(30)
		n = ('LINE: ' + str(self.lineNumber)).ljust(10)
		return  l + '  ' + t + '  ' + n   
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


""" class lexer *************************************************************
************************************************************************** """
'''
Make sure that as we make tokens available in the token buffer so our peek functions
do not break, make sure the tokens are being put in the right lines.  
'''
class Lexer:
	# Constructor
	def __init__(self, filename):
		self.tokenBuffer = []
		self.f = open(filename)
		self.currentLineNumber = 0
		self.nextToken()


	# member functions
	def printTokenBuf(self):
		for token in self.tokenBuffer:
			token.print()

	def getToken(self):
		if len(self.tokenBuffer) >= 1:
			return self.tokenBuffer[0]

	def peekToken(self): 
		if len(self.tokenBuffer) >= 2:
			return self.tokenBuffer[1]

	def peek2Token(self):
		if len(self.tokenBuffer) >= 3:
			return self.tokenBuffer[2]

	def nextToken(self):

		msg = 'nextToken: '
		if self.getToken() != None: 
			msg += self.getToken().lexeme + ' => '
		else:
			msg += 'None => '


		if len(self.tokenBuffer) > 0 and self.tokenBuffer[0].lexeme != 'EOF':				# make sure we wont get an error when we pop
			self.tokenBuffer.pop(0)					# pop 1st element off tokenBuffer			
		self.nextTokenHelper() 

		if TRACKER_ON and PASS_NUMBER == 2:
			print(msg + self.getToken().lexeme)


	def nextTokenHelper(self):
		if len(self.tokenBuffer) < 3: 
			# get new line from file 
			line = self.f.readline()

			# save the line into the comment map
			CM[self.currentLineNumber + 1] = line[:]

			if line != '':
				self.currentLineNumber += 1
				self.tokenize(line)
				# make sure we have three tokens in tokenBuffer so peeks won't break
				self.nextTokenHelper()
			else:
				for i in range(3):
					self.tokenBuffer.append(Token("EOF", tokenType["EOF"], self.currentLineNumber))

	def tokenize(self, line):
		while (len(line) > 0) :

			# ignore whitespace.  If we get an empty string after, line is done. 
			line = line.lstrip()
			if len(line) == 0:		
				break; 
			
			# ignore single line comments
			match = re.search("^\/\/.*", line)
			if match is not None:
				line = ''
				continue

			# match NUMBER
			match = re.search("^[0-9]+", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["NUMBER"], self.currentLineNumber))
				line = re.sub("^[0-9]+", '', line)
				continue

			# match MATH
			match = re.search("^[+\-*/]", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["MATHEMATICAL"], self.currentLineNumber))
				line = re.sub("^[+\-*/]", '', line)
				continue

			# match OUTPUT
			match = re.search("^<<", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["OUTPUT"], self.currentLineNumber))
				line = re.sub("^<<", '', line)
				continue

			# match INPUT
			match = re.search("^>>", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["INPUT"], self.currentLineNumber))
				line = re.sub("^>>", '', line)
				continue

			# match BOOLEAN
			match = re.search("^==|^!=|^<=|^>=|^[<>]", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["BOOLEAN"], self.currentLineNumber))
				line = re.sub("^==|^!=|^<=|^>=|^[<>]", '', line)
				continue

			# match ASSIGNMENT
			match = re.search("^=", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["ASSIGNMENT"], self.currentLineNumber))
				line = re.sub("^=", '', line)
				continue

			# match PUNCTUATION
			match = re.search("^[.,;:]", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["PUNCTUATION"], self.currentLineNumber))
				line = re.sub("^[.,;:]", '', line)
				continue

			# match ARRAY BEGIN
			match = re.search("^\[", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["ARRAY_BEGIN"], self.currentLineNumber))
				line = re.sub("^\[", '', line)
				continue

			# match ARRAY END
			match = re.search("^\]", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["ARRAY_END"], self.currentLineNumber))
				line = re.sub("^\]", '', line)
				continue

			# match PARENTHESIS BEGIN
			match = re.search("^\(", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["PARENTHESES_OPEN"], self.currentLineNumber))
				line = re.sub("^\(", '', line)
				continue

			# match PARENTHESIS END
			match = re.search("^\)", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["PARENTHESES_CLOSE"], self.currentLineNumber))
				line = re.sub("^\)", '', line)
				continue

			# match BLOCK BEGIN
			match = re.search("^\{", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["BLOCK_BEGIN"], self.currentLineNumber))
				line = re.sub("^\{", '', line)
				continue

			# match BLOCK END
			match = re.search("^\}", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["BLOCK_END"], self.currentLineNumber))
				line = re.sub("^\}", '', line)
				continue

			# match CHARACTER
			match = re.search("^'[ -~]'|^'\\\\[0abefnrtv]'", line)
			if match is not None:
				self.tokenBuffer.append(Token(match.group(), tokenType["CHARACTER"], self.currentLineNumber))
				line = re.sub("^'[ -~]'|^'\\\\[0abefnrtv]'", '', line)
				continue

			# match LOGIC, KEYWORD, and IDENTIFIER
			match = re.search("^[a-zA-Z][a-zA-Z0-9_]*", line)
			if match is not None:
				token = match.group()

				if token == 'and' or token == 'or':
					self.tokenBuffer.append(Token(match.group(), tokenType["LOGIC"], self.currentLineNumber))
					line = re.sub("^[a-zA-Z][a-zA-Z0-9_]*", '', line)
					continue

				if token in keywords:
					self.tokenBuffer.append(Token(match.group(), tokenType["KEYWORD"], self.currentLineNumber))
					line = re.sub("^[a-zA-Z][a-zA-Z0-9_]*", '', line)
					continue

				# if we get here, we know it's an identifier :D
				self.tokenBuffer.append(Token(match.group(), tokenType["IDENTIFIER"], self.currentLineNumber))
				line = re.sub("^[a-zA-Z][a-zA-Z0-9_]*", '', line)
				continue

			# if we get here, we don't know what this token is! 
			self.tokenBuffer.append(Token(line[0], tokenType["UNKNOWN"], self.currentLineNumber))
			line = line[1:]
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



# -------------------------------------------------------------------------------------------------
# *** SYNTAX HELPERS ******************************************************************************
def kill(token, expectation):
	PASS_SUCCESS = False
	print(str(token.lineNumber) + ': Found ' + token.lexeme + ' expecting ' + str(expectation))

	if TRACKER_ON:
		print(inspect.stack()[1][3] + ' - token: ' + lex.getToken().lexeme)

	sys.exit(1)

def tracker():
	if TRACKER_ON and PASS_NUMBER == 2: 
		print('  ** ' + inspect.stack()[1][3])

def isStatementStart(token):
	return token.lexeme in ['{', 'if', 'while', 'return', 'cout', 'cin', 'switch', 'break'] or isExpressionStart(token)

def isExpressionStart(token):
	return token.lexeme in ['(', 'true', 'false', 'null', 'this'] or token.tokenType in [tokenType['IDENTIFIER'], tokenType['CHARACTER']] or (token.tokenType == tokenType['NUMBER'] or token.lexeme == '+' or token.lexeme == '-')

def isBuiltInType(token):
	return token.lexeme in ['int', 'char', 'bool', 'void', 'sym']

def isExpressionzStart(token):
	return token.lexeme in ['=', 'and', 'or', '==', '!=', '<=', '>=', '<', '>', '+', '-', '*', '/']
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



# -----------------------------------------------------------------------------------------------------
# *** SYNTAX GRAMMAR RULES ****************************************************************************
def modifier():
	tracker()

	if lex.getToken().lexeme not in ['public', 'private']:
		kill(lex.getToken(), 'modifier')
	lex.nextToken()

def class_name():
	tracker()

	if lex.getToken().tokenType != tokenType['IDENTIFIER']:
		kill(lex.getToken(), 'identifier')
	lex.nextToken()

def type():
	tracker()

	typeToken = lex.getToken()
	if lex.getToken().lexeme == 'int': 
		lex.nextToken()

	elif lex.getToken().lexeme == 'char':
		lex.nextToken()

	elif lex.getToken().lexeme == 'bool':
		lex.nextToken()

	elif lex.getToken().lexeme == 'void':
		lex.nextToken()

	elif lex.getToken().lexeme == 'sym':
		lex.nextToken()

	elif lex.getToken().tokenType == tokenType['IDENTIFIER']:
		lex.nextToken()

	else: 
		kill(lex.getToken(), 'type')

	# SEMANTICS
	if PASS_NUMBER == 2:
		_tPush(typeToken)


def character_literal():
	tracker()

	literalToken = lex.getToken()
	if lex.getToken().tokenType != tokenType['CHARACTER']:
		kill(lex.getToken(), 'Character Literal')
	lex.nextToken()

	if PASS_NUMBER == 1:
		ST.add(scope='g', symid=None, lexeme=literalToken.lexeme, kind='hlit', theType='char', accessMod='public')

	# SEMANTICS
	if PASS_NUMBER == 2:
		_lPush(literalToken)


def numeric_literal():
	tracker()

	number = ''

	# Design Choice: we want positive numbers to not have a sign, 
	# 				 negative numbers will keep the negative sign. 
	if lex.getToken().lexeme == '+':
		lex.nextToken()

	elif lex.getToken().lexeme == '-':
		number += lex.getToken().lexeme
		lex.nextToken()

	numberToken = lex.getToken()
	number += lex.getToken().lexeme
	if lex.getToken().tokenType != tokenType['NUMBER']:
		kill(lex.getToken(), 'Numeric Literal')
	lex.nextToken()

	if PASS_NUMBER == 1:
		ST.add(scope='g', symid=None, lexeme=number, kind='nlit', theType='int', accessMod='public')

	# SEMANTICS
	if PASS_NUMBER == 2: 
		# create a custom token that has the number with the correct sign prepended onto it (if needed).  
		_lPush(Token(lineNumber=numberToken.lineNumber, lexeme=number, tokenType=tokenType['NUMBER']))
	


def case_block():
	tracker()

	if lex.getToken().tokenType != tokenType['BLOCK_BEGIN']:
		kill(lex.getToken(), '{')
	lex.nextToken()

	while lex.getToken().lexeme == 'case':
		case_label()

	if lex.getToken().lexeme != 'default':
		kill(lex.getToken(), 'default')
	lex.nextToken()

	if lex.getToken().lexeme != ':': 
		kill(lex.getToken(), ':')
	lex.nextToken()

	statement()

	if lex.getToken().tokenType != tokenType['BLOCK_END']:
		kill(lex.getToken(), '}')
	lex.nextToken()


def case_label():
	tracker()

	if lex.getToken().lexeme != 'case':
		kill(lex.getToken(), 'case') 
	lex.nextToken()

	literal()

	if lex.getToken().lexeme != ':': 
		kill(lex.getToken(), ':')
	lex.nextToken()

	statement()


def literal():
	tracker()

	if lex.getToken().lexeme in ['+','-'] or lex.getToken().tokenType == tokenType['NUMBER']:
		numeric_literal()
	elif lex.getToken().tokenType == tokenType['CHARACTER']:
		character_literal()
	else:
		kill(lex.getToken(), 'Literal')


def compilation_unit():
	tracker()

	# Add quads 
	if PASS_NUMBER == 2:
		# First three lines of ICode
		QT.add(label='', operator='FRAME', operand_1='main', operand_2='null', operand_3='', comment='')
		QT.add(label='', operator='CALL', operand_1='main', operand_2='', operand_3='', comment='')
		QT.add(label='', operator='STOP', operand_1='', operand_2='', operand_3='', comment='')
		

	while lex.getToken().lexeme == 'class':
		class_declaration()

	token = lex.getToken()
	if lex.getToken().lexeme != 'void': 
		kill(lex.getToken(), 'void')
	lex.nextToken()

	if lex.getToken().lexeme != 'kxi2020': 
		kill(lex.getToken(), 'kxi2020')
	lex.nextToken()

	if lex.getToken().lexeme != 'main': 
		kill(lex.getToken(), 'main')
	lex.nextToken()

	if lex.getToken().tokenType != tokenType['PARENTHESES_OPEN']: 
		kill(lex.getToken(), '(')
	lex.nextToken()

	if lex.getToken().tokenType != tokenType['PARENTHESES_CLOSE']: 
		kill(lex.getToken(), ')')
	lex.nextToken()


	if PASS_NUMBER == 1:
		ST.add(scope=None, symid='main', lexeme='main', kind='main', returnType='void', params=[], accessMod='public')

	if PASS_NUMBER == 2: 
		# Icode main function
		i_func('main')

	ST.appendScope('main') # SCOPE CHANGE

	method_body()

	ST.popScope() # SCOPE CHANGE

	# make sure there is nothing left in the file 
	if lex.getToken().lexeme != 'EOF':
		kill(lex.getToken(), 'EOF')


def class_declaration():
	tracker()

	if lex.getToken().lexeme != 'class': 
		kill(lex.getToken(), 'class')
	lex.nextToken()

	token = lex.getToken()
	class_name()

	if PASS_NUMBER == 1:
		ST.add(scope=None, symid=None, lexeme=token.lexeme, kind='class') 

	# SEMANTICS and ICODE
	if PASS_NUMBER == 2: 
		_dup(token)

	ST.appendScope(token.lexeme) # SCOPE CHANGE


	if PASS_NUMBER == 2:
		# Add symbol for the static init function
		staticInitFunc_symid = token.lexeme + 'StaticInit'
		ST.add(scope=None, symid=staticInitFunc_symid, lexeme=staticInitFunc_symid, kind='method', returnType='void', params=[])

		# add quad for the static init function
		i_squadfunc(staticInitFunc_symid)


	if lex.getToken().tokenType != tokenType['BLOCK_BEGIN']:
		kill(lex.getToken(), '{')
	lex.nextToken()

	while lex.getToken().lexeme in ['public', 'private'] or lex.getToken().tokenType == tokenType['IDENTIFIER']:
		class_member_declaration()


	if PASS_NUMBER == 2: 
	 	# Add RTN quad to SQUAD
	 	i_squadRTN(lex.getToken())

	 	# copy everything in squad over to QT
	 	i_movSQUAD()


	ST.popScope() # SCOPE CHANGE

	if lex.getToken().tokenType != tokenType['BLOCK_END']:
		kill(lex.getToken(), '}')
	lex.nextToken()


def class_member_declaration():
	tracker()

	if lex.getToken().lexeme in ['public', 'private']:
		memberModifier = lex.getToken().lexeme
		modifier()

		memberType = lex.getToken()
		type()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_tExist()

		if lex.getToken().tokenType == tokenType['ARRAY_BEGIN']:
			lex.nextToken()

			if lex.getToken().tokenType != tokenType['ARRAY_END']:
				kill(lex.getToken(), ']')
			lex.nextToken()

			memberType.lexeme = '@' + memberType.lexeme

		memberIdentifier = lex.getToken()
		if lex.getToken().tokenType != tokenType['IDENTIFIER']:
			kill(lex.getToken(), 'identifier')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2:
			_dup(memberIdentifier)
			_vPush()
	

		# field_declaration -------------------------------------
		operatorToken = lex.getToken()

		if lex.getToken().lexeme == '=':
			lex.nextToken()

			if PASS_NUMBER == 1:
				ST.add(scope=None, symid=None, lexeme=memberIdentifier.lexeme, kind='ivar', theType=memberType.lexeme, accessMod=memberModifier)

			# SEMANTICS
			if PASS_NUMBER == 2: 
				_oPush(operatorToken)

			assignment_expression()

			if lex.getToken().lexeme != ';': 
				kill(lex.getToken(), ';')
			lex.nextToken()

			# SEMANTICS
			if PASS_NUMBER == 2: 
				_EOE()



		elif lex.getToken().lexeme == ';':
			lex.nextToken()

			if PASS_NUMBER == 1:
				ST.add(scope=None, symid=None, lexeme=memberIdentifier.lexeme, kind='ivar', theType=memberType.lexeme, accessMod=memberModifier)

			# SEMANTICS
			if PASS_NUMBER == 2: 
				_EOE()


		
		elif lex.getToken().tokenType == tokenType['PARENTHESES_OPEN']:
			lex.nextToken()

			# Update the scope so the parameters will be in the correct scope. 
			# save this scope though because this is the scope the method belongs to
			scopeMethodBelongsTo = ST.scope
			ST.appendScope(memberIdentifier.lexeme) # SCOPE CHANGE


			# add the method's symobl into the symbol table wihtout the params.  We'll add those after we parse them. 
			if PASS_NUMBER == 1:
				ST.add(scope=scopeMethodBelongsTo, symid=None, lexeme=memberIdentifier.lexeme, kind='method', returnType=memberType.lexeme, params=[], accessMod=memberModifier)


			paramList = []
			if isBuiltInType(lex.getToken()) or lex.getToken().tokenType == tokenType['IDENTIFIER']:
				paramList = parameter_list()

			if lex.getToken().tokenType != tokenType['PARENTHESES_CLOSE']:
				kill(lex.getToken(), ')')
			lex.nextToken()


			# Add the params to the function's symbol here
			if PASS_NUMBER == 1:
				func_symid = ST.findFirst(scope=scopeMethodBelongsTo, lexeme=memberIdentifier.lexeme, kindList=['method'])
				ST[func_symid]['data']['params'] = paramList


			if PASS_NUMBER == 2:
				# find the symid of the funciton (there will be one because there is no function overloading in kxi)
				func_symid = ST.findFirst(scope=scopeMethodBelongsTo, lexeme=memberIdentifier.lexeme, kindList=['method'])
				# Make the quad
				i_func(func_symid)

			method_body()

			ST.popScope() # SCOPE CHANGE

		else:
			kill(lex.getToken(), ['=',';','IDENTIFIER'])
		# end field_declaration ---------------------------------


	elif lex.getToken().tokenType == tokenType['IDENTIFIER']:
		constructor_declaration()
	else:
		kill(lex.getToken(), ['public', 'private', 'IDENTIFIER'])

	
def constructor_declaration():
	tracker()

	xtorIdentifier = lex.getToken()
	class_name()

	# SEMANTICS
	if PASS_NUMBER == 2: 
		_dup(xtorIdentifier)
		_CD(xtorIdentifier)

	xtorScope = ST.scope

	ST.appendScope(xtorIdentifier.lexeme) # SCOPE CHANGE

	if lex.getToken().tokenType != tokenType['PARENTHESES_OPEN']: 
		kill(lex.getToken(), '(')
	lex.nextToken()


	if PASS_NUMBER == 1: 
		# add constructor into the symbol table (leave params empty - we'll fill those in later)
		ST.add(scope=xtorScope, symid=None, lexeme=xtorIdentifier.lexeme, kind='constructor', returnType=xtorIdentifier.lexeme, params=[], accessMod='public')


	paramList = []
	if lex.getToken().lexeme in ['int', 'char', 'bool', 'void', 'sym'] or lex.getToken().tokenType == tokenType['IDENTIFIER']:
		paramList = parameter_list()

	if lex.getToken().tokenType != tokenType['PARENTHESES_CLOSE']: 
		kill(lex.getToken(), ')')
	lex.nextToken()

	if PASS_NUMBER == 1: 
		# fill in the constructor's param list here
		constructor_symid = ST.findFirst(lexeme=xtorIdentifier.lexeme, kindList=['constructor'])
		ST[constructor_symid]['data']['params'] = paramList

	if PASS_NUMBER == 2: 
		# get the symid of the constructor (only one constructor per class, so it's an easy search)
		constructor_symid = ST.findFirst(lexeme=xtorIdentifier.lexeme, kindList=['constructor'])

		# generate the func quad
		i_func(constructor_symid)

		# call the class' staticInit function
		staticInitFunc_symid = ST.findFirst(lexeme=xtorIdentifier.lexeme + 'StaticInit', kindList=['method'])
		i_frame(A_symid='this', B_symid=staticInitFunc_symid, token=xtorIdentifier)

	method_body()

	ST.popScope() # SCOPE CHANGE



def method_body():
	tracker()

	if lex.getToken().tokenType != tokenType['BLOCK_BEGIN']:
		kill(lex.getToken(), '{')
	lex.nextToken()

	# if current token is IDENTIFIER, you will have to peek at least ONCE  
	# If peek token is ARRAY_BEGIN, you will have to peek a second time
	# If peek token is ARRAY_CLOSE, call variable_declaration 
	# If peek token is ExpressionStart, call statement
	while isBuiltInType(lex.getToken()) or (lex.getToken().tokenType == tokenType['IDENTIFIER'] and lex.peekToken().tokenType == tokenType['IDENTIFIER']) or (lex.getToken().tokenType == tokenType['IDENTIFIER'] and lex.peekToken().tokenType == tokenType['ARRAY_BEGIN'] and lex.peek2Token().tokenType == tokenType['ARRAY_END']):
		variable_declaration()

	#while (isStatementStart(lex.getToken()) and lex.getToken().tokenType != tokenType['IDENTIFIER']) or (lex.getToken().tokenType == tokenType['IDENTIFIER'] and (lex.peekToken().lexeme in ['(','.'] or isExpressionzStart(lex.peekToken()))) or (lex.getToken().tokenType == tokenType['IDENTIFIER'] and lex.peekToken().tokenType == tokenType['ARRAY_BEGIN'] and isExpressionStart(lex.peek2Token())) or (lex.getToken().tokenType == tokenType['IDENTIFIER'] and lex.peekToken().lexeme == ';'):
	while True:
		if lex.getToken().lexeme == '}':
			break
		statement()

	blockEnd_token = lex.getToken()
	if lex.getToken().tokenType != tokenType['BLOCK_END']:
		kill(lex.getToken(), '}')
	lex.nextToken()

	if PASS_NUMBER == 2:
		functionName = ST.popScope(ST.scope, returnRemoved=True)
		className = ST.popScope(ST.popScope(ST.scope), returnRemoved=True)
		if functionName == className:
			i_return('this')

		i_rtn(blockEnd_token)


def variable_declaration():
	tracker()

	varType = lex.getToken().lexeme
	type()

	# SEMANTICS
	if PASS_NUMBER == 2:
		_tExist()

	if lex.getToken().tokenType == tokenType['ARRAY_BEGIN']:
		lex.nextToken()

		if lex.getToken().tokenType != tokenType['ARRAY_END']:
			kill(lex.getToken(), ']')
		lex.nextToken()

		varType = '@' + varType

	varIdentifier = lex.getToken()
	if lex.getToken().tokenType != tokenType['IDENTIFIER']:
		kill(lex.getToken(), 'identifier')
	lex.nextToken()

	if PASS_NUMBER == 1: 
		ST.add(scope=None, symid=None, lexeme=varIdentifier.lexeme, kind='lvar', theType=varType, accessMod='private')

	# SEMANTICS
	if PASS_NUMBER == 2: 
		_dup(varIdentifier)
		_vPush()

	operatorToken = lex.getToken()
	if lex.getToken().tokenType == tokenType['ASSIGNMENT']:
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		assignment_expression()

	if lex.getToken().lexeme != ';':
		kill(lex.getToken(), ';')
	lex.nextToken()

	# SEMANTICS
	if PASS_NUMBER == 2: 
		_EOE()


def parameter_list():
	tracker()

	params = []

	paramSymid = parameter()
	params.append(paramSymid)

	while lex.getToken().lexeme == ',':
		lex.nextToken()
		paramSymid = parameter()
		params.append(paramSymid)

	return params


def parameter():
	tracker()

	paramType = lex.getToken().lexeme
	type()

	# SEMANTICS
	if PASS_NUMBER == 2:
		_tExist()

	if lex.getToken().tokenType == tokenType['ARRAY_BEGIN']:
		lex.nextToken()

		if lex.getToken().tokenType != tokenType['ARRAY_END']:
			kill(lex.getToken(), ']')
		lex.nextToken()

		paramType = '@' + paramType

	paramIdentifier = lex.getToken()
	if lex.getToken().tokenType != tokenType['IDENTIFIER']:
		kill(lex.getToken(), 'identifier')
	lex.nextToken()

	if PASS_NUMBER == 1:
		paramSymid = generateSymid('P')
		ST.add(scope=None, symid=paramSymid, lexeme=paramIdentifier.lexeme, kind='param', theType=paramType, accessMod='private')
		return paramSymid

	# SEMANTICS
	if PASS_NUMBER == 2: 
		_dup(paramIdentifier)
		return ST.findFirst(lexeme=paramIdentifier.lexeme, kindList=['param'], theType=paramType, accessMod='private')


def statement():
	tracker()

	if lex.getToken().tokenType == tokenType['BLOCK_BEGIN']: 
		lex.nextToken()

		while isStatementStart(lex.getToken()):
			statement()

		if lex.getToken().tokenType != tokenType['BLOCK_END']:
			kill(lex.getToken(), '}')
		lex.nextToken()

	elif isExpressionStart(lex.getToken()):
		expression()

		if lex.getToken().lexeme != ';':
			kill(lex.getToken(), ';')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_EOE()

	elif lex.getToken().lexeme == 'if':
		lex.nextToken()

		operatorToken = lex.getToken()
		if lex.getToken().tokenType != tokenType['PARENTHESES_OPEN']:
			kill(lex.getToken(), '(')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()

		if lex.getToken().tokenType != tokenType['PARENTHESES_CLOSE']:
			kill(lex.getToken(), ')')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_closingParenthesis()
			exp_symid =_if(operatorToken)
			SKIPIF = i_if(exp_symid)

		statement()

		if PASS_NUMBER == 2: 
			SKIPELSE = i_skip(SKIPIF)

		if lex.getToken().lexeme == 'else':
			lex.nextToken()
			statement()

			if PASS_NUMBER == 2: 
				i_else(SKIPELSE)

	elif lex.getToken().lexeme == 'while':
		lex.nextToken()

		if PASS_NUMBER == 2:
			BEGIN = i_begin()

		operatorToken = lex.getToken()
		if lex.getToken().tokenType != tokenType['PARENTHESES_OPEN']:
			kill(lex.getToken(), '(')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()

		if lex.getToken().tokenType != tokenType['PARENTHESES_CLOSE']:
			kill(lex.getToken(), ')')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_closingParenthesis()
			exp_symid =_while(operatorToken)
			ENDWHILE = i_while(exp_symid)

		statement()

		if PASS_NUMBER == 2:
			i_end(BEGIN, ENDWHILE)
		

	elif lex.getToken().lexeme == 'return':
		lex.nextToken()
		
		returnedSomething = False
		if isExpressionStart(lex.getToken()):
			expression()
			returnedSomething = True

		semicolonToken = lex.getToken()
		if lex.getToken().lexeme != ';':
			kill(lex.getToken(), ';')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			return_symid = _return(returnedSomething=returnedSomething)
			if return_symid != None:
				i_return(return_symid)
			else:
				i_rtn(semicolonToken)


	elif lex.getToken().lexeme == 'cout':
		lex.nextToken()    

		if lex.getToken().tokenType != tokenType['OUTPUT']:
			kill(lex.getToken(), '<<')
		lex.nextToken()

		expression()

		if lex.getToken().lexeme != ';':
			kill(lex.getToken(), ';')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			exp_symid = _cout()
			i_cout(exp_symid)
		

	elif lex.getToken().lexeme == 'cin':
		lex.nextToken()

		if lex.getToken().tokenType != tokenType['INPUT']:
			kill(lex.getToken(), '>>')
		lex.nextToken()

		expression()

		if lex.getToken().lexeme != ';':
			kill(lex.getToken(), ';')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			exp_symid = _cin()
			i_cin(exp_symid)
		

	elif lex.getToken().lexeme == 'switch':
		lex.nextToken()

		operatorToken = lex.getToken()
		if lex.getToken().tokenType != tokenType['PARENTHESES_OPEN']:
			kill(lex.getToken(), '(')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()

		if lex.getToken().tokenType != tokenType['PARENTHESES_CLOSE']:
			kill(lex.getToken(), ')')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_closingParenthesis()
			_switch()

		case_block()
		

	elif lex.getToken().lexeme == 'break':
		lex.nextToken()
		
		if lex.getToken().lexeme != ';':
			kill(lex.getToken(), ';')
		lex.nextToken()

	else:
		kill(lex.getToken(), 'statement')


def expression():
	tracker()

	operatorToken = lex.getToken()
	literalToken = lex.getToken()
	identifierToken = lex.getToken()

	if lex.getToken().tokenType == tokenType['PARENTHESES_OPEN']:
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()

		if lex.getToken().tokenType != tokenType['PARENTHESES_CLOSE']:
			kill(lex.getToken(), ')')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_closingParenthesis()

		if isExpressionzStart(lex.getToken()):
			expressionz()

	elif lex.getToken().lexeme == 'true':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_lPush(literalToken)

		if isExpressionzStart(lex.getToken()):
			expressionz()

	elif lex.getToken().lexeme == 'false':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_lPush(literalToken)

		if isExpressionzStart(lex.getToken()):
			expressionz()

	elif lex.getToken().lexeme == 'null':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_lPush(literalToken)

		if isExpressionzStart(lex.getToken()):
			expressionz()

	elif lex.getToken().lexeme == 'this':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_iPush(identifierToken)
			_iExist()

		if lex.getToken().lexeme == '.':
			member_refz()

		if isExpressionzStart(lex.getToken()):
			expressionz()

	elif lex.getToken().lexeme in ['+','-'] or lex.getToken().tokenType == tokenType['NUMBER']:
		numeric_literal()

		if isExpressionzStart(lex.getToken()):
			expressionz()

	elif lex.getToken().tokenType == tokenType['CHARACTER']:
		character_literal()

		if isExpressionzStart(lex.getToken()):
			expressionz()

	elif lex.getToken().tokenType == tokenType['IDENTIFIER']:
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_iPush(identifierToken)

		if lex.getToken().tokenType == tokenType['PARENTHESES_OPEN'] or lex.getToken().tokenType == tokenType['ARRAY_BEGIN']:
			fn_arr_member()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_iExist()

		if lex.getToken().lexeme == '.':
			member_refz()

		if isExpressionzStart(lex.getToken()):
			expressionz()
	else:
		kill(lex.getToken(), 'expression')
	

def fn_arr_member():
	tracker()

	operatorToken = lex.getToken()
	if lex.getToken().tokenType == tokenType['PARENTHESES_OPEN']:
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)
			_BAL()

		if isExpressionStart(lex.getToken()):
			argument_list()

		if lex.getToken().tokenType != tokenType['PARENTHESES_CLOSE']:
			kill(lex.getToken(), ')')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_closingParenthesis()
			_EAL()
			_func()

	elif lex.getToken().tokenType == tokenType['ARRAY_BEGIN']:
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()

		if lex.getToken().tokenType != tokenType['ARRAY_END']:
			kill(lex.getToken(), [']'])
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_closingSquareBracket()
			_arr()

	else:
		kill(lex.getToken(), ['[','(']) 


def argument_list():
	tracker()

	expression()

	while lex.getToken().lexeme == ',':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_argument()

		expression()


def member_refz():
	tracker()

	if lex.getToken().lexeme != '.':
		kill(lex.getToken(), ['.'])
	lex.nextToken()

	identifierToken = lex.getToken()
	if lex.getToken().tokenType != tokenType['IDENTIFIER']:
		kill(lex.getToken(), 'identifier')
	lex.nextToken()

	# SEMANTICS
	if PASS_NUMBER == 2:
		_iPush(identifierToken)

	if lex.getToken().tokenType == tokenType['PARENTHESES_OPEN'] or lex.getToken().tokenType == tokenType['ARRAY_BEGIN']:
		fn_arr_member()

	# SEMANTICS
	if PASS_NUMBER == 2:
		_rExist()

	if lex.getToken().lexeme == '.':
		member_refz()


def expressionz():
	tracker()

	operatorToken = lex.getToken()

	if lex.getToken().lexeme == '=':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		assignment_expression()
	elif lex.getToken().lexeme == 'and':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	elif lex.getToken().lexeme == 'or':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	elif lex.getToken().lexeme == '==':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	elif lex.getToken().lexeme == '!=':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	elif lex.getToken().lexeme == '<=':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	elif lex.getToken().lexeme == '>=':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	elif lex.getToken().lexeme == '<':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	elif lex.getToken().lexeme == '>':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	elif lex.getToken().lexeme == '+':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	elif lex.getToken().lexeme == '-':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	elif lex.getToken().lexeme == '*':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	elif lex.getToken().lexeme == '/':
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2: 
			_oPush(operatorToken)

		expression()
	else:
		kill(lex.getToken(), 'expressionz')


def assignment_expression():
	tracker()

	if isExpressionStart(lex.getToken()):
		expression()
	elif lex.getToken().lexeme == 'new':
		lex.nextToken()
		type()
		new_declaration()
	else: 
		kill(lex.getToken(), ['expression', 'new'])


def new_declaration():
	tracker()

	operatorToken = lex.getToken()
	if lex.getToken().tokenType == tokenType['PARENTHESES_OPEN']:
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2:
			_oPush(operatorToken)
			_BAL()

		if isExpressionStart(lex.getToken()):
			argument_list()

		if lex.getToken().tokenType != tokenType['PARENTHESES_CLOSE']:
			kill(lex.getToken(), ')')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2:
			_closingParenthesis()
			_EAL()
			_newObj()

	elif lex.getToken().tokenType == tokenType['ARRAY_BEGIN']:
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2:
			_oPush(operatorToken)

		expression()
		if lex.getToken().tokenType != tokenType ['ARRAY_END']:
			kill(lex.getToken(), ']')
		lex.nextToken()

		# SEMANTICS
		if PASS_NUMBER == 2:
			_closingSquareBracket()
			_newArr()

	else:
		kill(lex.getToken(), ['(', '['])
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^




""" class: OperatorStack  ************************************************************
****************************************************************************************"""
class OperatorStack(list):
	def __init__(self):
		super(list).__init__()

	def print(self):
		print('\n\n*** Operator Stack ********************')
		if self:
			for token in self:
				print(token.toString())
				print('----') 
		else:
			print('EMPTY')
		print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



""" class: SemanticActionStack  ************************************************************
****************************************************************************************"""
class SemanticActionStack(list):
	def __init__(self):
		super(list).__init__()

	def print(self):
		print('\n\n*** Semantic Action Stack *************')
		if self: 
			for item in self[::-1]:
				print(item.toString(), end='')
				print('----') 
		else: 
			print('EMPTY')
		print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



""" class: SemanticActionRecord  ************************************************************
****************************************************************************************"""
class SAR(dict):
	def __init__(self, **kwargs):
		super(dict).__init__()
		self.update(kwargs)

	def toString(self):
		text = ''
		for key in self:
			if isinstance(self[key], Token):
				text += str(key) + ': ' + self[key].toString() + '\n'
			else: 
				text += str(key) + ': ' + str(self[key]) + '\n'
		return text

# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^




""" Semantic Routine Helpers  ************************************************************
****************************************************************************************"""
def semKill(message):
	print(message)
	if TRACKER_ON: 
		print('routine that triggered the error: ' + inspect.stack()[1][3])
	sys.exit()

def operatorFunctionality(operator):

	# get top two sars. Expected contents: symid, token
	B_sar = SAS.pop()
	A_sar = SAS.pop()

	# Get symids the sars
	B_symid = B_sar['symid']
	A_symid = A_sar['symid']

	# Get tokens from the sars
	B_token = B_sar['token']
	A_token = A_sar['token']

	# get symbol from symbol table
	B_symbol = ST[B_symid]
	A_symbol = ST[A_symid]

	# get the types of A and B from their symbols
	B_type = B_symbol['data']['theType']
	A_type = A_symbol['data']['theType']


	# Checks
	tempVar_symid = ''
	if operator in ['+', '-', '*', '/']:

		# Test that B can be added to A (they both have type int)
		if B_type != A_type or A_type != 'int':
			# report semantic error
			semKill(str(A_token.lineNumber) + ': Invalid Operation ' + A_type + ' ' + A_symbol['lexeme'] + ' ' + operator + ' ' + B_type + ' ' + B_symbol['lexeme'])
		
		# create a temporary variable, create the temporary variable's token, put symid and token into a sar, push to SAS
		tempVar_symid = createTempAndPush(prefix='T', scope=None, theType='int', lexeme=None, token=A_token)


	elif operator in ['<', '>', '<=', '>=']:

		# IF THESE OPERATORS CAN HAVE INTS AND CHARS, BUT BOTH OPERANDS MUST BE THE SAME TYPE
		if A_type not in ['int', 'char'] or B_type not in ['int', 'char'] or A_type != B_type:
			semKill(str(A_token.lineNumber) + ': Invalid Operation ' + A_type + ' ' + A_symbol['lexeme'] + ' ' + operator + ' ' + B_type + ' ' + B_symbol['lexeme'])

		# create a temporary variable, create the temporary variable's token, put symid and token into a sar, push to SAS
		tempVar_symid = createTempAndPush(prefix='T', scope=None, theType='bool', lexeme=None, token=A_token)


	elif operator in ['==', '!=']:

		# Test that B is the same type as A (these work on all data types) OR that the B_type is a Null (for example, x == null)
		if A_type != B_type and B_type != 'null':
			semKill(str(A_token.lineNumber) + ': Invalid Operation ' + A_type + ' ' + A_symbol['lexeme'] + ' ' + operator + ' ' + B_type + ' ' + B_symbol['lexeme'])

		# create a temporary variable, create the temporary variable's token, put symid and token into a sar, push to SAS
		tempVar_symid = createTempAndPush(prefix='T', scope=None, theType='bool', lexeme=None, token=A_token)


	elif operator in ['and', 'or']:

		# Test that both a and b are of type bool, report the right error depending on operator. 
		if A_type != 'bool':
			if operator == 'and':
				semKill(str(A_token.lineNumber) + ': And requires bool found ' + A_type)
			elif operator == 'or':
				semKill(str(A_token.lineNumber) + ': Or requires bool found ' + A_type)
		if B_type != 'bool':
			if operator == 'and':
				semKill(str(B_token.lineNumber) + ': And requires bool found ' + B_type)
			elif operator == 'or':
				semKill(str(B_token.lineNumber) + ': Or requires bool found ' + B_type)	

		# create a temporary variable, create the temporary variable's token, put symid and token into a sar, push to SAS
		tempVar_symid = createTempAndPush(prefix='T', scope=None, theType='bool', lexeme=None, token=A_token)


	elif operator == '=':
		
		# *** only user defined class types can be assigned to null ******************************************************
		# Make sure B can be assigned to A. 
		# if B is the same type as A, no error.  If B is null and A is a class type or an array type, no error. 
		if B_type == A_type:
			pass
		elif B_symbol['lexeme'] == 'null' and A_token.tokenType == tokenType['IDENTIFIER'] and A_type not in ['int', 'char', 'bool', 'sym', 'void']:
			# NO ERROR
			pass
		else:
			# report semantic error
			semKill(str(A_token.lineNumber) + ': Invalid Operation ' + A_type + ' ' + A_symbol['lexeme'] + ' ' + operator + ' ' + B_type + ' ' + B_symbol['lexeme'])

		# Make sure the left hand operand is not a constant
		if A_symbol['kind'] in ['nlit', 'hlit', 'true', 'false', 'null'] or A_token.lexeme == 'this': 
			semKill(str(A_token.lineNumber) + ': Invalid Operation ' + A_type + ' ' + A_symbol['lexeme'] + ' ' + operator + ' ' + B_type + ' ' + B_symbol['lexeme'])

		# no need to create temp vars or put anyting on the SAS (we don't allow for nested assignment statements)

	else: 
		print('did not recognize operator: ' + str(operator))
		sys.exit(1)


	return {
		'A_symid' : A_symid, 
		'B_symid' : B_symid, 
		'tempVar_symid' : tempVar_symid, 
		'token' : A_token
	}

'''
lexeme - will usually be the symid, but not always (e.g. this), so we have a different param for it
token - just for the line number we'll need to make the token that represents the temp variable.  
'''
def createTempAndPush(prefix, scope, theType, lexeme, token):
	# Create temporary variable in symbol table, create a sar to represent it, push the sar to Sas
	symid = generateSymid(prefix)
	if not lexeme:
		lexeme = symid[:]  
	if not scope:
		scope = None
	ST.add(scope=scope, symid=symid, lexeme=lexeme, kind='temp', theType=theType, accessMod='private')
	token = Token(lexeme=lexeme, tokenType=tokenType['TEMP'], lineNumber=token.lineNumber)
	resultSar = SAR(symid=symid , token=token)
	SAS.append(resultSar)

	return symid


def callOperator(operatorToken):

	# pull operator lexeme out of given token 
	operator = operatorToken.lexeme

	# Route the operator to the correct operation function
	if operator == '+':
		_addOperator(operator)
	elif operator == '-':
		_subtractOperator(operator)
	elif operator == '*':
		_multiplyOperator(operator)
	elif operator == '/':
		_divideOperator(operator)
	elif operator == '<':
		_lessThanOperator(operator)
	elif operator == '>':
		_greaterThanOperator(operator)
	elif operator == '<=':	
		_lessThanEqualToOperator(operator)
	elif operator == '>=':
		_greaterThanEqualToOperator(operator)
	elif operator == '==':
		_equalOperator(operator)
	elif operator == '!=':
		_notEqualOperator(operator)
	elif operator == 'and':
		_andOperator(operator)
	elif operator == 'or':
		_orOperator(operator)
	elif operator == '=':
		_assignmentOperator(operator)
	else: 
		print('callOperator error: popped an operator we did not recognize: ' + operatorToken.lexeme)

# arglist is a list of symids that should all represent parameters
def getArglistTypes(arglist):
	# Pull types out of arglist and place in a string for the error message
	arglistTypes = ''
	for index in range(len(arglist)):
		param_symid = arglist[index] 
		arglistTypes += ST[param_symid]['data']['theType']
		if index < len(arglist) - 1:
			arglistTypes += ','
	return arglistTypes 

def isType(token):
	# skip the check if the type is a built in type
	if not isBuiltInType(token):
		result = ST.findAllInScope(scope='g', lexeme=token.lexeme, kindList=['class'])
		if not result: 
			return False
	return True

def eoeFunctionality():
	# Pop operators off the stack, perform operation
	while len(OS) > 0:

		# pop operator token off the OS
		operatorToken = OS.pop()

		# call the appropriate operator function
		callOperator(operatorToken)
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^




""" SEMANTIC ACTION ROUTINES  ************************************************************
****************************************************************************************"""
def _iPush(identifierToken):
	tracker()

	# Put token into a sar
	identifierSar = SAR(token=identifierToken)

	# place sar on top of the SAS
	SAS.append(identifierSar)


def _lPush(literalToken):
	tracker()

	# get the symid of the literal from the symbol table 
	literalSymid = ST.findFirst(scope='g', lexeme=literalToken.lexeme, kindList=['hlit', 'nlit', 'true', 'false', 'null'])
	if literalToken.lexeme == 'this': 
		literalSymid = 'this'

	# Create a Sar with the token in it
	literalSar = SAR(token=literalToken, symid=literalSymid)

	# push literal sar onto SAS
	SAS.append(literalSar)



def _oPush(operatorToken):
	tracker()

	# while OS is not empty AND operatorToken has <= precedence of the top of the OS
	while len(OS) != 0 and onStackOperatorPrecedence[OS[len(OS) - 1].lexeme] > inputOperatorPrecedence[operatorToken.lexeme]:

		# pop operator token off the OS
		topOfOS = OS.pop()

		# call the appropriate operator function
		callOperator(topOfOS)


	# Push token holding the operator onto the OS
	OS.append(operatorToken)


def _tPush(typeToken):
	tracker()

	# Put token holding the type into a SAR
	typeSar = SAR(token=typeToken)

	# place sar on top of the SAS
	SAS.append(typeSar)


def _iExist():
	tracker()

	# pop top sar off the SAS.  Could be a 
	# tokenSar from #iPush
	# arrSar from #arr
	# funcSar from #func
	# thisSar from #iPush
	topSar = SAS.pop()

	# if topSar is a thisSar
	if not (topSar.keys() - {'token'}) and topSar['token'].lexeme == 'this':

		# 'THIS' CAN ONLY BE USED IN A CLASS METHOD OR CLASS CONSTRUCTOR
		# make sure 'this' is only used in a constructor or method 
		# if we're three scopes deep in kxi, we know we're in a constructor or a method. 
		if len(ST.scope.split('.')) != 3:
			semKill(str(topSar['token'].lineNumber) + ': Variable ' + topSar['token'].lexeme + ' not defined')

		# Save theType, create a symid, create the lexeme
		tempVar_type = ST.popScope(ST.popScope(ST.scope), returnRemoved=True)

		# if we want a temp var associated with 'this'
		createTempAndPush(prefix='T', scope=None, theType=tempVar_type, lexeme='this', token=topSar['token'])

		# # if we do NOT want a temp var associated with 'this'
		# # create the symid Sar
		# symidSar = SAR(symid='this', token=topSar['token'])
		# # push the SAR onto the SAS
		# SAS.append(symidSar)


		
	# if topSar is a tokenSar (represents a variable or an unindexed array)
	elif not (topSar.keys() - {'token'}):

		# get symid of variable that matches the lexeme and is NOT an array type. 
		matchedVariableSymid = ST.findFirst(lexeme=topSar['token'].lexeme, kindList=['lvar', 'param', 'ivar'], theType='')

		# get symid of array that matches the lexeme that is NOT a variable type
		matchedArraySymid = ST.findFirst(lexeme=topSar['token'].lexeme, kindList=['lvar', 'param', 'ivar'], theType='@')

		# First each scope, there can never be a variable and an array type with the same lexeme thanks to _dup 
		# Because we use findFirst, we could find variables/arrays at higher scopes. 
		# So, if both of the previous findFirst functions find something, take the one with the deeper scope.   
		matchedSymid = None

		# if we found both an array and a variable,
		if matchedVariableSymid and matchedArraySymid:
			# use the one with the deeper scope. 
			variable_scope_length = len(ST[matchedVariableSymid]['scope'].split('.'))
			array_scope_length = len(ST[matchedArraySymid]['scope'].split('.'))

			# if the found variable has the deper scope, use it's type
			if variable_scope_length > array_scope_length:
				matchedSymid = matchedVariableSymid

			# if the found array has the deeper scope, use it's type
			elif variable_scope_length < array_scope_length:
				matchedSymid = matchedArraySymid
			else:
				print('iExist error - dup did not do its job.  Found variable and array with same lexeme in the same scope. ')

		# if we only found a variable, use it's type
		elif matchedVariableSymid:
			matchedSymid = matchedVariableSymid
		
		# if we only found an array, use it's type
		elif matchedArraySymid:
			matchedSymid = matchedArraySymid

		# if we could not find a variable OR an unindexed array with that lexeme in or above the current scope, error. 
		if not matchedSymid: 
			semKill(str(topSar['token'].lineNumber) + ': Variable ' + topSar['token'].lexeme + ' not defined')


		# IF I WANT TO CREATE A TEMP VAR FOR EVERY IEXIST TOPSAR CASE, INCLUDING VARIABLE
		# Save theType, create a symid, create the lexeme
		# tempVar_type = ST[matchedSymid]['data']['theType']
		# tempVar_symid = generateSymid('T')
		# tempVar_lexeme = tempVar_symid[:]


		# IF I DO NOT WANT TO CREATE A TEMP VAR FOR THE VARIABLE IEXIST TOPSAR CASE
		# create the symid Sar
		symidSar = SAR(symid=matchedSymid, token=topSar['token'])

		# push the SAR onto the SAS
		SAS.append(symidSar)



	# if topSar is an arrSar (represents an indexed array)
	elif not (topSar.keys() - {'symid', 'token'}):

		# get symid of variable that matches the lexeme AND is an array type. 
		matchedSymid = ST.findFirst(lexeme=topSar['token'].lexeme, kindList=['lvar', 'param', 'ivar'], theType='@')

		# if we could not find an array variable with that lexeme in or above the current scope, error. 
		if not matchedSymid: 
			semKill(str(topSar['token'].lineNumber) + ': Array ' + topSar['token'].lexeme + ' not defined')


		# Save theType, create a symid, create the lexeme
		# this temporary variable will represent a reference! Mark it as such.  
		tempVar_type = ST[matchedSymid]['data']['theType'][1:]

		tempVar_symid = createTempAndPush(prefix='R', scope=None, theType=tempVar_type, lexeme=None, token=topSar['token'])

		# Create a quad!! :D
		i_arr(matchedSymid, topSar['symid'], tempVar_symid, topSar['token'])



	# if topSar is a funcSar (represents a function call)
	elif not (topSar.keys() - {'arglist', 'token'}): 
		# pull out arglist from topSar
		arglist = topSar['arglist']

		# get symid of function that matches the lexeme
		matchedSymid = ST.findFirst(lexeme=topSar['token'].lexeme, kindList=['method'], params=arglist)

		# if we could not find a method with that lexeme, order, arity, and type in the current scope or above, error 
		if not matchedSymid: 
			semKill(str(topSar['token'].lineNumber) + ': Function ' + topSar['token'].lexeme + '(' + getArglistTypes(arglist) + ') not defined')

		# Save theType, create a symid, create the lexeme
		tempVar_type = ST[matchedSymid]['data']['returnType']

		# Represents the return value of the function
		tempVar_symid = createTempAndPush(prefix='T', scope=None, theType=tempVar_type, lexeme=None, token=topSar['token'])

		# Create the quads
		i_frame('this', matchedSymid, arglist, tempVar_symid, topSar['token'])



	# else, 
	else: 
		semKill('_iExist popped a sar we did not recognize: ' + topSar.toString())


	


def _vPush():
	tracker()
	variableSymidSAR = SAS.pop()

	# create a SAR
	varSar = SAR(symid=variableSymidSAR['symid'], token=variableSymidSAR['token'])

	# push the SAR to the SAS
	SAS.append(varSar)

def _rExist():
	tracker()

	# pop B_sar off the SAS. Could be a this, func, array reference, or variable that has not been proven to exist yet.  
	# expected contents: token, arglist | token, symid | token
	B_sar = SAS.pop()

	# pop A_sar off the SAS. Could be a this, func, array reference, or variable that HAS been proven to exist already. 
	# expected contents: token, symid
	A_sar = SAS.pop()



	# ++++ PROCESS A_sar +++++++++++++++++++++++++++++++++++++++++++++++++
	'''
	pull out A_sar's symid
	get theType or returnType from the symbol table (will depend on A_sars sar type)
	set A_type variable to theTYpe or returnType
	'''
	A_type = ''
	A_symid = A_sar['symid']

	# if A_sar represents a variable or this
	if A_sar['symid'] != None and A_sar['symid'] in ST and ST[A_sar['symid']]['data']['theType'] != None and ST[A_sar['symid']]['data']['theType'][0] != '@':
		# pull theType from the symbol in the symbol table
		A_type = ST[A_sar['symid']]['data']['theType']

	# if A_sar represents an array reference
	elif A_sar['symid'] != None and A_sar['symid'] in ST and ST[A_sar['symid']]['data']['theType'] != None and ST[A_sar['symid']]['data']['theType'][0] == '@':
		# pull theTYpe from the symbol in the symbol table and 
		# change it from it's array form into it's singular form
		A_type = ST[A_sar['symid']]['data']['theType'][1:]

	# if A_sar represents a function
	elif A_sar['symid'] != None and A_sar['symid'] in ST and ST[A_sar['symid']]['data']['returnType'] != None:
		# pull the returnType from the symbol in the symbol table
		A_type = ST[A_sar['symid']]['data']['returnType']

	# else, we get an error
	else:
		print('rExist Error - A_sar not proven to be existing yet.  No symid OR It\'s symid is not found in the symbol table. ')
		sys.exit(1)



	# ++++ PROCESS B_sar, Error if we can't find it +++++++++++++++++++++++++++++++++++++++++++++++
	'''
	I'll need A_type to be filled in to know what scope to search for B in (g.<A_type>)

	pull out B_sar's token
	find a variable in the symbol table that matches what is in B_sar (depends on the sar type of B_sar)  
	set B_type variable to B_sar's theTYpe or returnType respectively. 
	'''
	# if A_sar is a 'this' or if the current class we're parsing is where 
	# this referenced thing comes from, then B_sar does not need to be a public member
	# default to looking for a public member. 
	accessMod = 'public'
	if A_sar['token'].lexeme == 'this': 
		accessMod = None 

	# Use A_type to create the scope we'll search for B_sar in the symbol table. 
	scopeToSearch = 'g.' + A_type

	# Save the type of the B_sar that we find in the symbol table here. 
	B_type = ''

	# if B_sar is a tokenSar (represents a variable or an unindexed array)
	if not (B_sar.keys() - {'token'}):

		# find a symbol in the symbol table that's a variable type
		B_symid_variable = ST.findFirstInScope(scope=scopeToSearch, lexeme=B_sar['token'].lexeme, theType='', kindList=['ivar'], accessMod=accessMod)

		# find a symbol in the symbol table that's an array type
		B_symid_array = ST.findFirstInScope(scope=scopeToSearch, lexeme=B_sar['token'].lexeme, theType='@', kindList=['ivar'], accessMod=accessMod)

		# all instance variables are in the same scope depth (g.<className>), so we don't have to worry about checking scope depths. 
		# we are garunteed to never have an array and a variable with the same lexeme at that scope level, so use the symid of whichever one you found. 
		B_symid = None
		if B_symid_variable:
			B_symid = B_symid_variable
		elif B_symid_array:
			B_symid = B_symid_array

		# if nothing found, error
		if not B_symid: 
			semKill(str(B_sar['token'].lineNumber) + ': Variable ' + B_sar['token'].lexeme + ' not defined/public in class ' + A_type)

		# put theType into B_type
		B_type = ST[B_symid]['data']['theType']

		# tempVar_symid represents the value of the variable that was referenced
		tempVar_symid = createTempAndPush(prefix='R', scope=None, theType=B_type, lexeme=None, token=B_sar['token'])


		# ICODE
		i_ref(A_symid, B_symid, tempVar_symid, A_sar['token'])
		

	# if B_sar is an arrSar
	elif not (B_sar.keys() - {'symid', 'token'}):

		# token: array name
		# symid: expression that indexes into the array.  

		# find a symbol in the symbol table that's an array type. 
		B_symid = ST.findFirstInScope(scope=scopeToSearch, lexeme=B_sar['token'].lexeme, theType='@', kindList=['ivar'], accessMod=accessMod)

		# pull the expression symid out of the sar
		exp_symid = B_sar['symid']

		# if nothing found, error
		if not B_symid: 
			semKill(str(B_sar['token'].lineNumber) + ': Array ' + B_sar['token'].lexeme + ' not defined/public in class ' + A_type)

		# get the singular version of the array type
		B_type = ST[B_symid]['data']['theType'][1:]

		# tempVar_symid represents the reference
		arr_tempVar_symid = generateSymid('R')
		ST.add(symid=arr_tempVar_symid, lexeme=arr_tempVar_symid, kind='temp', theType=ST[B_symid]['data']['theType'], accessMod='private')

		# this temp var represents the final value after the reference and the indexing into has been completed
		final_tempVar_symid = generateSymid('R')
		ST.add(symid=final_tempVar_symid, lexeme=final_tempVar_symid, kind='temp', theType=B_type, accessMod='private')

		# Create a token that represents the reference
		final_tempVar_token = Token(lineNumber=B_sar['token'].lineNumber, lexeme=final_tempVar_symid, tokenType=tokenType['REFERENCE'])

		# Create a sar with the symid of the temporary variable and the token
		final_tempVar_sar = SAR(symid=final_tempVar_symid, token=final_tempVar_token)

		# Push sar onto the stack
		SAS.append(final_tempVar_sar)

		# ICODE
		# 1st (reference), 2nd (variable referenced), 3rd (temp variable representing the reference)
		i_ref(A_symid, B_symid, arr_tempVar_symid, A_sar['token'])

		# 1st (the var that represents the referenc), 2nd (expression that indexes into the array), 3rd (temp variable that represents the final value)
		i_arr(arr_tempVar_symid, exp_symid, final_tempVar_symid, A_sar['token'])


	# if B_sar is a funcSar
	elif not (B_sar.keys() - {'arglist', 'token'}): 

		# find a symbol in the symbol table that's a function type
		B_symid = ST.findFirstInScope(scope=scopeToSearch, lexeme=B_sar['token'].lexeme, kindList=['method'], accessMod=accessMod, params=B_sar['arglist'])

		# if nothing found, error
		if not B_symid: 
			# Error
			semKill(str(B_sar['token'].lineNumber) + ': Function ' + B_sar['token'].lexeme + '(' + str(getArglistTypes(B_sar['arglist'])) + ') not defined/public in class ' + A_type)

		# put the returnType in B_type
		B_type = ST[B_symid]['data']['returnType']

		# tempVar_symid represents the return value of the function
		tempVar_symid = createTempAndPush(prefix='T', scope=None, theType=B_type, lexeme=None, token=B_sar['token'])

		# ICODE
		i_frame(A_symid, B_symid, B_sar['arglist'], tempVar_symid, B_sar['token'])


	# if B_sar is a thisSar
	elif not (B_sar.keys() - {'token'}) and B_sar['token'].lexeme == 'this':
		# *** JUDGEMENT CALL *****************************
		# We don't allow a 'this' to be the B_sar, so we toss an ERROR
		semKill(str(B_sar['token'].lineNumber) + ': Variable ' + B_sar['token'].lexeme + ' not defined/public in class ' + A_type)

	# else, we don't recognize the sar
	else: 
		print('_rExist B_sar is not a sar we recognize: \n'  + B_sar.toString())
		sys.exit(1)





def _tExist():
	tracker()

	# Expected contents of top SAR: 
	#	token - token that holds an identifier that could represent a class
	topSar = SAS.pop()
	token = topSar['token']

	# skip the check if the type is a built in type
	if not isType(token):
		semKill(str(token.lineNumber) + ': Type ' + token.lexeme + ' not defined')


def _BAL():
	tracker()

	# Make a blank SAR. 
	balSar = SAR()

	# Push the balSar
	SAS.append(balSar)


def _EAL():
	tracker()

	paramSymidList = []

	# stop collecting parameters when we find the _BAL sar
	while len(SAS) > 0 and SAS[len(SAS) - 1]:
		# Pop the top sar
		# expected contents: symid, token
		topSar = SAS.pop()

		# stick it's symid into the list
		paramSymidList.insert(0, topSar['symid'])

	# get rid of _BAL sar on top of stack
	SAS.pop()

	# create new arglistSar
	arglistSar = SAR(arglist=paramSymidList)

	# push sar onto SAS
	SAS.append(arglistSar)



def _func():
	tracker()

	# expected contents: arglist
	arglistSar = SAS.pop()

	# expected contents: token
	tokenSar = SAS.pop()

	# create funcSar 
	funcSar = SAR(arglist=arglistSar['arglist'], token=tokenSar['token'])

	# place funcSar on SAS
	SAS.append(funcSar)



def _arr():
	tracker()

	# expected contents: symid (represents the expression that indexed into the array)
	expSar = SAS.pop()

	# expected contents: token (represents the name of the array)
	tokenSar = SAS.pop()

	# if symid is not an int type, ERROR
	if not ST.matchingType(symid=expSar['symid'], theType='int'):
		semKill(str(tokenSar['token'].lineNumber) + ': Array requires int index got ' + ST[expSar['symid']]['data']['theType']) 

	# Create an arrSar
	# token (array name), symid (expression)
	arrSar = SAR(token=tokenSar['token'], symid=expSar['symid'])

	# push sar onto SAS
	SAS.append(arrSar)


def _if(token):
	tracker()

	if len(SAS) == 0:
		semKill(str(token.lineNumber) + ': if requires bool got assignment statement')

	# pop expression sar from SAS
	expSar = SAS.pop()

	# test that the expression is a boolean
	if not ST.matchingType(symid=expSar['symid'], theType='bool'):
		semKill(str(expSar['token'].lineNumber) + ': if requires bool got ' + ST[expSar['symid']]['data']['theType'])

	# Get rid of the rest of the SARs on the SAS
	while len(SAS) != 0:
		SAS.pop()

	return expSar['symid']


def _while(token):
	tracker()

	if len(SAS) == 0:
		semKill(str(token.lineNumber) + ': while requires bool got assignment statement')

	# pop expression sar from SAS
	expSar = SAS.pop()

	# test that the expression is a boolean
	if not ST.matchingType(symid=expSar['symid'], theType='bool'):
		semKill(str(expSar['token'].lineNumber) + ': while requires bool got ' + ST[expSar['symid']]['data']['theType'])

	# Get rid of the rest of the SARs on the SAS
	while len(SAS) != 0:
		SAS.pop()

	return expSar['symid']

def _return(returnedSomething=False):
	tracker()

	# Pop operators off the stack, perform operation
	eoeFunctionality()

	# get the returnType of the current function you're parsing. 
	returnType = ''

	# if we're three scopes deep, we need to get the name of the function from the current scope, then look up the function's returnType in the symbol table.  
	if len(ST.scope.split('.')) == 3:

		# get the function's name
		f_name = ST.popScope(scope=ST.scope, returnRemoved=True)

		# get the name of the class the function is in (so we can search that scope in the symbol table)
		class_name = ST.popScope(ST.popScope(ST.scope), returnRemoved=True)

		# search in the symbol table for the function to get it's returnType
		scopeToSearch = 'g.' + class_name 
		f_symid = ST.findFirst(scope=scopeToSearch, lexeme=f_name, kindList=['method'])

		# get the returnType out of the symbol
		returnType = ST[f_symid]['data']['returnType']

	# if we're two scopes deep and we hit this semantic routine, we know we are in the main function, so the return type is void. 
	elif len(ST.scope.split('.')) == 2:
		returnType = ST['main']['data']['returnType']


	# if we returned something, make sure it's type matches the function's return type. 
	if returnedSomething:
		# pop the final expression off the SAS
		expSar = SAS.pop()

		# Get rid of the rest of the SARs on the SAS
		while len(SAS) != 0:
			SAS.pop()

		# test that this final expression has the same type as the function you're currently parsing.  
		if not ST.matchingType(symid=expSar['symid'], theType=returnType):
			semKill(str(expSar['token'].lineNumber) + ': Function requires ' + returnType + ' returned ' + ST[expSar['symid']]['data']['theType'] )

		if expSar['token'].lexeme == 'this':
			return 'this'

		# save the symid of the return value
		return expSar['symid']
	else:
		# Get rid of the rest of the SARs on the SAS
		while len(SAS) != 0:
			SAS.pop()



def _cout():
	tracker()

	# Pop operators off the stack, perform operation
	eoeFunctionality()

	# pop the final expression off the SAS
	expSar = SAS.pop()

	# test that the expression can be printed with cout
	if not ST.matchingType(symid=expSar['symid'], theType='int') and not ST.matchingType(symid=expSar['symid'], theType='char'):
		semKill(str(expSar['token'].lineNumber) + ': cout not defined for ' + ST[expSar['symid']]['data']['theType'])

	# Get rid of the rest of the SARs on the SAS
	while len(SAS) != 0:
		SAS.pop()

	return expSar['symid']


def _cin():
	tracker()

	# Pop operators off the stack, perform operation
	eoeFunctionality()

	# pop the final expression off the SAS
	expSar = SAS.pop()

	# test that the expression can be printed with cout
	if not ST.matchingType(symid=expSar['symid'], theType='int') and not ST.matchingType(symid=expSar['symid'], theType='char'):
		semKill(str(expSar['token'].lineNumber) + ': cin not defined for ' + ST[expSar['symid']]['data']['theType'])

	# Get rid of the rest of the SARs on the SAS
	while len(SAS) != 0:
		SAS.pop()

	return expSar['symid']


# This is obsolete and need not be implemented after kxi 2018
def _atoi():
	pass

# This is obsolete and need not be implemented after kxi 2018
def _itoa():
	pass


def _newObj():
	tracker()

	# pop arglist Sar from SAS. Expected contents: arglist
	arglistSar = SAS.pop()

	# pop typeSar from SAS. expected contents: token
	typeSar = SAS.pop()

	# in the symbol table, look for a constructor that can create an instance of the given type
	scopeToSearch = 'g.' + typeSar['token'].lexeme
	constructor_symid = ST.findFirstInScope(scope=scopeToSearch, lexeme=typeSar['token'].lexeme, kindList=['constructor'], params=arglistSar['arglist'])

	# if we did not find a constructor that lets us make the given type, error. 
	if not constructor_symid:
		semKill(str(typeSar['token'].lineNumber) + ': Constructor ' + typeSar['token'].lexeme + '(' + str(getArglistTypes(arglistSar['arglist'])) + ') not defined') 


	# Create a temporary variable that's a pointer to the beginning of the heap space that was allocated for this object
	allocatedSpacePointer_symid = generateSymid('T')
	ST.add(symid=allocatedSpacePointer_symid, lexeme=allocatedSpacePointer_symid, kind='temp', theType=typeSar['token'].lexeme, accessMod='private')

	# create a temporary variable representing the return value of the constructor (the new object that is made)
	returnVal_symid = createTempAndPush(prefix='T', scope=None, theType=typeSar['token'].lexeme, lexeme=None, token=typeSar['token'])


	# add quads for new object
	class_symid = ST.findFirst(lexeme=typeSar['token'].lexeme, kindList=['class'])
	i_newObj(allocatedSpacePointer_symid, returnVal_symid, class_symid, constructor_symid, arglistSar['arglist'], typeSar['token'])

	'''
	For Future Use
	allocatedSpacePointer_symid - holds the address of the beginning of the allocated space in the heap
	returnVal_symid - holds the address of the allocatedSpacePointer_symid and is marked with an R. 
	'''

def _newArr():
	tracker()

	# pop expressionSar off SAS. Expected contents: symid, token
	expSar = SAS.pop()

	# test that the expression is an integer
	if not ST.matchingType(symid=expSar['symid'], theType='int'):
		semKill(str(expSar['token'].lineNumber) + ': Array requires int index got ' + ST[expSar['symid']]['data']['theType'])

	# pop typeSar from SAS. Expected contents: token
	typeSar = SAS.pop()

	# test if an array of this type can be generated
	if not isType(typeSar['token']): 
		semKill(str(expSar['token'].lineNumber) + ': Type ' + typeSar['token'].lexeme + ' not defined') 


	# expSar holds the expression representing the size of the array. 

	# create a temporary variable representing a pointer to the begining of the space allocated on the heap for this array
	theArrayType = '@' + typeSar['token'].lexeme
	arrPointer_symid = createTempAndPush(prefix='R', scope=None, theType=theArrayType, lexeme=None, token=typeSar['token'])


	# figure out the size of the array type
	theType = typeSar['token'].lexeme
	if theType == 'bool': 
		typeSize_symid = 'sizeOfBool'
	elif theType == 'int': 
		typeSize_symid = 'sizeOfInt'
	elif theType == 'char': 
		typeSize_symid = 'sizeOfChar'
	else: 
		typeSize_symid = 'sizeOfPointer' # pointers are 4 bytes

	# Add quads for new array
	i_newArr(typeSize_symid, expSar['symid'], expSar['symid'], arrPointer_symid, typeSar['token'])



def _CD(xtorIdentifierToken):
	tracker()

	# get the class name from the current scope
	className = ST.popScope(ST.scope, returnRemoved=True)

	# if the constructor name does not match the class name, error
	if className != xtorIdentifierToken.lexeme:
		semKill(str(xtorIdentifierToken.lineNumber) + ': Constructor ' + xtorIdentifierToken.lexeme + ' must match class name ' + className)


''' 
dup
if there are two classes with the same name, error
	(g)

if there are two constructors with the same name in a class, error
	(g.<className>)

if there are two functions in a class with the same name, error
	(g.<className>)

if two member variables in a class have the same name, error
	(g.<className>)

if two local variables have the same name, error
	(g.<className>.<functionName>)
	(g.main)

if a local variable and passed parameter have the same name, error
	(g.<className>.<functionName>)

if two passed parameters have the same name, error
	(g.<className>.<functionName>)


'''
def _dup(token):
	tracker()

	# pull the grammar rule off the function stack :D
	grammarRule = inspect.stack()[1][3][:]

	result = []
	errorMsg = ''
	if grammarRule == 'class_declaration':
		
		result = ST.findAllInScope(lexeme=token.lexeme, kindList=['class'])
		if len(result) > 1:
			semKill(str(token.lineNumber) + ': Duplicate class ' + token.lexeme)

	elif grammarRule == 'class_member_declaration':
		
		# ivar (variable OR array reference)
		if lex.getToken().lexeme in ['=', ';']:
			result = ST.findAllInScope(lexeme=token.lexeme, kindList=['ivar'])
			if len(result) > 1: 
				semKill(str(token.lineNumber) + ': Duplicate variable ' + token.lexeme)

		# func
		elif lex.getToken().lexeme == '(':
			result = ST.findAllInScope(lexeme=token.lexeme, kindList=['method'])
			if len(result) > 1: 
				semKill(str(token.lineNumber) + ': Duplicate function ' + token.lexeme)

	elif grammarRule == 'constructor_declaration':

		result = ST.findAllInScope(lexeme=token.lexeme, kindList=['constructor'])
		if len(result) > 1: 
			semKill(str(token.lineNumber) + ': Duplicate function ' + token.lexeme)


	elif grammarRule in ['variable_declaration', 'parameter']:
		
		resultLvar = ST.findAllInScope(lexeme=token.lexeme, kindList=['lvar'])
		resultParam = ST.findAllInScope(lexeme=token.lexeme, kindList=['param'])

		if len(resultLvar) + len(resultParam) > 1: 
			semKill(str(token.lineNumber) + ': Duplicate variable ' + token.lexeme)
		
		# tell vPush about the symid we found
		if grammarRule == 'variable_declaration':
			result = ST.findAllInScope(lexeme=token.lexeme, kindList=['lvar'])

	else:
		print('dup error: ' + grammarRule + ' called dup and we have not handled that')

	# tell vPush about the symid of the variable (ivar or lvar) that was just created
	if grammarRule in ['class_member_declaration', 'variable_declaration']:
		SAS.append(SAR(symid=result[0], token=token))


# NOT IMPLEMENTED IN CS 4490
def _spawn():
	tracker()

# NOT IMPLEMENTED IN CS 4490
def _lock():
	tracker()

# NOT IMPLEMENTED IN CS 4490
def _release():
	tracker()

# NOT IMPLEMENTED IN CS 4490
def _switch():
	tracker()


def _closingParenthesis():
	tracker()

	# loop until we hit the opening parenthesis. 
	while len(OS) > 0 and OS[len(OS) - 1].tokenType != tokenType['PARENTHESES_OPEN']:
		
		# pop operator token off the OS
		operatorToken = OS.pop()

		# call the appropriate operator function
		callOperator(operatorToken)

	# Remove opening parenthesis from OS
	if len(OS) > 0 and OS[len(OS) - 1].tokenType == tokenType['PARENTHESES_OPEN']:
		OS.pop()
	else:
		print('closingParenthesis problem - popped to an empty operator stack before hitting an opening paranthesis.')



def _closingSquareBracket():
	tracker()

	# loop until we hit the opening parenthesis. 
	while len(OS) > 0 and OS[len(OS) - 1].tokenType != tokenType['ARRAY_BEGIN']:
		
		# pop operator token off the OS
		operatorToken = OS.pop()

		# call the appropriate operator function
		callOperator(operatorToken)

	# Remove opening square bracket from OS
	if len(OS) > 0 and OS[len(OS) - 1].tokenType == tokenType['ARRAY_BEGIN']:
		OS.pop()
	else:
		print('closingSquareBracket problem - popped to an empty operator stack before hitting an opening square bracket.')


def _argument():
	tracker()

	# loop until we hit the opening parenthesis. 
	while len(OS) > 0 and OS[len(OS) - 1].tokenType != tokenType['PARENTHESES_OPEN']:
		
		# pop operator token off the OS
		operatorToken = OS.pop()

		# call the appropriate operator function
		callOperator(operatorToken)


def _EOE():
	tracker()

	# Pop operators off the stack, perform operation
	eoeFunctionality()

	# Get rid of the rest of the SARs on the SAS
	while len(SAS) != 0:
		SAS.pop()




def _addOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('ADD', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)

def _subtractOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('SUB', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)
	
def _multiplyOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('MUL', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)
	
def _divideOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('DIV', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)
	
def _assignmentOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('MOV', quadInfo['B_symid'], quadInfo['A_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)
	
def _lessThanOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('LT', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)

def _greaterThanOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('GT', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)

def _equalOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('EQ', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)

def _lessThanEqualToOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('LE', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)

def _greaterThanEqualToOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('GE', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)

def _andOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('AND', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)

def _orOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('OR', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)

def _notEqualOperator(operator):
	tracker()
	quadInfo = operatorFunctionality(operator)
	i_operatorQuad('NE', quadInfo['A_symid'], quadInfo['B_symid'], quadInfo['tempVar_symid'], quadInfo['token'].lineNumber)


# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^




# ----------------------------------------------------------------------------------------------------
# *** iCode Methods *********************************************************************************
def i_operatorQuad(operator, A_symid, B_symid, tempVar_symid, lineNumber):
	QT.add(label='', operator=operator, operand_1=A_symid, operand_2=B_symid, operand_3=tempVar_symid, comment=CM.get(lineNumber))

def i_ref(A_symid, B_symid, tempVar_symid, token):
	# Create a quad for the reference! 
	QT.add(label='', operator='REF', operand_1=A_symid, operand_2=B_symid, operand_3=tempVar_symid, comment=CM.get(token.lineNumber))

def i_if(exp_symid):
	SKIPIF = generateLabel()
	QT.add(label='', operator='BF', operand_1=exp_symid, operand_2=SKIPIF, operand_3='', comment=CM.get())
	return SKIPIF

def i_skip(SKIPIF):
	SKIPELSE = ''
	if lex.getToken().lexeme == 'else':
		SKIPELSE = generateLabel()
		QT.add(label='', operator='JMP', operand_1=SKIPELSE, operand_2='', operand_3='', comment=CM.get())
	
	QT.add(label=SKIPIF, operator='', operand_1='', operand_2='', operand_3='', comment=CM.get())
	return SKIPELSE

def i_else(SKIPELSE):
	QT.add(label=SKIPELSE, operator='', operand_1='', operand_2='', operand_3='', comment=CM.get())

def i_begin():
	BEGIN = generateLabel()
	QT.add(label=BEGIN, operator='', operand_1='', operand_2='', operand_3='', comment=CM.get())
	return BEGIN
	# make sure the conditional code will get put in the quad we just made. 

def i_while(exp_symid):
	ENDWHILE = generateLabel()
	QT.add(label='', operator='BF', operand_1=exp_symid, operand_2=ENDWHILE, operand_3='', comment=CM.get())
	return ENDWHILE

def i_end(BEGIN, ENDWHILE):
	QT.add(label='', operator='JMP', operand_1=BEGIN, operand_2='', operand_3='', comment=CM.get())
	QT.add(label=ENDWHILE, operator='', operand_1='', operand_2='', operand_3='', comment=CM.get())

def i_cout(exp_symid):
	QT.add(label='', operator='WRITE', operand_1=exp_symid, operand_2='', operand_3='', comment=CM.get())

def i_cin(exp_symid):
	QT.add(label='', operator='READ', operand_1=exp_symid, operand_2='', operand_3='', comment=CM.get())

def i_return(return_symid):
	QT.add(label='', operator='RETURN', operand_1=return_symid, operand_2='', operand_3='', comment=CM.get())

def i_rtn(blockEnd_token):
	QT.add(label='', operator='RTN', operand_1='', operand_2='', operand_3='', comment=CM.get(blockEnd_token.lineNumber))

def i_func(func_symid):
	QT.add(label=func_symid, operator='FUNC', operand_1=func_symid, operand_2='', operand_3='', comment=CM.get())

# allocatedSpacePointer_symid, constructor_symid, arglist, returnVal_symid, token
def i_frame(A_symid, B_symid, arglist=[], returnVal_symid='', token=''):
	QT.add(label='', operator='FRAME', operand_1=B_symid, operand_2=A_symid, operand_3='', comment=CM.get(token.lineNumber))
	for symid in arglist: 
		QT.add(label='', operator='PUSH', operand_1=symid, operand_2='', operand_3='', comment=CM.get(token.lineNumber))
	QT.add(label='', operator='CALL', operand_1=B_symid, operand_2='', operand_3='', comment=CM.get(token.lineNumber))
	
	if returnVal_symid != '' and ST[returnVal_symid]['data']['theType'] != 'void':
		QT.add(label='', operator='PEEK', operand_1=returnVal_symid, operand_2='', operand_3='', comment=CM.get(token.lineNumber))

def i_stop():
	QT.add(label='', operator='STOP', operand_1='', operand_2='', operand_3='', comment='')	

def i_arr(A_symid, B_symid, tempVar_symid, token):
	# A_symid: Base address of the array
	# B_symid: Temporary variable that holds the offset we use to index into the array
	QT.add(label='', operator='AEF', operand_1=A_symid, operand_2=B_symid, operand_3=tempVar_symid, comment=CM.get(token.lineNumber))
	
def i_newObj(allocatedSpacePointer_symid, returnVal_symid, class_symid, constructor_symid, arglist, token):
	QT.add(label='', operator='NEWI', operand_1=str(ST[class_symid]['size']), operand_2=allocatedSpacePointer_symid, operand_3='', comment=CM.get(token.lineNumber))
	i_frame(allocatedSpacePointer_symid, constructor_symid, arglist, returnVal_symid, token)
	
def i_newArr(typeSize_symid, exp_symid, arrSize_symid, arrPointer_symid, token):
	QT.add(label='', operator='MUL', operand_1=typeSize_symid, operand_2=exp_symid, operand_3=arrSize_symid, comment=CM.get(token.lineNumber))
	QT.add(label='', operator='NEW', operand_1=arrSize_symid, operand_2=arrPointer_symid, operand_3='', comment=CM.get(token.lineNumber))
	
def i_squadfunc(func_symid):
	QT.add(label=func_symid, operator='FUNC', operand_1=func_symid, operand_2='', operand_3='', comment=CM.get())

def i_squadRTN(blockEnd_token):
	QT.add(label='', operator='RTN', operand_1='', operand_2='', operand_3='', comment=CM.get(blockEnd_token.lineNumber))

def i_movSQUAD():
	# copy everything in SQUAD into QT
	QT.QT.extend(QT.SQUAD)
	# empty out SQUAD
	QT.SQUAD.clear()
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



# ---------------------------------------------------------------------------------------------------
# *** TCODE HELPER FUNCTIONS  ***********************************************************************
def generateTCode():
	global tcodeWriter

	# if the tcode file already exists, delete it.
	if os.path.exists(tcodeFilename):
		os.remove(tcodeFilename) 

	# open a file that we'll append tcode lines to. 
	tcodeWriter = open(tcodeFilename, 'a')

	# generate tcode for globals
	genGlobalTcode()

	# loop through 
	for line in QT.QT: 

		# Generate the TCode 
		if line['operator'] == 'ADD':
			T_add(line)
		elif line['operator'] == 'SUB':
			T_sub(line)
		elif line['operator'] == 'MUL':
			T_mul(line)
		elif line['operator'] == 'DIV':
			T_div(line)
		elif line['operator'] == 'MOV':
			T_mov(line)
		elif line['operator'] == 'LT':
			T_lt(line)
		elif line['operator'] == 'GT':
			T_gt(line)
		elif line['operator'] == 'EQ':
			T_eq(line)
		elif line['operator'] == 'LE':
			T_le(line)
		elif line['operator'] == 'GE':
			T_ge(line)
		elif line['operator'] == 'AND':
			T_and(line)
		elif line['operator'] == 'OR':
			T_or(line)
		elif line['operator'] == 'NE':
			T_ne(line)
		elif line['operator'] == 'FRAME':
			T_frame(line)
		elif line['operator'] == 'PUSH': # to test
			T_push(line)
		elif line['operator'] == 'CALL':
			T_call(line)
		elif line['operator'] == 'PEEK': # to test
			T_peek(line)
		elif line['operator'] == 'FUNC':
			T_func(line)
		elif line['operator'] == 'RTN':
			T_rtn(line)
		elif line['operator'] == 'RETURN': # to test
			T_return(line)
		elif line['operator'] == 'REF': # to do 
			T_ref(line)
		elif line['operator'] == 'AEF': # to do
			T_aef(line)
		elif line['operator'] == 'BF':
			T_bf(line)
		elif line['operator'] == 'JMP':
			T_jmp(line)
		elif line['operator'] == 'WRITE':
			T_write(line)
		elif line['operator'] == 'READ':
			T_read(line)
		elif line['operator'] == 'NEW':  # to test (used only on arrays)
			T_new(line)
		elif line['operator'] == 'NEWI':  # to test (used only on objects)
			T_newi(line)
		elif line['operator'] == 'STOP':
			T_stop(line)
		else:
			print('did not recognize the icode instruction: ' + line['operator'])

	# generate error reporting functions
	genOverUnderFlow()

	# close the file writer
	tcodeWriter.close()

	
'''
returns the symid's offset in memory. 

calling context can tell which base address to use with this: 
 global
 	will always be positive or 0.  
 	in ST[symid], scope will be 'g'
 heap
 	will always be positive
 	in ST[symid], scope will not be 'g'
 stack 
 	will always be negative 
'''
def getLocation(symid):
	# if symid is 'this', it will be on the stack, inside the current activation record. 
	# its offset will always be -8
	if symid == 'this': 
		return -8

	# get the symbol from the symbol table
	symbol = ST[symid]

	# pull the scope out of the symbol 
	scope = symbol['scope']

	# if the value at the memory address of the symid is a global variable
	if scope[0] == 'g' and symbol['kind'] in ['nlit', 'hlit', 'true', 'false', 'null', 'sizeOfPointer', 'sizeOfChar', 'sizeOfInt', 'sizeOfBool']:
		return symbol['offset']

	# if the value at the memory address of the symid is a on the heap
	elif symbol['kind'] == 'ivar':
		return symbol['offset']

	# if the value at the memory address of the symid is a on the stack
	elif symbol['kind'] == 'lvar' or symbol['kind'] == 'param' or symbol['kind'] == 'temp': 
		return symbol['offset']

	else: 
		print('getLocation ERROR: could not sort symid - ' + symid)
		print('symid\'s symbol: ' + str(symbol)) 


'''
Takes the parameters and outputs it to our TCode destination file
'''
def genTLine(label=None, operator='', operand_1='', operand_2='', comment=''):
	labelBuf = 15
	operatorBuf = 10
	op1Buf = 20
	op2Buf = 10
	commentBuf = 30


	# if we were given an instruction
	line = ''
	# if an instruction like this: MOV R1, R2
	if operator and operand_1 and operand_2: 
		line = label.ljust(labelBuf) + operator.ljust(operatorBuf) + (operand_1 + ', ').ljust(op1Buf) + operand_2.ljust(op2Buf)
		if comment: 
			line += '; ' + comment.ljust(commentBuf)
	
	# if an instruction like this: JMR R7
	elif operator and operand_1 and not operand_2:
		line = label.ljust(labelBuf) + operator.ljust(operatorBuf) + operand_1.ljust(op1Buf)
		if comment: 
			line += '; ' + comment.ljust(commentBuf)

	# if we only have a comment and we want it indented
	elif label and comment:
		line = label.ljust(labelBuf) + '; ' + comment.ljust(commentBuf)

	# if we only have a comment and we DO NOT want it indented 
	elif (label == '' or label == ' ') and comment: 
		line = ' '.ljust(labelBuf) + '; ' + comment

	elif label == None and comment: 
		line = '; ' + comment 

	elif label: 
		line = label

	tcodeWriter.write(line + '\n')

	

def genGlobalTcode(): 
	genTLine(comment='----------------------------------------------------------------------------')
	genTLine(comment='GLOBAL VARIABLES')
	genTLine(comment='----------------------------------------------------------------------------')
	for symid in ST:
		symbol = ST[symid] 
		if symbol['scope'] == 'g': 
			if symbol['kind'] == 'hlit': 
				genTLine(label=symbol['symid'], operator='.BYT', operand_1 = symbol['lexeme'])
			elif symbol['kind'] == 'nlit': 
				genTLine(label=symbol['symid'], operator='.INT', operand_1 = symbol['lexeme'])
			elif symbol['kind'] == 'true':
				genTLine(label=symbol['symid'], operator='.INT', operand_1 = '1')
			elif symbol['kind'] == 'false':
				genTLine(label=symbol['symid'], operator='.INT', operand_1 = '0')
			elif symbol['kind'] == 'null':
				genTLine(label=symbol['symid'], operator='.INT', operand_1 = '0')
			elif symbol['kind'] == 'sizeOfPointer':
				genTLine(label=symbol['symid'], operator='.INT', operand_1 = '4')
			elif symbol['kind'] == 'sizeOfChar':
				genTLine(label=symbol['symid'], operator='.INT', operand_1 = '1')
			elif symbol['kind'] == 'sizeOfBool':
				genTLine(label=symbol['symid'], operator='.INT', operand_1 = '4')
			elif symbol['kind'] == 'sizeOfInt':
				genTLine(label=symbol['symid'], operator='.INT', operand_1 = '4')



def genOverUnderFlow(): 
	genTLine(comment='')
	genTLine(comment='----------------------------------------------------------------------------')
	genTLine(comment='ERROR REPORTING FUNCTIONS')
	genTLine(comment='----------------------------------------------------------------------------')

	# -- overflow ---------
	genTLine(label='overflow', operator='CMP', operand_1='R3', operand_2='R3', comment='')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')

	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='79', comment='ASCII code for O')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='86', comment='ASCII code for V')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='69', comment='ASCII code for E')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='82', comment='ASCII code for R')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='70', comment='ASCII code for F')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='76', comment='ASCII code for L')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='79', comment='ASCII code for O')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='87', comment='ASCII code for W')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')

	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')

	genTLine(label='', operator='JMP', operand_1='end', operand_2='', comment='')


	# -- underflow -----
	genTLine(label='underflow', operator='CMP', operand_1='R3', operand_2='R3', comment='')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='85', comment='ASCII code for U')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='78', comment='ASCII code for N')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='68', comment='ASCII code for D')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='69', comment='ASCII code for E')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='82', comment='ASCII code for R')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='70', comment='ASCII code for F')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='76', comment='ASCII code for L')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='79', comment='ASCII code for O')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='clear R3')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='87', comment='ASCII code for W')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')

	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')

	genTLine(label='', operator='JMP', operand_1='end', operand_2='', comment='')











'''
R7 will be our mediary register - never use R7 outside of this function to preserve saved values 
'''
def genLoadValue(destReg, symid, baseAddress='FP'):
	offset = getLocation(symid)

	if symid == 'this': 
		genTLine(label='', operator='MOV', operand_1='R7', operand_2=baseAddress, comment='')
		genTLine(label='', operator='ADI', operand_1='R7', operand_2=str(offset), comment='R7 now points to "this"')
		genTLine(label='', operator='LDR', operand_1=destReg, operand_2='R7', comment='')
		return


	scope = ST[symid]['scope']
	theType = ST[symid]['data']['theType']
	kind = ST[symid]['kind']


	# if symid represents a global variable
	if scope == 'g': 
		if theType == 'char':
			genTLine(label='', operator='LDB', operand_1=destReg, operand_2=symid, comment='load global into ' + destReg)
		else: 
			genTLine(label='', operator='LDR', operand_1=destReg, operand_2=symid, comment='load global into ' + destReg)

	elif symid[0] == 'R':
		genTLine(label='', operator='MOV', operand_1='R7', operand_2=baseAddress, comment='place base address in R7')
		genTLine(label='', operator='ADI', operand_1='R7', operand_2=str(offset), comment='base address + offset. R7 points at the address of the stack variable (this address holds an address)')
		genTLine(label='', operator='LDR', operand_1='R7', operand_2='R7', comment='place ivar pointer into R7')

		if theType == 'char':
			genTLine(label='', operator='LDB', operand_1=destReg, operand_2='R7', comment='load ivar value into ' + destReg)
		else:
			genTLine(label='', operator='LDR', operand_1=destReg, operand_2='R7', comment='load ivar value into ' + destReg)

	# if symid represents a normal stack variable
	elif offset < 0:
		genTLine(label='', operator='MOV', operand_1='R7', operand_2=baseAddress, comment='')
		genTLine(label='', operator='ADI', operand_1='R7', operand_2=str(offset), comment='')
		genTLine(label='', operator='LDR', operand_1=destReg, operand_2='R7', comment='')

	# If symid represents an ivar, 
	elif kind == 'ivar':
		# load 'this', get offset from passed in variable, then load that value
		genTLine(label='', operator='MOV', operand_1='R7', operand_2=baseAddress, comment='')
		genTLine(label='', operator='ADI', operand_1='R7', operand_2='-8', comment='')
		genTLine(label='', operator='LDR', operand_1='R7', operand_2='R7', comment='load the value of "this" into R7')
		genTLine(label='', operator='ADI', operand_1='R7', operand_2=str(offset), comment='add offset.  R7 now points at the ivar')

		if theType == 'char':
			genTLine(label='', operator='LDB', operand_1=destReg, operand_2='R7', comment='load ivar value into ' + destReg)
		else:
			genTLine(label='', operator='LDR', operand_1=destReg, operand_2='R7', comment='load ivar value into ' + destReg)

	# if we did not recognize how to handle this symid
	else:
		print('genLoadValue ERROR: we have not handled this type yet: ' + theType)
		print('kind: ' + kind)



'''
finds the memory address of symid

generates tcode that
	stores the value in the source register into that memory location.  
'''
def genStoreValue(sourceReg, symid, baseAddress='FP'):
	offset = getLocation(symid)

	if symid == 'this': 
		genTLine(label='', operator='MOV', operand_1='R7', operand_2=baseAddress, comment='')
		genTLine(label='', operator='ADI', operand_1='R7', operand_2=str(offset), comment='R7 now points to "this"')
		genTLine(label='', operator='STR', operand_1=sourceReg, operand_2='R7', comment='')
		return


	scope = ST[symid]['scope']
	theType = ST[symid]['data']['theType']
	kind = ST[symid]['kind']


	# if symid represents a global variable
	if scope == 'g': 
		if theType == 'char':
			genTLine(label='', operator='STB', operand_1=sourceReg, operand_2=symid, comment='store value in ' + sourceReg + ' into global')
		else: 
			genTLine(label='', operator='STR', operand_1=sourceReg, operand_2=symid, comment='store value in ' + sourceReg + ' into global')


	elif symid[0] == 'R':
		genTLine(label='', operator='MOV', operand_1='R7', operand_2=baseAddress, comment='place base address in R7')
		genTLine(label='', operator='ADI', operand_1='R7', operand_2=str(offset), comment='base address + offset. R7 points at the address of the stack variable (this address holds the ivar address)')
		genTLine(label='', operator='LDR', operand_1='R7', operand_2='R7', comment='place ivar address into R7')

		if theType == 'char':
			genTLine(label='', operator='STB', operand_1=sourceReg, operand_2='R7', comment='store value currently in ' + sourceReg + ' into the ivar heap address that is in R7')
		else:
			genTLine(label='', operator='STR', operand_1=sourceReg, operand_2='R7', comment='store value currently in ' + sourceReg + ' into the ivar heap address that is in R7')


	# if symid represents a normal stack variable
	elif offset < 0:
		genTLine(label='', operator='MOV', operand_1='R7', operand_2=baseAddress, comment='')
		genTLine(label='', operator='ADI', operand_1='R7', operand_2=str(offset), comment='')
		genTLine(label='', operator='STR', operand_1=sourceReg, operand_2='R7', comment='')


	# If symid represents an ivar, 
	elif kind == 'ivar':
		# load 'this', get offset from passed in variable, then load that value
		genTLine(label='', operator='MOV', operand_1='R7', operand_2=baseAddress, comment='')
		genTLine(label='', operator='ADI', operand_1='R7', operand_2='-8', comment='')
		genTLine(label='', operator='LDR', operand_1='R7', operand_2='R7', comment='load the value of "this" into R7')
		genTLine(label='', operator='ADI', operand_1='R7', operand_2=str(offset), comment='add offset.  R7 now points at the ivar')

		if theType == 'char':
			genTLine(label='', operator='STB', operand_1=sourceReg, operand_2='R7', comment='load ivar value into ' + sourceReg)
		else:
			genTLine(label='', operator='STR', operand_1=sourceReg, operand_2='R7', comment='load ivar value into ' + sourceReg)

	# if we did not recognize how to handle this symid
	else:
		print('genStoreValue ERROR: we have not handled this type yet: ' + theType)
		print('kind: ' + kind)


# conversion functions ---------------
# genTLine(label='', operator='', operand_1='', operand_2='', comment='')

# DONE
def T_add(line):
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: ADD ***********************************************')

	# load operands
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do the operation
	genTLine(label='', operator='ADD', operand_1='R0', operand_2='R1', comment='')

	# save operands
	genStoreValue('R0', line['operand_3'])

# DONE
def T_sub(line):
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: SUB ***********************************************')

	# load operands
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do the operation
	genTLine(label='', operator='SUB', operand_1='R0', operand_2='R1', comment='')

	# save operands
	genStoreValue('R0', line['operand_3'])

# DONE
def T_mul(line):
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: MUL ***********************************************')

	# load operands
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do the operation
	genTLine(label='', operator='MUL', operand_1='R0', operand_2='R1', comment='')

	# save operands
	genStoreValue('R0', line['operand_3'])

# DONE
def T_div(line):
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: DIV ***********************************************')

	# load operands
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do the operation
	genTLine(label='', operator='DIV', operand_1='R0', operand_2='R1', comment='')

	# save operands
	genStoreValue('R0', line['operand_3'])

# DONE
def T_mov(line):
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: MOV ***********************************************')	

	# operand_1's value => operand_2 

	# load operands
	genLoadValue('R1', line['operand_1'])

	# do the operation
	genTLine(label='', operator='MOV', operand_1='R0', operand_2='R1', comment='')

	# save operands
	genStoreValue('R0', line['operand_2'])


# DONE
def T_lt(line):
	# get the information you need to generate the tcode
	L1 = generateLabel()
	L2 = generateLabel()

	# generate the tcode
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: LT ***********************************************')

	# load
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do operation
	genTLine(label='', operator='CMP', operand_1='R0', operand_2='R1', comment='')
	genTLine(label='', operator='BLT', operand_1='R0', operand_2=L1, comment='')

	genTLine(label='', operator='LDR', operand_1='R0', operand_2='false', comment='set FALSE')
	genStoreValue('R0', line['operand_3'])
	genTLine(label='', operator='JMP', operand_1=L2, operand_2='', comment='')

	genTLine(label=L1, operator='LDR', operand_1='R0', operand_2='true', comment='set TRUE')
	genStoreValue('R0', line['operand_3'])

	genTLine(label=L2, operator='', operand_1='', operand_2='', comment='')

# DONE
def T_gt(line):
	# get the information you need to generate the tcode
	L1 = generateLabel()
	L2 = generateLabel()

	# generate the tcode
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: GT ***********************************************')

	# load
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do operation
	genTLine(label='', operator='CMP', operand_1='R0', operand_2='R1', comment='')
	genTLine(label='', operator='BGT', operand_1='R0', operand_2=L1, comment='')

	genTLine(label='', operator='LDR', operand_1='R0', operand_2='false', comment='set FALSE')
	genStoreValue('R0', line['operand_3'])
	genTLine(label='', operator='JMP', operand_1=L2, operand_2='', comment='')

	genTLine(label=L1, operator='LDR', operand_1='R0', operand_2='true', comment='set TRUE')
	genStoreValue('R0', line['operand_3'])

	genTLine(label=L2, operator='', operand_1='', operand_2='', comment='')

# DONE
def T_eq(line):
	# get the information you need to generate the tcode
	L1 = generateLabel()
	L2 = generateLabel()

	# generate the tcode
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: EQ ***********************************************')

	# load
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do operation
	genTLine(label='', operator='CMP', operand_1='R0', operand_2='R1', comment='')
	genTLine(label='', operator='BRZ', operand_1='R0', operand_2=L1, comment='')

	genTLine(label='', operator='LDR', operand_1='R0', operand_2='false', comment='set FALSE')
	genStoreValue('R0', line['operand_3'])
	genTLine(label='', operator='JMP', operand_1=L2, operand_2='', comment='')

	genTLine(label=L1, operator='LDR', operand_1='R0', operand_2='true', comment='set TRUE')
	genStoreValue('R0', line['operand_3'])

	genTLine(label=L2, operator='', operand_1='', operand_2='', comment='')

# DONE
def T_le(line):
	# get the information you need to generate the tcode
	L1 = generateLabel()
	L2 = generateLabel()

	# generate the tcode
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: LE ***********************************************')

	# load
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do operation
	genTLine(label='', operator='CMP', operand_1='R0', operand_2='R1', comment='')
	genTLine(label='', operator='BRZ', operand_1='R0', operand_2=L1, comment='')
	genTLine(label='', operator='BLT', operand_1='R0', operand_2=L1, comment='')

	genTLine(label='', operator='LDR', operand_1='R0', operand_2='false', comment='set FALSE')
	genStoreValue('R0', line['operand_3'])
	genTLine(label='', operator='JMP', operand_1=L2, operand_2='', comment='')

	genTLine(label=L1, operator='LDR', operand_1='R0', operand_2='true', comment='set TRUE')
	genStoreValue('R0', line['operand_3'])

	genTLine(label=L2, operator='', operand_1='', operand_2='', comment='')

# DONE
def T_ge(line):
	# get the information you need to generate the tcode
	L1 = generateLabel()
	L2 = generateLabel()

	# generate the tcode
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: GE ***********************************************')

	# load
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do operation
	genTLine(label='', operator='CMP', operand_1='R0', operand_2='R1', comment='')
	genTLine(label='', operator='BRZ', operand_1='R0', operand_2=L1, comment='')
	genTLine(label='', operator='BGT', operand_1='R0', operand_2=L1, comment='')

	genTLine(label='', operator='LDR', operand_1='R0', operand_2='false', comment='set FALSE')
	genStoreValue('R0', line['operand_3'])
	genTLine(label='', operator='JMP', operand_1=L2, operand_2='', comment='')

	genTLine(label=L1, operator='LDR', operand_1='R0', operand_2='true', comment='set TRUE')
	genStoreValue('R0', line['operand_3'])

	genTLine(label=L2, operator='', operand_1='', operand_2='', comment='')


# DONE
def T_and(line):
	# get the information you need to generate the tcode
	L1 = generateLabel()
	L2 = generateLabel()
	L3 = generateLabel()

	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: AND ***********************************************')

	# load
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do operation
	genTLine(label='', operator='BRZ', operand_1='R0', operand_2=L3, comment='')
	genTLine(label='', operator='BRZ', operand_1='R1', operand_2=L3, comment='')
	genTLine(label='', operator='JMP', operand_1=L1, operand_2='', comment='')

	genTLine(label=L3, operator='LDR', operand_1='R0', operand_2='false', comment='set FALSE')
	genStoreValue('R0', line['operand_3'])
	genTLine(label='', operator='JMP', operand_1=L2, operand_2='', comment='')

	genTLine(label=L1, operator='LDR', operand_1='R0', operand_2='true', comment='set TRUE')
	genStoreValue('R0', line['operand_3'])

	genTLine(label=L2, operator='', operand_1='', operand_2='', comment='')


# DONE
def T_or(line):
	# get the information you need to generate the tcode
	L1 = generateLabel()
	L2 = generateLabel()
	L3 = generateLabel()

	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: OR ***********************************************')

	# load
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do operation
	genTLine(label='', operator='BNZ', operand_1='R0', operand_2=L1, comment='')
	genTLine(label='', operator='BNZ', operand_1='R1', operand_2=L1, comment='')

	genTLine(label='', operator='LDR', operand_1='R0', operand_2='false', comment='set FALSE')
	genStoreValue('R0', line['operand_3'])
	genTLine(label='', operator='JMP', operand_1=L2, operand_2='', comment='')

	genTLine(label=L1, operator='LDR', operand_1='R0', operand_2='true', comment='set TRUE')
	genStoreValue('R0', line['operand_3'])

	genTLine(label=L2, operator='', operand_1='', operand_2='', comment='')

# DONE
def T_ne(line):
	# get the information you need to generate the tcode
	L1 = generateLabel()
	L2 = generateLabel()

	# generate the tcode
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: NE ***********************************************')

	# load
	genLoadValue('R0', line['operand_1'])
	genLoadValue('R1', line['operand_2'])

	# do operation
	genTLine(label='', operator='CMP', operand_1='R0', operand_2='R1', comment='')
	genTLine(label='', operator='BLT', operand_1='R0', operand_2=L1, comment='')
	genTLine(label='', operator='BGT', operand_1='R0', operand_2=L1, comment='')

	genTLine(label='', operator='LDR', operand_1='R0', operand_2='false', comment='set FALSE')
	genStoreValue('R0', line['operand_3'])
	genTLine(label='', operator='JMP', operand_1=L2, operand_2='', comment='')

	genTLine(label=L1, operator='LDR', operand_1='R0', operand_2='true', comment='set TRUE')
	genStoreValue('R0', line['operand_3'])

	genTLine(label=L2, operator='', operand_1='', operand_2='', comment='')


# DONE
def T_frame(line):

	# Get the information needed to generate the tcode
	func_size = ST[line['operand_1']]['size']
	scopeToSearch = ST[line['operand_1']]['scope'] + '.' + ST[line['operand_1']]['lexeme']
	baseFrame_size = func_size + ST.localTempSize(scopeToSearch)

	# print(str(line))
	# print('scope: ' + scopeToSearch)
	# print('func_size: ' + str(func_size))
	# print('localTempSize: ' + str(ST.localTempSize(scopeToSearch)))
	# print('base frame size: ' + str(baseFrame_size))

	# Generate the tcode
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: FRAME ***********************************************')

	genTLine(label=' ', comment='Compute activation record size')
	genTLine(label='', operator='CMP', operand_1='R1', operand_2='R1', comment='')
	genTLine(label='', operator='ADI', operand_1='R1', operand_2=str(baseFrame_size), comment='summed up space for return, this, pfp, and params')	

	genTLine(comment='')
	genTLine(label=' ', comment='Test for overflow')
	genTLine(label='', operator='MOV', operand_1='R2', operand_2='SP', comment='')
	genTLine(label='', operator='ADD', operand_1='R2', operand_2='R1', comment='R1 will be filled with a negative offset')
	genTLine(label='', operator='CMP', operand_1='R2', operand_2='SL', comment='')
	genTLine(label='', operator='BLT', operand_1='R2', operand_2='overflow', comment='tests if there is space for return, this, pfp, and params')

	genTLine(comment='')
	genTLine(label=' ', comment='Allocate space on the stack for the new frame')
	genTLine(label='', operator='MOV', operand_1='R4', operand_2='FP', comment='save PFP into R4 *****')
	genTLine(label='', operator='MOV', operand_1='FP', operand_2='SP', comment='SP => FP')
	genTLine(label='', operator='ADI', operand_1='SP', operand_2='-12', comment='SP - (return + this + pfp) => SP')

	genTLine(comment='')
	genTLine(label=' ', comment='Figure out address for "this" pointer and place in frame')
	genTLine(label='', operator='MOV', operand_1='R0', operand_2='FP', comment='')
	genTLine(label='', operator='ADI', operand_1='R0', operand_2='-8', comment='compute memory address "this" will be stored')
	genLoadValue('R2', line['operand_2'], 'R4') # get the address of 'this' into R2 (it will be contained in the OLD FRAME, so base address is PFP)
	genTLine(label='', operator='STR', operand_1='R2', operand_2='R0', comment='')

	genTLine(comment='')
	genTLine(label=' ', comment='Place PFP in the frame')
	genTLine(label='', operator='MOV', operand_1='R0', operand_2='FP', comment='')
	genTLine(label='', operator='ADI', operand_1='R0', operand_2='-12', comment='compute memory address PFP will be stored')
	genTLine(label='', operator='STR', operand_1='R4', operand_2='R0', comment='')



def T_push(line):
	# get the info necessary to generate the tCode
	offset = ST[line['operand_1']]['offset']

	# generate the tCode
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: PUSH ***********************************************')

	# get the address of PFP
	genTLine(label='', operator='MOV', operand_1='R0', operand_2='FP', comment='')
	genTLine(label='', operator='ADI', operand_1='R0', operand_2='-12', comment='R0 now points to where we stored the PFP')
	genTLine(label='', operator='LDR', operand_1='R4', operand_2='R0', comment='SAVE the PFP into R4')

	# load the parameter's value into R0
	genLoadValue('R0', line['operand_1'], 'R4')

	# allocate a spot on the current frame 
	genTLine(label='', operator='ADI', operand_1='SP', operand_2='-4', comment='allocate space for the new param')

	# store param's value in new slot that we allocated inside the currrent frame. 
	genTLine(label='', operator='STR', operand_1='R0', operand_2='SP', comment='SAVE the PFP into R4')

	# # print what's in R1
	# genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='')
	# genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
	# genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	# genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='')
	# genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
	# genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')

	# genTLine(label='', operator='MOV', operand_1='R3', operand_2='R1', comment='')
	# genTLine(label='', operator='TRP', operand_1='1', operand_2='', comment='')

	# genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='')
	# genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
	# genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	# genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='')
	# genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
	# genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')


# DONE
def T_call(line):
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: CALL ***********************************************')

	genTLine(label=' ', comment='Figure out the return address and place it in the frame')
	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='60', comment='5 (instruction words) * 12 (word size) = 60 (ret offset)') 

	genTLine(label='', operator='MOV', operand_1='R4', operand_2='PC', comment='')
	genTLine(label='', operator='ADD', operand_1='R3', operand_2='R4', comment='return address => R3')

	genTLine(label='', operator='MOV', operand_1='R4', operand_2='FP', comment='compute the address return address will be stored')
	genTLine(label='', operator='ADI', operand_1='R4', operand_2='-4', comment='')
	genTLine(label='', operator='STR', operand_1='R3', operand_2='R4', comment='store return address in the frame')

	genTLine(comment='')
	genTLine(label=' ', comment='call the function')
	genTLine(label='', operator='JMP', operand_1=line['operand_1'], operand_2='', comment='')



def T_peek(line):
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: PEEK ***********************************************')

	genTLine(label='', operator='MOV', operand_1='R0', operand_2='SP', comment='')
	genTLine(label='', operator='ADI', operand_1='R0', operand_2='-4', comment='')
	genTLine(label='', operator='LDR', operand_1='R0', operand_2='R0', comment='')

	genStoreValue('R0', line['operand_1'])


# DONE
def T_func(line):
	# Get the information you need to generate the tcode
	# get the size of the locals and temps in this function's scope. 
	func_symid = line['operand_1']
	scopeToSearch = ST[func_symid]['scope'] + '.' + ST[func_symid]['lexeme'] 
	lt_size = ST.localTempSize(scopeToSearch)

	# print(str(line))
	# print('scopeToSearch: ' + scopeToSearch)
	# print('localTempSize: ' + str(ST.localTempSize(scopeToSearch)))


	# generate the tCode
	genTLine(comment='')
	genTLine(comment='----------------------------------------------------------------------------')
	genTLine(comment='BEGIN ' + line['label'].upper() + ' FUNCITON') 
	genTLine(comment='----------------------------------------------------------------------------')

	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: FUNC ***********************************************')
	genTLine(label=' ', comment='Test for overflow')
	genTLine(label='', operator='MOV', operand_1='R2', operand_2='SP', comment='')
	genTLine(label='', operator='ADI', operand_1='R2', operand_2='-'+str(lt_size), comment='')
	genTLine(label='', operator='BLT', operand_1='R2', operand_2='overflow', comment='')
	
	genTLine(comment='')
	genTLine(label=' ', comment='Allocate space on the stack for the rest of the frame')
	genTLine(label='', operator='ADI', operand_1='SP', operand_2='-'+str(lt_size), comment='')
	
	genTLine(comment='')
	genTLine(label=' ', comment='Place local variables in the frame')
	genTLine(label=' ', comment='leave these uninitialized - they will get filled/used in the func body')

	genTLine(comment='')
	genTLine(label=' ', comment='Place temporary variables in the frame')
	genTLine(label=' ', comment='leave these uninitialized - they will get filled/used in the func body')	
	
# DONE
def T_rtn(line):
	# Get the information you'll need to generate the code

	# Generate the tcode
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: RTN ***********************************************')

	genTLine(label=' ', comment='deallocate the frame')
	genTLine(label='', operator='MOV', operand_1='SP', operand_2='FP', comment='FP => SP')
	genTLine(label='', operator='MOV', operand_1='R1', operand_2='FP', comment='')
	genTLine(label='', operator='ADI', operand_1='R1', operand_2='-12', comment='R1 now points at PFP')
	genTLine(label='', operator='LDR', operand_1='FP', operand_2='R1', comment='PFP => FP')

	genTLine(comment='')
	genTLine(label=' ', comment='test for underflow')
	genTLine(label='', operator='MOV', operand_1='R1', operand_2='SP', comment='')
	genTLine(label='', operator='CMP', operand_1='R1', operand_2='SB', comment='')
	genTLine(label='', operator='BGT', operand_1='R1', operand_2='underflow', comment='')

	genTLine(comment='')
	genTLine(label=' ', comment='get return address off the stack')
	genTLine(label='', operator='MOV', operand_1='R1', operand_2='SP', comment='')
	genTLine(label='', operator='ADI', operand_1='R1', operand_2='-4', comment='')
	genTLine(label='', operator='LDR', operand_1='R4', operand_2='R1', comment='return address => R4')

	genTLine(comment='')
	genTLine(label=' ', comment='return from the function')
	genTLine(label='', operator='JMR', operand_1='R4', operand_2='', comment='')


	genTLine(comment='^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
	genTLine(comment='END FUNCTION')
	genTLine(comment='^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
	


def T_return(line):
	# Get the information you'll need to generate the code
	# frame size of the current function 

	# Generate the tcode
	genTLine(comment='')
	genTLine(label=line['label'], comment='** icode: RETURN ***********************************************')

	genTLine(label=' ', comment='deallocate the frame')
	genTLine(label='', operator='MOV', operand_1='SP', operand_2='FP', comment='FP => SP')
	genTLine(label='', operator='MOV', operand_1='R1', operand_2='FP', comment='')
	genTLine(label='', operator='ADI', operand_1='R1', operand_2='-12', comment='R1 now points at PFP')
	genTLine(label='', operator='LDR', operand_1='FP', operand_2='R1', comment='PFP => FP')

	genTLine(comment='')
	genTLine(label=' ', comment='test for underflow')
	genTLine(label='', operator='MOV', operand_1='R1', operand_2='SP', comment='')
	genTLine(label='', operator='CMP', operand_1='R1', operand_2='SB', comment='')
	genTLine(label='', operator='BGT', operand_1='R1', operand_2='underflow', comment='')

	genTLine(comment='')
	genTLine(label=' ', comment='get return address off the stack')
	genTLine(label='', operator='MOV', operand_1='R1', operand_2='SP', comment='')
	genTLine(label='', operator='ADI', operand_1='R1', operand_2='-4', comment='')
	genTLine(label='', operator='LDR', operand_1='R4', operand_2='R1', comment='return address => R4')

	genTLine(comment='')
	genTLine(label=' ', comment='Place return value just above the top of stack')
	genTLine(label='', operator='MOV', operand_1='R1', operand_2='SP', comment='')
	genTLine(label='', operator='ADI', operand_1='R1', operand_2='-4', comment='return value memory spot => R1')
	genLoadValue('R0', line['operand_1'], 'SP')
	genTLine(label='', operator='STR', operand_1='R0', operand_2='R1', comment='store return value just above the SP')

	genTLine(comment='')
	genTLine(label=' ', comment='return from the function')
	genTLine(label='', operator='JMR', operand_1='R4', operand_2='', comment='return address should have been saved into R4')


def T_ref(line):
	# get the offset of B
	b_offset = getLocation(line['operand_2'])
	c_offset = getLocation(line['operand_3'])

	genTLine(label=' ', comment='')
	genTLine(label=line['label'], comment='** icode: REF ***********************************************')

	# load the address contained in operand 1 (base address of the object on the heap)
	genLoadValue('R0', line['operand_1'])

	# add the offset of operand_2 (the offset of the ivar)
	genTLine(label='', operator='ADI', operand_1='R0', operand_2=str(b_offset), comment='')

	# store the address that is now contained in R0 into the memory address of operand_3
	genTLine(label='', operator='MOV', operand_1='R1', operand_2='FP', comment='store the address of the ivar into operand_3')
	genTLine(label='', operator='ADI', operand_1='R1', operand_2=str(c_offset), comment='')
	genTLine(label='', operator='STR', operand_1='R0', operand_2='R1', comment='')	




def T_aef(line):
	# get the offset of B
	b_offset = getLocation(line['operand_2'])
	c_offset = getLocation(line['operand_3'])
	arr_type = ST[line['operand_1']]['data']['theType'][1:] # get the size of the datatype. 

	# figure out the element's size
	if arr_type == 'bool': 
		el_size = 1
	else:
		el_size = 4

	genTLine(label=' ', comment='')
	genTLine(label=line['label'], comment='** icode: AEF ***********************************************')

	# load the address contained in operand 1 (base address of the object on the heap)
	genLoadValue('R0', line['operand_1'])

	# the index that we use to index into this array
	genLoadValue('R1', line['operand_2'])

	# get the size of the array type into R2
	genTLine(label='', operator='CMP', operand_1='R2', operand_2='R2', comment='')
	genTLine(label='', operator='ADI', operand_1='R2', operand_2=str(el_size), comment='')

	# multiply R1 and R2 to get the total offset 
	genTLine(label='', operator='MUL', operand_1='R1', operand_2='R2', comment='')

	# add the offset to the base address (the offset of the indexed value of the array)
	genTLine(label='', operator='ADD', operand_1='R0', operand_2='R1', comment='')

	# store the address that is now contained in R0 into the memory address of operand_3
	genTLine(label='', operator='MOV', operand_1='R1', operand_2='FP', comment='store the address of the ivar into operand_3')
	genTLine(label='', operator='ADI', operand_1='R1', operand_2=str(c_offset), comment='')
	genTLine(label='', operator='STR', operand_1='R0', operand_2='R1', comment='')	


# DONE
def T_bf(line):
	# get in information you'll need to generate the tcode
	# none

	# generate the tCode
	genTLine(label=' ', comment='')
	genTLine(label=line['label'], comment='** icode: BF ***********************************************')

	# Load
	genLoadValue(destReg='R1', symid=line['operand_1'])
	
	# operation
	genTLine(label='', operator='BRZ', operand_1='R1', operand_2=line['operand_2'], comment='')

	# save
	# nothing to save


# DONE
def T_jmp(line):
	genTLine(label=' ', comment='')
	genTLine(label=line['label'], comment='** icode: JMP ***********************************************')
	genTLine(label='', operator='JMP', operand_1=line['operand_1'], operand_2='', comment='')

	
# DONE
def T_write(line):
	# get the information you'll need to generate the tcode
	theType = ST[line['operand_1']]['data']['theType']
	scope = ST[line['operand_1']]['scope']
	offset = getLocation(line['operand_1'])

	# generate the tCode
	genTLine(label=' ', comment='')
	genTLine(label=line['label'], comment='** icode: WRITE ***********************************************')

	genLoadValue(destReg='R3', symid=line['operand_1'])

	if theType == 'int': 
		genTLine(label='', operator='TRP', operand_1='1', operand_2='', comment='')
	elif theType == 'char':
		genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')
	else: 
		print('WRITE error - did not recognize the type for printing')

def T_read(line):
	# get the information you'll need to generate the tcode
	theType = ST[line['operand_1']]['data']['theType']
	scope = ST[line['operand_1']]['scope']
	offset = getLocation(line['operand_1'])

	# generate the tCode
	genTLine(label=' ', comment='')
	genTLine(label=line['label'], comment='** icode: WRITE ***********************************************')

	if theType == 'int': 
		genTLine(label='', operator='TRP', operand_1='2', operand_2='', comment='')
	elif theType == 'char':
		genTLine(label='', operator='TRP', operand_1='4', operand_2='', comment='')
	else: 
		print('WRITE error - did not recognize the type for printing')

	genStoreValue(sourceReg='R3', symid=line['operand_1'])


def T_new(line):
	# get the info needed to generate tcode
	offset = ST[line['operand_2']]['offset']
	# the size of the class


	# genereate tcode
	genTLine(label=' ', comment='')
	genTLine(label=line['label'], comment='** icode: NEW ***********************************************')


	# get the address that points to the begining of the allocated object. 
	genTLine(label='', operator='MOV', operand_1='R0', operand_2='SL', comment='save the top of the to-be allocated object => R0')

	# save that address into the given temp variable. 
	genStoreValue('R0', line['operand_2'])

	# op1 is a variable that contains the total size of the array. 
	genLoadValue('R1', line['operand_1'])

	# allocate the space for the given object. 
	genTLine(label='', operator='ADD', operand_1='SL', operand_2='R1', comment='allocate space for the new object')




#  sizeToAllocate, symid
'''
This will save the free heap pointer (SL), save that value into the temp variable, 
then allocate space for the given object.  
'''
def T_newi(line):
	# get the info needed to generate tcode
	offset = ST[line['operand_2']]['offset']

	# genereate tcode
	genTLine(label=' ', comment='')
	genTLine(label=line['label'], comment='** icode: NEWI ***********************************************')

	# get the address that points to the begining of the allocated object. 
	genTLine(label='', operator='MOV', operand_1='R0', operand_2='SL', comment='save the top of the to-be allocated object => R0')
	
	# save that address into the given temp variable. 
	genStoreValue('R0', line['operand_2'])

	# allocate the space for the given object. 
	genTLine(label='', operator='ADI', operand_1='SL', operand_2=str(line['operand_1']), comment='allocate space for the new object')


# DONE
def T_stop(line):
	genTLine(label=' ', comment='')
	genTLine(label=line['label'], comment='** icode: STOP ***********************************************')	
	genTLine(label='end', operator='TRP', operand_1='0')



def printCurrentFrame(howmuch):
	genTLine(label='', operator='MOV', operand_1='R3', operand_2='FP', comment='')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='-4', comment='')
	genTLine(label='', operator='LDR', operand_1='R3', operand_2='R3', comment='')
	genTLine(label='', operator='TRP', operand_1='1', operand_2='', comment='')

	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')

	genTLine(label='', operator='MOV', operand_1='R3', operand_2='FP', comment='')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='-8', comment='')
	genTLine(label='', operator='LDR', operand_1='R3', operand_2='R3', comment='')
	genTLine(label='', operator='TRP', operand_1='1', operand_2='', comment='')

	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')

	genTLine(label='', operator='MOV', operand_1='R3', operand_2='FP', comment='')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='-12', comment='')
	genTLine(label='', operator='LDR', operand_1='R3', operand_2='R3', comment='')
	genTLine(label='', operator='TRP', operand_1='1', operand_2='', comment='')

	genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='')
	genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
	genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')

	for slot in range(howmuch):
		offset = (-12) - (slot * 4)
		genTLine(label='', operator='MOV', operand_1='R3', operand_2='FP', comment='')
		genTLine(label='', operator='ADI', operand_1='R3', operand_2=str(offset), comment='')
		genTLine(label='', operator='LDR', operand_1='R3', operand_2='R3', comment='')
		genTLine(label='', operator='TRP', operand_1='1', operand_2='', comment='')

		genTLine(label='', operator='CMP', operand_1='R3', operand_2='R3', comment='')
		genTLine(label='', operator='ADI', operand_1='R3', operand_2='10', comment='')
		genTLine(label='', operator='TRP', operand_1='3', operand_2='', comment='')

#  genTLine(label='', operator='', operand_1='', operand_2='', comment='')
# ***************************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



#*******************************************************************
# COMPILER DRIVER
#*******************************************************************
# validate command line args
if(len(sys.argv) != 2):						# appropriate arg count
	print('invalid command line args')
	sys.exit(0)
if(not sys.argv[1].endswith('.kxi')):		# input file is .kxi extension
	print('given file must be kxi')
	sys.exit(0)

# make sure we can open the file. Give error if opening failed.  
try:
	f = open(sys.argv[1], "r");
	f.close()
except IOError: 
	print('Failed to open file. Check your file name and path')
	sys.exit(0) 


# Debug Globals
TRACKER_ON = False
TRACK_SCOPE = False


# Compiler Globals
ST = SymbolTable()
SAS = SemanticActionStack() # Semantic Action Stack - will be filled with SAR objects
OS = OperatorStack() # Operator Stack - will be filled with Tokens :D
QT = QuadTable()
CM = CommentMap()
generateLabel = labelFactory()


# SYNTAX CHECK $$$$$$$$$$$$$$$$$$$$$
PASS_NUMBER = 1
PASS_SUCCESS = True
generateSymid = symidFactory()
lex = Lexer(sys.argv[1])

compilation_unit()
if not PASS_SUCCESS:
	sys.exit(1)
# ST.print()


# SEMANTICS CHECK $$$$$$$$$$$$$$$$$$
PASS_NUMBER = 2
lex = Lexer(sys.argv[1]) # restart lexer
compilation_unit()
# ST.print()


# ICODE $$$$$$$$$$$$$$$$$$$$$$$$$$$$ 
# CM.print()
# QT.print()
QT.toFile()


# TCODE $$$$$$$$$$$$$$$$$$$$$$$$$$$$
tcodeFilename = 'tcode.asm'
tcodeWriter = ''
generateTCode()	
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



#*******************************************************************
# VIRTUAL MACHINE CODE
#*******************************************************************
count = 0

MEM_INST = 60000
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
	# print('A - lineNumber: ' + str(assemblyLine))
	global mem
	if not inBounds(pos):
		kill('out of bounds')
	if pos < globalVarsStart:
		kill('Cannot change a constant variable')
	mem[pos] = asciiCode

# Pull out an int from the byte array
def getIntAt(pos):
	# print('B - lineNumber: ' + str(assemblyLine))

	if not inBounds(pos) or not inBounds(pos + 3):
		kill('out of bounds')
	myIntInBytes = mem[pos:pos+4]
	return int.from_bytes(myIntInBytes, byteorder='little', signed=True)

# Place an int into the byte array
def setIntAt(pos, num):
	# print('C - lineNumber: ' + str(assemblyLine))

	global mem
	if not inBounds(pos) or not inBounds(pos + 3):
		kill('out of bounds')
	if pos < globalVarsStart:
		kill('Cannot change a constant variable')
	numBytes = num.to_bytes(4, byteorder='little', signed=True)
	mem[pos:pos + 4] = numBytes

# pull out a char from the byte array
def getCharAt(pos):
	# print('D - lineNumber: ' + str(assemblyLine))

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
	# reg[SL] = MEM_SIZE - MEM_STACK
	reg[SL] = MEM_INST # == MEM_SIZE - MEM_STACK
	reg[SP] = MEM_SIZE
	reg[FP] = 0	# null
	reg[SB] = MEM_SIZE
	globalVarsStart = 0
	assemblyLine = 0
	multiLineComment = False

	# open the file
	try:
		# f = open(sys.argv[1], "r")
		f = open('tcode.asm', "r")
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
		if '.BYT' in x or '.INT' in x:
			tokens = re.split("[\s]", x)		# leave commas in
		else: 
			tokens = re.split("[\s,]", x)	# take commas out

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


		# Handle when we want to set a character with the value of 32, but with the actual character, like ' '
		if len(tokens) == 3 and tokens[0] == '.BYT':
			tokens = [tokens[0], ' '] 

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
		kill('INVALID DIRECTIVE - ' + str(assemblyLine) + ' A')

	# Make sure given data is actually a character
	character = tokens[1]
	x = re.search("^('[\w\W]')$", character)	# matches quoted characters (letter, and special)
	y = re.search("^([\d]+)$", character)		# matches number
	z = re.search("^('\\\\\w')$", character)	# matches special characters (\n, \t, etc. )
	w = re.search(" ", character)				# matches single space
	if x: 
		character = ord(character[1]) # strip the quotations and convert to ascii code equivalent
	elif y: 
		character = int(character) # convert to integer ('10' -> 10)
	elif z: 
		# match any special character and change it to it's letter equivalent. 
		character = ord(character[1:len(character)-1].encode().decode('unicode_escape'))
	elif w:
		character = ord(' ')
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
		
		# comment out not being able to directly modify SL register, so we can addd to the heap wiht it.  
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
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



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

			# print(values['method'])

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
# ******************************************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^





