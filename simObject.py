# R. Scout Kingery, 2013
# University of Southern California
# Ming Hsieh Dept. of Electrical Engineering
# Communication Sciences Institiute
#
#
#
# simObject.py
# a python object definition.  A simObject will store all the pertinent attributes like number of desired results, which logical operator to search for, etc.  The methods will include the ability to read/write files, call minisat, etc.

import numpy as np
import linecache
from subprocess import call
import SATfunctions, circuit

class sim(object)
###Sim class definition
    def __init__(self):
        self.L = 0
        
    def generateDimacs(self,code,dimacsfile):
    ###generates a dimacs file from the CNF form
        dimacs = SATfunctions.cnf_to_dimacs(self.cnf)

        f = open(dimacsfile,'w')
        f.write(dimacs)
        f.close()
        
    def generateCNFVariables(self,circuitfile):
    ###generate (cnf,vars) as code values
        C = []
        for line in file(circuitfile):
            if line.strip():
                C.append(eval(line))
        (self.cnf,self.variables) = SATfunctions.circuit_to_cnf(C)

    def determineHBasis(self):
    ### take the propogated vectors and determine a basis for stabilizers of ancillary code
    ### uses Gaussian elimination to determine if vector is in the span efficiently

        self.hBasis = np.array(np.zeros([self.M,2*self.M],int))
        # self.span = np.zeros(2*self.M)

        # print self.propogatedVectors
        count = 0
        # print self.hBasis

        for vector in self.propogatedVectors:
            self.hBasis[-1]=vector
            checkerThing = np.copy(self.hBasis)
            if not self.checkInSpan(np.transpose(checkerThing)):
                self.hBasis[count] = vector
                count += 1

        # print "Ancilla Code Stabilizer Generators:"
        # print self.hBasis

    def writeLogicalCircuit(self,code):
    ### writes the logical circuit to the file
    ###going to need to know what the block code is (parameters, stabilizer gnerators, logical operators
    #circuitfile must be an open (-w) file
    
    #define vectors a,b,c,e which describe the forward and backward propogation of pauli operators due to the transversal circuit
        for i in range(code.M):
            circuitfile.write("'ac_%d','and','a_%d','c_%d'\n" % (i,i,i))
            circuitfile.write("'be_%d','and','b_%d','e_%d'\n" % (i,i,i))
            circuitfile.write("'ac_%d','equal','be_%d'\n" % (i,i))
        ##main requirement: IxLa-->LxLa ==> BLa=L
        #write clauses defining B*La
        for i in range(code.M):
            #BLa_1_i is c_i*La_i
            circuitfile.write("'BLa_1_%d','and','c_%d','La_%d'\n" % (i,i,i))
            #BLa_2_i is e_i*La_i+M
            circuitfile.write("'BLa_2_%d','and','e_%d','La_%d'\n" % (i,i,i+code.M))
            circuitfile.write("'BLa_%d','xor','BLa_1_%d','BLa_2_%d'\n" % (i,i,i))
            circuitfile.write("'BLa_%d','equal','L_%d'\n" % (i,i))
        for i in range(code.M,2*code.M):
            #BLa_1_i is b_i*La_i
            circuitfile.write("'BLa_1_%d','and','b_%d','La_%d'\n" % (i,i-code.M,i-code.M))
            #BLa_2_i is a_i*La_i+M
            circuitfile.write("'BLa_2_%d','and','a_%d','La_%d'\n" % (i,i-code.M,i))
            circuitfile.write("'BLa_%d','xor','BLa_1_%d','BLa_2_%d'\n" % (i,i,i))
            circuitfile.write("'BLa_%d','equal','L_%d'\n" % (i,i))
        #write clauses restricting L to be the desired logical op
        for i in range(2*code.M):
        	if code.L[i]:
        		circuitfile.write("'L_%d','equal','one'\n" %i)
        	else:
        		circuitfile.write("'L_%d','equal','zero'\n" %i)

    def runMinisat(self):
        call(["opt/local/bin/minisat",self.dimacsfile,self.outputfile])
        call(self.outputToLookup,shell=True)
                
    def updateDimacs(self):
        # update the dimacs file to require a new solution on next iteration
         
        newClause = ''
        lines = open(self.dimacsfile).readlines()
        lines[0] = 'p cnf ' + lines[0].split()[-2] + ' ' + str(int(lines[0].split()[-1]) + 1) + '\n'
        f = open(self.dimacsfile,'w')
        for line in lines:
            f.write(line)
        f.close()
        
        for i in range(self.M):
            lineIndex = self.variables['a_%d' % i]
            if '-' in linecache.getline('lookup', lineIndex + 1):
                newClause += str(lineIndex) + ' '
            else:
                newClause += '-' + str(lineIndex) + ' '
             
            lineIndex = self.variables['b_%d' % i]
            if '-' in linecache.getline('lookup', lineIndex + 1):
                newClause += str(lineIndex) + ' '
            else:
                newClause += '-' + str(lineIndex) + ' '
      
            lineIndex = self.variables['c_%d' % i]
            if '-' in linecache.getline('lookup', lineIndex + 1):
                newClause += str(lineIndex) + ' '
            else:
                newClause += '-' + str(lineIndex) + ' '
                
            lineIndex = self.variables['e_%d' % i]
            if '-' in linecache.getline('lookup', lineIndex + 1):
                newClause += str(lineIndex) + ' '
            else:
                newClause += '-' + str(lineIndex) + ' '

        linecache.clearcache()
        newClause += '0\n'

        f = open(self.dimacsfile,'a')
        f.write(newClause)
        f.close()
