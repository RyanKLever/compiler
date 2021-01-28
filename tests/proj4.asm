; GLOBALS
fibArr			.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0
				.INT 0

threadMutex		.INT 0

CNT 			.INT 0
currentIndex	.INT 0



; *********************************************************************************************
; PROGRAM START 
; *********************************************************************************************
				; -- MAIN FUNCTION CALL ------------------------------------------------------- 
				; main function activation record size: 2 = (ret add, PFP [no params])
START			CMP R0, R0				
				ADI R0, 2				; number of stack words needed for frame
				CMP R1, R1
				ADI R1, 4				; size of stack word
				MUL R0, R1				; ************** FrameSize => R0

				; Test for Overflow
				MOV R1, SP
				SUB R1, R0				; SP - frameSize => R2
				CMP R1, SL
				BLT R1, overflow 		; if SP < SL, OVERFLOW
				
				; Allocate space on stack for new frame
				MOV R1, FP				; ************** PFP = FP => R1
				MOV FP, SP 				; FP = SP
				SUB SP, R0				; SP = SP - frameSize

				; Figure out return address and put that on the stack
				CMP R2, R2
				ADI R2, 12				; Size of instruction word = > R5
				CMP R3, R3				
				ADI R3, 18				; # inst btw PC mov and inst to ex upon return
				MUL R2, R3				; R2 now holds the PC offset 

				MOV R3, PC
				ADD R2, R3				; return address => R2 **************************

				MOV R3, FP				; FP => R1
				CMP R4, R4
				ADI R4, 4				; Size of stack word => R4
				CMP R5, R5				
				ADI R5, 1				; Activation record slot we want to store in (not 0 based)
				MUL R4, R5				; FP offset => R4
				SUB R3, R4				; R3 now points to where we store return address on stack
				STR R2, R3				; place return address on stack

				; Put PFP on stack
				MOV R3, FP				; FP => R4    DERP
				CMP R4, R4
				ADI R4, 4				; Size of stack word => R4
				CMP R5, R5				
				ADI R5, 2				; Activation record slot we want to store in (not 0 based)
				MUL R4, R5				; FP offset => R4
				SUB R3, R4				; R5 now points to where we store the PFP on stack
				STR R1, R3				; place PFP on stack

				; No parameters are given with this main function

				; Call the function
				JMP MAIN
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

				; TESTING
				; end of program.  Print 'ABC' to signify end (For debugging only)
				; CMP R3, R3
				; ADI R3, 10
				; TRP 3
				; CMP R3, R3
				; ADI R3, 97
				; TRP 3
				; CMP R3, R3
				; ADI R3, 98
				; TRP 3
				; CMP R3, R3
				; ADI R3, 99
				; TRP 3

end				TRP 0
; =============================================================================================
; END PROGRAM START 
; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


; *********************************************************************************************
; MAIN FUNCTION
; *********************************************************************************************
MAIN 			; -- INSIDE MAIN FUNCTION PREP ------------------------------------------------
				; Compute space needed for the rest of activation record (local, temp)
				; 2 local, 0 temp = 1
				CMP R0, R0				
				ADI R0, 1				; number of stack words needed for frame
				CMP R1, R1
				ADI R1, 4				; size of stack word
				MUL R0, R1				; ************** FrameSize => R0

				; Test for Overflow
				MOV R1, SP
				SUB R1, R0				; SP - frameSize => R2
				CMP R1, SL
				BLT R1, overflow 		; if SP < SL, OVERFLOW
				
				; Allocate space on stack for the rest of the frame (FP and PFP stays same)
				SUB SP, R0				; SP = SP - frameSize

				; place local vars on stack
				; get inital value(0) of 'input' into R1
				CMP R1, R1
				ADI R1, 0				
				; Put local var on stack
				MOV R2, FP				; FP => R2
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R3
				CMP R4, R4				
				ADI R4, 3 				; Activation record slot we want to store in (not 0 based)
				MUL R3, R4				; R3 holds offset
				SUB R2, R3				; R2 now points to where we store the param on stack
				STR R1, R2

				; place temporary vars on stack
				; NONE
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


				; -- MAIN FUNCTION BODY -------------------------------------------------------
