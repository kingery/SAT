# Copyright (C) R. Scout Kingery, 2013
# University of Southern California
# Ming Hsieh Dept. of Electrical Engineering
# Communication Sciences Institiute
#
#
#
# findSolutions.py
# a script that will determine a transversal circuit, maximum error-correcting ancillary code

#import modules and necessary methods
import codeClass, SATfunctions
import numpy as np
import linecache
from subprocess import call

from constants import A, codeInfo
from sys import argv

script, circuitfile, dimacsfile = argv
N = int(N)
K = int(K)
M = np.array(A,int)
outputToLookup = ["cat","output","|","tr","' '","'\n'",">","lookup"]

code = logical.Code(M,codeInfo['N'],codeInfo['K'])
code.generateStabilizer()
code.logicalOpIndex = 1
if code.logicalOpIndex < K:
	code.L = M[code.logicalOpIndex + N-K]
else:
	code.L = M[code.logicalOpIndex + 2*(N-K)]

code.codeInfo = codeInfo
code.truncatedL=code.L
code.lightLogOp()

code.truncate()

f = open(circuitfile,'w')
logical.writeLogicalCircuit(f,code)
f.close()

code.generateCNFVariables(circuitfile)
code.generateDimacs(dimacsfile)


###------------------------
### 	* create output file
### 	* write code information to file
###		* write 
###------------------------

workflowFunctions(code)

####----------------------
#### ADJUST DIMACS TO REQUIRE NEW SOLUTION
####----------------------

workflowFunctions.newSolution(code,dimacsfile)
