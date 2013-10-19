# Copyright (C) R. Scout Kingery, 2013
# University of Southern California
# Ming Hsieh Dept. of Electrical Engineering
# Communication Sciences Institiute
#
#
#
# MAIN
# the main function which will actually run the search for fault-tolerant measurements

# import the modules, class definitions, and code data
import codeClass, SATfunctions #workflowFunctions
import numpy as np
import linecache
from subprocess import call

from constants import A, codeInfo
from sys import argv

script, N, K = argv

N = int(N)
K = int(K)
M = np.array(A,int)

code = codeClass.Code(M,N,K)
code.generateStabilizer()
code.outputToLookup = ["cat","output","|","tr","' '","'\n'",">","lookup"]

code.logicalOpIndex = 0;
if code.logicalOpIndex < K:
    code.L = M[code.logicalOpIndex + N - K]
else:
    code.L = M[code.logicalOpIndex + 2(N-K)]

code.codeInfo = codeInfo
code.truncatedL = code.L
code.lightLogOp()
code.truncate()

### write code for generating a cicuitfile string based on simulation parameters
### generate a dimacs file too.  This will make it easier to go back and find the circuits
### defining the good solutions
code.circuitfile = 'circuitfile_'
code.dimacsfile = 'dimacsfile_'
code.outputfile = 'outputfile_'

f = open(code.circuitfile,'w')
code.writeLogicalCircuit(f)
f.close()

code.generateCNFVariables(code.circuitfile)
code.generateDimacs(code.dimacsfile)

f = open("n%dk%dL%d_%d"%(code.N,code.K,code.logicalOpIndex,1),"w") 
f.write("--------------------\n")
f.write(code.codeInfo + "\n")
if code.logicalOpIndex < code.K:
    f.write("measuring logical X%d" % code.logicalOpIndex + "\n")
else:
    f.write("measuring logical Z%d" % (code.logicalOpIndex - code.K) + "\n")

# run minisat and catlog the results
code.runMinisat()
code.getValues('lookup')
# propogate the resulting vectors and determine a basis for the ancilla stabilizer
code.propogate()
code.determineHbasis()
##write to output the simulation results
code.writeResults()
# further restric the dimacs file to find new solution on next iteration
code.updateDimacs()