; PART 1 and 2 start &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
mainWhile		TRP 2					; get input from user => R3
				CMP R0, R0
				ADI R0, 0				; place a zero in R0
				CMP R0, R3				; Is user input 0? 
				BRZ R0, endMainWhile	; if yes, end the loop.  otherwhise, loop again.  


				; save value into main temporary variable.  
				MOV R0, FP				; FP => R2
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R3
				CMP R2, R2				
				ADI R2, 3 				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; R3 holds offset
				SUB R0, R1				; R2 now points to where we store the param on stack
				STR R3, R0

				; -- FIB FUNCTION CALL ----------------------------------------------------
				; Activation Record Size (return, PFP, 1 param) = 3
				CMP R7, R7				
				ADI R7, 3				; number of stack words needed for frame
				CMP R6, R6
				ADI R6, 4				; size of stack word
				MUL R7, R6				; ************** FrameSize => R7

				; Test for Overflow
				MOV R6, SP
				SUB R6, R7				; SP - frameSize => R6
				CMP R6, SL
				BLT R6, overflow 		; if SP < SL, OVERFLOW

				
				; Allocate space on stack for new frame
				MOV R6, FP				; ************** PFP = FP => R6
				MOV FP, SP 				; FP = SP
				SUB SP, R7				; SP = SP - frameSize

				; Figure out return address and put that on the stack
				CMP R3, R3
				ADI R3, 12				; Size of instruction word = > R3
				CMP R2, R2				
				ADI R2, 28				; # inst btw PC mov and inst to ex upon return***** FIX **
				MUL R3, R2				; R3 now holds the PC offset

				MOV R5, PC
				ADD R5, R3				; return address => R5 

				MOV R4, FP				; FP => R1
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 1				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; FP offset => R4
				SUB R4, R3				; R4 now points to where we store return address on stack
				STR R5, R4				; place return address on stack

				; Put PFP on stack
				MOV R4, FP				; FP => R4   
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 2				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R5 now points to where we store the PFP on stack
				STR R6, R4				; place PFP on stack

				; One parameter must be given
				; Get value of first parameter into R6 (get value of the main function's local variable)
				MOV R4, FP 				; ERROR - if we add another local variable, this 
										; will reference the wrong value
				LDR R6, R4				; FP should be pointing at main's local variable right now.

				; Put 1st param on stack
				MOV R4, FP				; FP => R4     
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 3				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R4 now points to where we store the PFP on stack
				STR R6, R4

				; Call the function
				JMP FIB
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

				; TESTING - print return value from original fib function call
				CMP R3, R3
				ADI R3, 70				; F
				TRP 3
				CMP R3, R3
				ADI R3, 105				; i
				TRP 3
				CMP R3, R3
				ADI R3, 98				; b
				TRP 3
				CMP R3, R3
				ADI R3, 111				; o
				TRP 3
				CMP R3, R3
				ADI R3, 110				; n
				TRP 3
				CMP R3, R3
				ADI R3, 97				; a
				TRP 3
				CMP R3, R3
				ADI R3, 99				; c
				TRP 3
				CMP R3, R3
				ADI R3, 99				; c
				TRP 3
				CMP R3, R3
				ADI R3, 105				; i
				TRP 3
				CMP R3, R3
				ADI R3, 32				; space
				TRP 3
				CMP R3, R3
				ADI R3, 111				; o
				TRP 3
				CMP R3, R3
				ADI R3, 102				; f
				TRP 3
				CMP R3, R3
				ADI R3, 32				; space
				TRP 3

				MOV R0, FP				; FP => R2
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R3
				CMP R2, R2				
				ADI R2, 3 				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; R3 holds offset
				SUB R0, R1				; R2 now points to where we store the param on stack
				LDR R3, R0				; value entered by the user.  
				TRP 1

				CMP R3, R3
				ADI R3, 32				; space
				TRP 3
				CMP R3, R3
				ADI R3, 105				; i
				TRP 3
				CMP R3, R3
				ADI R3, 115				; s
				TRP 3
				CMP R3, R3
				ADI R3, 32				; space
				TRP 3

				MOV R0, SP				
				CMP R1, R1
				ADI R1, 4				; Size of stack word 
				CMP R2, R2				
				ADI R2, 1				; Number of stack words we need to traverse
				MUL R1, R2				; offset
				SUB R0, R1				
				LDR R3, R0				; value returned by the fib function call  
				TRP 1

				CMP R3, R3
				ADI R3, 10				; newline
				TRP 3
				; ^^^^^^^^^^^^^^^^^^^^^

				; Get value entered by user
				MOV R0, FP				; FP => R2
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R3
				CMP R2, R2				
				ADI R2, 3 				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; R3 holds offset
				SUB R0, R1				; R2 now points to where we store the param on stack
				LDR R0, R0				; value entered by the user.  

				; get fibArr address
				LDA R1, fibArr			; get address of fibArr
				LDR R2, CNT 			; get current value of CNT
				CMP R3, R3
				ADI R3, 4				; size of individual 
				MUL R2, R3				; fibArr offset
				ADD R1, R2				; now points at the index in fibArr we want to store 

				; store the x value
				STR R0, R1 				; store the x value

				; increment CNT
				LDA R0, CNT
				LDR R1, R0
				ADI R1, 1
				STR R1, R0

				; get the fib number result 
				MOV R0, SP				
				CMP R1, R1
				ADI R1, 4				; Size of stack word 
				CMP R2, R2				
				ADI R2, 1				; Number of stack words we need to traverse
				MUL R1, R2				; offset
				SUB R0, R1				
				LDR R0, R0				; value returned by the fib function call  

				; get fibArr address for the next index
				LDA R1, fibArr			; get address of fibArr
				LDR R2, CNT 			; get current value of CNT
				CMP R3, R3
				ADI R3, 4				; size of individual 
				MUL R2, R3				; fibArr offset
				ADD R1, R2				; now points at the index in fibArr we want to store 

				; store the y value
				STR R0, R1 				; store the y value

				; increment CNT
				LDA R0, CNT
				LDR R1, R0
				ADI R1, 1
				STR R1, R0

				JMP mainWhile
endMainWhile


				; Reset currentIndex to 0
				CMP R0, R0
				STR R0, currentIndex

printWhile 		LDR R0, currentIndex	; get currentIndex current value
				LDR R1, CNT
				CMP R2, R2
				ADI R2, 2
				DIV R1, R2				; Divide CNT by 2 (it will always be even)
				ADI R1, -1				; account for currentIndex's zero base
				CMP R0, R1
				BLT	R0, printWhileBody	; if currentIndex is less than 30, printWhileBody
				BRZ	R0, printWhileBody	; if currentIndex is equal to 30, printWhileBody
				BGT	R0, endPrintWhile	; if currentIndex is greater than 30, end the loop

printWhileBody	LDA R0, fibArr
				LDR R1, currentIndex
				CMP R2, R2
				ADI R2, 4				; size of one element in fibArr
				MUL R1, R2				; fibArr offset
				ADD R0, R1 				; points to where we want to read from
				LDR R3, R0
				TRP 1

				CMP R3, R3
				ADI R3, 44				; COMMA
				TRP 3
				CMP R3, R3
				ADI R3, 32				; SPACE
				TRP 3

				LDA R0, fibArr
				LDR R1, CNT 
				ADI R1, -1
				LDR R2, currentIndex
				SUB R1, R2
				CMP R2, R2
				ADI R2, 4				; size of one element in fibArr
				MUL R1, R2				; fibArr offset
				ADD R0, R1 				; points to where we want to read from
				LDR R3, R0
				TRP 1


commaIf 		LDR R0, currentIndex	; get currentIndex current value
				LDR R1, CNT
				CMP R2, R2
				ADI R2, 2
				DIV R1, R2				; Divide CNT by 2 (it will always be even)
				ADI R1, -2				; account for currentIndex's zero base 
				CMP R0, R1
				BLT	R0, commaIfFirst	; if currentIndex is less than 30, printWhileBody
				BRZ	R0, commaIfFirst	; if currentIndex is equal to 30, printWhileBody
				BGT	R0, commaIfEnd		; if currentIndex is greater than 30, end the loop

commaIfFirst	CMP R3, R3
				ADI R3, 44				; COMMA
				TRP 3
				CMP R3, R3
				ADI R3, 32				; SPACE
				TRP 3
commaIfEnd
				
				; increment currentIndex
				LDA R0, currentIndex
				LDR R1, R0
				ADI R1, 1
				STR R1, R0

				JMP printWhile
endPrintWhile	
				
				; print a newline for nice looks 
				CMP R3, R3
				ADI R3, 10
				TRP 3
; PART 1 AND 2 END %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



; PART 3 Start &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
				LCK CNT					; lock CNT	
	
				CMP R0, R0				; Reset CNT
				STR R0, CNT

				LCK threadMutex			; LOCK THREAD MUTEX

secondWhile		TRP 2					; get input from user => R3
				CMP R0, R0
				ADI R0, 0				; place a zero in R0
				CMP R0, R3				; Is user input 0? 
				BRZ R0, endSecondWhile	; if yes, end the loop.  otherwhise, loop again.  


				RUN R0, NewThread		; RUN NEW THREAD


				JMP secondWhile
endSecondWhile
				
				ULK threadMutex			; UNLOCK THREAD MUTEX
				BLK						; BLOCK MAIN THREAD
				
	
				LCK currentIndex
										; PRINT ARRAY
				; Reset currentIndex to 0
				CMP R0, R0
				STR R0, currentIndex

pWhile 	 		LDR R0, currentIndex	; get currentIndex current value
				LDR R1, CNT
				CMP R2, R2
				ADI R2, 2
				DIV R1, R2				; Divide CNT by 2 (it will always be even)
				ADI R1, -1				; account for currentIndex's zero base
				CMP R0, R1
				BLT	R0, pWhileBody	; if currentIndex is less than 30, pWhileBody
				BRZ	R0, pWhileBody	; if currentIndex is equal to 30, pWhileBody
				BGT	R0, endpWhile	; if currentIndex is greater than 30, end the loop

pWhileBody		LDA R0, fibArr
				LDR R1, currentIndex
				CMP R2, R2
				ADI R2, 4				; size of one element in fibArr
				MUL R1, R2				; fibArr offset
				ADD R0, R1 				; points to where we want to read from
				LDR R3, R0
				TRP 1

				CMP R3, R3
				ADI R3, 44				; COMMA
				TRP 3
				CMP R3, R3
				ADI R3, 32				; SPACE
				TRP 3

				LDA R0, fibArr
				LDR R1, CNT 
				ADI R1, -1
				LDR R2, currentIndex
				SUB R1, R2
				CMP R2, R2
				ADI R2, 4				; size of one element in fibArr
				MUL R1, R2				; fibArr offset
				ADD R0, R1 				; points to where we want to read from
				LDR R3, R0
				TRP 1


cIf 			LDR R0, currentIndex	; get currentIndex current value
				LDR R1, CNT
				CMP R2, R2
				ADI R2, 2
				DIV R1, R2				; Divide CNT by 2 (it will always be even)
				ADI R1, -2				; account for currentIndex's zero base 
				CMP R0, R1
				BLT	R0, cIfFirst	; if currentIndex is less than 30, pWhileBody
				BRZ	R0, cIfFirst	; if currentIndex is equal to 30, pWhileBody
				BGT	R0, cIfEnd		; if currentIndex is greater than 30, end the loop

cIfFirst		CMP R3, R3
				ADI R3, 44				; COMMA
				TRP 3
				CMP R3, R3
				ADI R3, 32				; SPACE
				TRP 3
cIfEnd


				; increment currentIndex
				LDA R0, currentIndex
				LDR R1, R0
				ADI R1, 1
				STR R1, R0

				JMP pWhile
endpWhile

				ULK CNT
				ULK currentIndex


				JMP MAINRETURN			; STOP PROGRAM



NewThread		LCK threadMutex			; LOCK THREAD MUTEX
				ULK threadMutex			; UNLOCK THREAD MUTEX

				; save value entered by User (in R3 right now) into main temporary variable.  
				MOV R0, SB				; SP => R2
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R3
				CMP R2, R2				
				ADI R2, 3 				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; R3 holds offset
				SUB R0, R1				; R2 now points to where we store the param on stack
				STR R3, R0


										; CALL Y - fib(X)
				; -- FIB FUNCTION CALL ----------------------------------------------------
				; Activation Record Size (return, PFP, 1 param) = 3
				CMP R7, R7				
				ADI R7, 3				; number of stack words needed for frame
				CMP R6, R6
				ADI R6, 4				; size of stack word
				MUL R7, R6				; ************** FrameSize => R7

				; Test for Overflow
				MOV R6, SP
				SUB R6, R7				; SP - frameSize => R6
				CMP R6, SL
				BLT R6, overflow 		; if SP < SL, OVERFLOW

				
				; Allocate space on stack for new frame
				MOV R6, FP				; ************** PFP = FP => R6
				MOV FP, SP 				; FP = SP
				SUB SP, R7				; SP = SP - frameSize

				; Figure out return address and put that on the stack
				CMP R3, R3
				ADI R3, 12				; Size of instruction word = > R3
				CMP R2, R2				
				ADI R2, 34				; # inst btw PC mov and inst to ex upon return***** FIX **
				MUL R3, R2				; R3 now holds the PC offset

				MOV R5, PC
				ADD R5, R3				; return address => R5 

				MOV R4, FP				; FP => R1
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 1				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; FP offset => R4
				SUB R4, R3				; R4 now points to where we store return address on stack
				STR R5, R4				; place return address on stack

				; Put PFP on stack
				MOV R4, FP				; FP => R4   
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 2				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R5 now points to where we store the PFP on stack
				STR R6, R4				; place PFP on stack

				; One parameter must be given
				; get n off the stack and put it in R6
				MOV R0, FP				; FP => R0
				CMP R1, R1
				ADI R1, 4				; Size of stack word 
				CMP R2, R2				
				ADI R2, 3 				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; offset
				SUB R0, R1				; R0 Holds address of n *************************
				LDR R6, R0				; Get current value of n

				; Put 1st param on stack
				MOV R4, FP				; FP => R4     
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 3				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R4 now points to where we store the PFP on stack
				STR R6, R4

				; Call the function
				JMP FIB
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

										; PRINT FIBONACCI OF X IS Y // THIS WILL CREATE MISHMOOSH
				; print return value from original fib function call
				CMP R3, R3
				ADI R3, 70				; F
				TRP 3
				CMP R3, R3
				ADI R3, 105				; i
				TRP 3
				CMP R3, R3
				ADI R3, 98				; b
				TRP 3
				CMP R3, R3
				ADI R3, 111				; o
				TRP 3
				CMP R3, R3
				ADI R3, 110				; n
				TRP 3
				CMP R3, R3
				ADI R3, 97				; a
				TRP 3
				CMP R3, R3
				ADI R3, 99				; c
				TRP 3
				CMP R3, R3
				ADI R3, 99				; c
				TRP 3
				CMP R3, R3
				ADI R3, 105				; i
				TRP 3
				CMP R3, R3
				ADI R3, 32				; space
				TRP 3
				CMP R3, R3
				ADI R3, 111				; o
				TRP 3
				CMP R3, R3
				ADI R3, 102				; f
				TRP 3
				CMP R3, R3
				ADI R3, 32				; space
				TRP 3

				MOV R0, SP				; FP => R2
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R3
				CMP R2, R2				
				ADI R2, 3 				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; R3 holds offset
				SUB R0, R1				; R2 now points to where we store the param on stack
				LDR R3, R0				; value entered by the user.  
				TRP 1

				CMP R3, R3
				ADI R3, 32				; space
				TRP 3
				CMP R3, R3
				ADI R3, 105				; i
				TRP 3
				CMP R3, R3
				ADI R3, 115				; s
				TRP 3
				CMP R3, R3
				ADI R3, 32				; space
				TRP 3

				MOV R0, SP				
				CMP R1, R1
				ADI R1, 4				; Size of stack word 
				CMP R2, R2				
				ADI R2, 1				; Number of stack words we need to traverse
				MUL R1, R2				; offset
				SUB R0, R1				
				LDR R3, R0				; value returned by the fib function call  
				TRP 1

				CMP R3, R3
				ADI R3, 10				; newline
				TRP 3
				; ^^^^^^^^^^^^^^^^^^^^^


				LCK CNT 
				
				LCK fibArr				; LOCK ARRAY MUTEX


										; LOAD ARRAY WITH X AND Y VALUES
				; Get value entered by user
				MOV R0, SP				; FP => R2
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R3
				CMP R2, R2				
				ADI R2, 3 				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; R3 holds offset
				SUB R0, R1				; R2 now points to where we store the param on stack
				LDR R0, R0				; value entered by the user.  

				; get fibArr address
				LDA R1, fibArr			; get address of fibArr
				LDR R2, CNT 			; get current value of CNT
				CMP R3, R3
				ADI R3, 4				; size of individual 
				MUL R2, R3				; fibArr offset
				ADD R1, R2				; now points at the index in fibArr we want to store 

				; store the x value
				STR R0, R1 				; store the x value

				; increment CNT
				LDA R0, CNT
				LDR R1, R0
				ADI R1, 1
				STR R1, R0

				; get the fib number result 
				MOV R0, SP				
				CMP R1, R1
				ADI R1, 4				; Size of stack word 
				CMP R2, R2				
				ADI R2, 1				; Number of stack words we need to traverse
				MUL R1, R2				; offset
				SUB R0, R1				
				LDR R0, R0				; value returned by the fib function call  

				; get fibArr address for the next index
				LDA R1, fibArr			; get address of fibArr
				LDR R2, CNT 			; get current value of CNT
				CMP R3, R3
				ADI R3, 4				; size of individual 
				MUL R2, R3				; fibArr offset
				ADD R1, R2				; now points at the index in fibArr we want to store 

				; store the y value
				STR R0, R1 				; store the y value

			
				LDA R0, CNT 			; INCREMENT COUNTER
				LDR R1, R0
				ADI R1, 1
				STR R1, R0



				ULK fibArr 				; UNLOCK ARRAY MUTEX

				ULK CNT

				END 					; END NON MAIN THREAD
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
; PART THREE END %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

				; -- MAIN FUNCTION RETURN -----------------------------------------------------
				; deallocate the frame
MAINRETURN		MOV SP, FP				; SP = FP

				MOV R1, FP				; FP => R1
				CMP R2, R2
				ADI R2, 4				; Size of stack word => R2
				CMP R3, R3				
				ADI R3, 2				; Activation record slot we want to store in (not 0 based)
				MUL R2, R3				; offset
				SUB R1, R2				; R1 now points to where we store PFP on stack
				LDR FP, R1				; FP = PFP

				; Test for underflow				
				MOV R7, SP
				CMP R7, SB
				BGT R7, underflow 		; if SP > SB, UNDERFLOW

				; Get return address from stack
				MOV R1, SP				; FP => R1
				CMP R2, R2
				ADI R2, 4				; Size of stack word => R4
				CMP R3, R3				
				ADI R3, 1				; Activation record slot we want to store in (not 0 based)
				MUL R2, R3				; stackWordSize * n => R4
				SUB R1, R2				; R5 now points to where we store return address on stack
				LDR R7, R1				; Get return address from stack

				; Place return value on top of stack
				; no return values in this case

				; Return from function
				JMR R7
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
; ==============================================================================================
; END MAIN FUNCTION
; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



; **********************************************************************************************
; FIB FUNCTION
; **********************************************************************************************
FIB 			; -- INSIDE FUNCTION PREP ------------------------------------------------------
				; Compute space needed for the rest of activation record (local, temp)
				; One 3 temporary variables needed
				CMP R7, R7				
				ADI R7, 3				; one local variable, no temporary vars.  
				CMP R2, R2
				ADI R2, 4				; size of stack word
				MUL R7, R2				; ************** FrameSize => R7

				; Test for Overflow
				MOV R2, SP
				SUB R2, R7				; SP - frameSize => R2
				CMP R2, SL
				BLT R2, overflow 		; if SP < SL, OVERFLOW
				
				; Allocate space on stack for the rest of the frame (FP and PFP stays same)
				SUB SP, R7				; SP = SP - frameSize

				; place local vars on stack 
				; (initialize all temp vars to zero ) 
				
				; place temporary vars on stack
				; NONE
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


				; -- FUNCTION BODY ------------------------------------------------------------
				; if (n <= 1) 
				; get n off the stack
				MOV R0, FP				; FP => R0
				CMP R1, R1
				ADI R1, 4				; Size of stack word 
				CMP R2, R2				
				ADI R2, 3 				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; offset
				SUB R0, R1				; R0 Holds address of n *************************

				LDR R1, R0				; Get current value of n
				CMP R2, R2
				ADI R2, 1				; place a 1 into R2
				CMP R1, R2		
				BLT R1, ifRes1			; if less then, go to first option in if statement
				BRZ	R1, ifRes1			; if equal to, go to first option in if statement
				JMP ifElse				; if greater than, jump to else option in if statement

ifRes1			; return n; 
				LDR R7, R0				; Get current value of n and return
				JMP fibReturn

ifElse			; return fib(n - 1) + fib(n - 2)
				; Activation record slot 4 = fib(n - 1)
				; Activation record slot 5 = fib(n - 2)
				; Activation record slot 6 = the additino of the results of the two fib functions
				; call the function, get the returned value, place it in the activation record

				; get current value of n into R0
				MOV R0, FP				; FP => R0
				CMP R1, R1
				ADI R1, 4				; Size of stack word 
				CMP R2, R2				
				ADI R2, 3 				; Activation record slot where n is (not 0 based)
				MUL R1, R2				; offset
				SUB R0, R1				; R0 Holds address of n *************************

				; -- FIB FUNCTION CALL ----------------------------------------------------
				; Activation Record Size (return, PFP, 1 param) = 3
				CMP R7, R7				 
				ADI R7, 3				; number of stack words needed for frame
				CMP R6, R6
				ADI R6, 4				; size of stack word
				MUL R7, R6				; ************** FrameSize => R7

				; Test for Overflow
				MOV R6, SP
				SUB R6, R7				; SP - frameSize => R6
				CMP R6, SL
				BLT R6, overflow 		; if SP < SL, OVERFLOW
				
				; Allocate space on stack for new frame
				MOV R6, FP				; ************** PFP = FP => R6
				MOV FP, SP 				; FP = SP
				SUB SP, R7				; SP = SP - frameSize

				; Figure out return address and put that on the stack
				CMP R3, R3
				ADI R3, 12				; Size of instruction word = > R3
				CMP R2, R2				
				ADI R2, 28				; # inst btw PC mov and inst to ex upon return***** FIX **
				MUL R3, R2				; R3 now holds the PC offset

				MOV R5, PC
				ADD R5, R3				; return address => R5 

				MOV R4, FP				; FP => R1
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 1				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; FP offset => R4
				SUB R4, R3				; R4 now points to where we store return address on stack
				STR R5, R4				; place return address on stack

				; Put PFP on stack
				MOV R4, FP				; FP => R4   
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 2				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R5 now points to where we store the PFP on stack
				STR R6, R4				; place PFP on stack

				; One parameter must be given (n - 1)
				; Get value of first parameter into R6 
				LDR R6, R0				; get current value of n
				ADI R6, -1				; n - 1

				; Put 1st param on stack
				MOV R4, FP				; FP => R4     
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 3				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R4 now points to where we store the PFP on stack
				STR R6, R4

				; Call the function
				JMP FIB
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

				; Save return value on the stack (activation record slot 4) 
				MOV R0, SP				; FP => R1
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 1				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; stackWordSize * n => R4
				SUB R0, R1				; R5 now points to where we store return address on stack
				LDR R0, R0				; Get return value from stack			

				MOV R4, FP				; FP => R4     
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 4				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R4 now points to where we store the PFP on stack
				STR R0, R4


				; get current address of n into R0 
				MOV R0, FP				; FP => R0
				CMP R1, R1
				ADI R1, 4				; Size of stack word 
				CMP R2, R2				
				ADI R2, 3 				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; offset
				SUB R0, R1				; R0 Holds address of n *************************

				; -- FIB FUNCTION CALL ----------------------------------------------------
				; Activation Record Size (return, PFP, 1 param) = 3
				CMP R7, R7				 
				ADI R7, 3				; number of stack words needed for frame
				CMP R6, R6
				ADI R6, 4				; size of stack word
				MUL R7, R6				; ************** FrameSize => R7

				; Test for Overflow
				MOV R6, SP
				SUB R6, R7				; SP - frameSize => R6
				CMP R6, SL
				BLT R6, overflow 		; if SP < SL, OVERFLOW
				
				; Allocate space on stack for new frame
				MOV R6, FP				; ************** PFP = FP => R6
				MOV FP, SP 				; FP = SP
				SUB SP, R7				; SP = SP - frameSize

				; Figure out return address and put that on the stack
				CMP R3, R3
				ADI R3, 12				; Size of instruction word = > R3
				CMP R2, R2				
				ADI R2, 28				; # inst btw PC mov and inst to ex upon return***** FIX **
				MUL R3, R2				; R3 now holds the PC offset

				MOV R5, PC
				ADD R5, R3				; return address => R5 

				MOV R4, FP				; FP => R1
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 1				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; FP offset => R4
				SUB R4, R3				; R4 now points to where we store return address on stack
				STR R5, R4				; place return address on stack

				; Put PFP on stack
				MOV R4, FP				; FP => R4   
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 2				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R5 now points to where we store the PFP on stack
				STR R6, R4				; place PFP on stack

				; One parameter must be given
				; Get value of first parameter into R6 
				LDR R6, R0				; get current value of n
				ADI R6, -2				; n - 2

				; Put 1st param on stack
				MOV R4, FP				; FP => R4     
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 3				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R4 now points to where we store the PFP on stack
				STR R6, R4

				; Call the function
				JMP FIB
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

				; Save return value on the stack (activation record slot 5) 
				MOV R0, SP				; FP => R1
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 1				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; stackWordSize * n => R4
				SUB R0, R1				; R5 now points to where we store return address on stack
				LDR R0, R0				; Get return address from stack	

				MOV R4, FP				; FP => R4     
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 5				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R4 now points to where we store the return on stack
				STR R0, R4


				; Get the results from the different fib functions from the stack
				; add them together
				; put result on the stack (activation record position 6)
				
				; fib(n - 1) result => R6
				MOV R4, FP				; FP => R4     
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 4				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R4 now points to where we store the PFP on stack
				LDR R6, R4

				; fib(n - 2) result => R7
				MOV R4, FP				; FP => R4     
				CMP R3, R3
				ADI R3, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 5				; Activation record slot we want to store in (not 0 based)
				MUL R3, R2				; stackWordSize * n => R4
				SUB R4, R3				; R4 now points to where we store the PFP on stack
				LDR R7, R4

				; fib(n - 1) + fib(n - 2) => R7
				ADD R7, R6

				JMP fibReturn

ifEnd
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


fibReturn		; -- RETURN -----------------------------------------------------------------
				; deallocate the frame
				MOV SP, FP				; SP = FP

				MOV R0, FP				; FP => R1
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 2				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; stackWordSize * n => R4
				SUB R0, R1				; R5 now points to where we store PFP on stack
				LDR FP, R0				; FP = PFP

				; Test for underflow				
				MOV R0, SP
				CMP R0, SB
				BGT R0, underflow 		; if SP > SB, UNDERFLOW

				; Get return address from stack
				MOV R0, SP				; FP => R1
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 1				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; stackWordSize * n => R4
				SUB R0, R1				; R5 now points to where we store return address on stack
				LDR R5, R0				; RETURN ADDRESS => R5 ***********************************

				; Place return value on top of stack
				MOV R0, SP
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R4
				CMP R2, R2				
				ADI R2, 1				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; stackWordSize * n => R4
				SUB R0, R1
				STR R7, R0				; store return VALUE on the stack 

				; Return from function
				JMR R5
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
; ===============================================================================================
; END FIB FUNCTION
; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

				; TESTING
				LDR R3, FP 
				TRP 1
				; ^^^^^^^^^^^^^^^^

				; TESTING - for some reason, we lost the user given value in the Main's temporary variable after the first fib function call.  THIS IS WHERE I LEFT OFF
				MOV R0, FP				; FP => R2
				CMP R1, R1
				ADI R1, 4				; Size of stack word => R3
				CMP R2, R2				
				ADI R2, 3 				; Activation record slot we want to store in (not 0 based)
				MUL R1, R2				; R3 holds offset
				SUB R0, R1				; R2 now points to where we store the param on stack
				LDR R3, R0
				TRP 1
				; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^


; **********************************************************************************************
; ERROR REPORTING
; **********************************************************************************************
overflow 		CMP R3, R3
				ADI R3, 10
				TRP 3
				CMP R3, R3		; clear R3
				ADI R3, 79		; ASCII code for O
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 86		; ASCII code for V
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 69		; ASCII code for E
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 82		; ASCII code for R
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 70		; ASCII code for F
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 76		; ASCII code for L
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 79		; ASCII code for O
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 87		; ASCII code for W
				TRP 3 	
				CMP R3, R3
				ADI R3, 10
				TRP 3		
				JMP end

underflow		CMP R3, R3
				ADI R3, 10
				TRP 3
				CMP R3, R3		; clear R5
				ADI R3, 85		; ASCII code for U
				TRP 3
				CMP R3, R3		; clear R3
				ADI R3, 78		; ASCII code for N
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 68		; ASCII code for D
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 69		; ASCII code for E
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 82		; ASCII code for R
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 70		; ASCII code for F
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 76		; ASCII code for L
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 79		; ASCII code for O
				TRP 3 
				CMP R3, R3		; clear R3
				ADI R3, 87		; ASCII code for W
				TRP 3 	
				CMP R3, R3
				ADI R3, 10
				TRP 3	
				JMP end
; ===============================================================================================
; END ERROR REPORTING
; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
