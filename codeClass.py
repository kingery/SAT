# Copyright (C) R. Scout Kingery, 2013
# University of Southern California
# Ming Hsieh Dept. of Electrical Engineering
# Communication Sciences Institiute
#
#
#
# codeClass.py
# python module defining a code class
# ATTRIBUTES:
# N,K - code parameters
# partners      - an np array containing the N-K symplecic partners
# Xops          - an np array of the K logical X operators
# Zops          - an np array of the K logical Z operators
# gens          - an np array of the N-K stabilize generators
# Lsupport      - a list of qubits which support a given logical operator
#
#
# METHODS:
# generateStabilizer()  
#       no input arguments.  Generates the entire stabilizer group and stores it
#       in np array self.stabilizer
# generateCNFVariables(circuitfile)
#       input circuitfile is a closed file containing a non-cnf "circuit" as generated by other methods.
#       returns (self.cnf,self.variables)


import math
import linecache
import numpy as np
import itertools
import SATfunctions
from subprocess import call

class Code(object):
###Code class has attributes for a given quantum code.
    def __init__(self,M,N,K):
        self.N = N
        self.M = N
        self.K = K
        self.partners = M[0:N-K]
        self.Xops = M[N-K:N]
        self.gens = M[N:2*N-K]
        self.Zops = M[2*N-K:2*N]
        self.Lsupport = range(N)

    def generateStabilizer(self):
    ##generate the entire stabilizer group attribute
        self.stabilizer = np.zeros([2**(self.N-self.K)-1,2*self.N],int) #allocate space
        count = 0
        for i in range(1,self.N-self.K+1):
            for subset in itertools.combinations(self.gens,i):
                for stab in subset:
                    self.stabilizer[count] = self.stabilizer[count] + stab
                self.stabilizer[count] = np.mod(self.stabilizer[count],2)
                count += 1
    
    def generateCNFVariables(self,circuitfile):
    ###generate (cnf,vars) as code values
        C = []
        for line in file(circuitfile):
            if line.strip():
                C.append(eval(line))
        (self.cnf,self.variables) = SATfunctions.circuit_to_cnf(C)

    def generateDimacs(self,dimacsfile):
    ###generates a dimacs file from the CNF form
        dimacs = SATfunctions.cnf_to_dimacs(self.cnf)

        f = open(dimacsfile,'w')
        f.write(dimacs)
        f.close()

    def getValues(self,lookupfile):
    ### method to return satisfying values for a,b,c,e, etc.
    ### circuitfile must be a closed file
        self.a = np.ones(self.M,int)
        self.b = np.ones(self.M,int)
        self.c = np.ones(self.M,int)
        self.e = np.ones(self.M,int)
        self.La = np.ones(2*self.M,int)
        self.Lsat = np.ones(2*self.M,int)

        # print self.a
        # print self.b
        # print self.c
        # print self.e

        # determine satisfying assignment for a,b,c,e
        for i in range(self.M):
            lineIndex = self.variables['a_%d' % i]
            if '-' in linecache.getline(lookupfile,lineIndex+1):
                self.a[i]=0
                # print self.a[i]
            lineIndex = self.variables['b_%d' % i]
            if '-' in linecache.getline(lookupfile,lineIndex+1):
                self.b[i]=0
                # print self.b[i]
            lineIndex = self.variables['c_%d' % i]
            if '-' in linecache.getline(lookupfile,lineIndex+1):
                self.c[i]=0
            lineIndex = self.variables['e_%d' % i]
            if '-' in linecache.getline(lookupfile,lineIndex+1):
                self.e[i]=0
        for i in range(2*self.M):
            lineIndex = self.variables['La_%d' % i]
            if '-' in linecache.getline(lookupfile,lineIndex+1):
                self.La[i]=0

        #define self.A, self.B
        self.A = np.concatenate((np.concatenate((np.diag(self.a),np.diag(self.e)),axis=1),np.concatenate((np.diag(self.b),np.diag(self.c)),axis=1)))
        self.B = np.concatenate((np.concatenate((np.diag(self.c),np.diag(self.e)),axis=1),np.concatenate((np.diag(self.b),np.diag(self.a)),axis=1)))

        #check to see if Lsat is equal to L
        for i in range(2*self.M):
            lineIndex = self.variables['L_%d' % i]
            if '-' in linecache.getline(lookupfile,lineIndex+1):
                self.Lsat[i]=0
        
    def lightLogOp(self):
    ### sets the lowest weight representative of the logical operator equivalence class (self.lowL),
    ### sets the weight (self.M)
    ### sets the support of the lowest weight representative (self.Lsupport)
    ### must have previously set attribute L, an np.array

        self.Lsupport = []
        ##iteratate over each element of the stabilizer
        for stab in self.stabilizer:
            Ltemp = np.mod(stab+self.L,2)
            tempWeight = self.weight(Ltemp)
            #check new weight and update if we have improvement
            if tempWeight < self.M:
                self.M = tempWeight
                self.lowL = Ltemp
        #determine the support of the smallest 
        for i in range(self.N):
            if self.lowL[i] or self.lowL[i+self.N]:
                self.Lsupport.append(i)

    # def generateLogicalClasses(self):
    #     self.

    def weight(self, pauli):
    ###method taking a pauli operator in symplectic form and returning that operators weight
    
    	N = len(pauli)/2
    	weight = 0
    	for i in range(N):
    		if pauli[i]+pauli[i+N]:
    			weight = weight + 1
    
    	return(weight)

    def truncate(self):
    ### truncate all the stabilizer generators and logical operators

        self.truncatedGens = np.zeros([self.N-self.K,2*self.M],int)
        self.truncatedXops = np.zeros([self.K,2*self.M],int)
        self.truncatedZops = np.zeros([self.K,2*self.M],int)
        self.truncatedL = np.zeros(2*self.M,int)

        # iterate over all generators
        for i in range(self.N-self.K):
            #iterate over all support qubits
            for j in self.Lsupport:
                #copy values to self.truncatedGens
                if self.gens[i][j]:
                    self.truncatedGens[i][self.Lsupport.index(j)] = 1
                if self.gens[i][j+self.N]:
                    self.truncatedGens[i][self.Lsupport.index(j)+self.M] = 1

        # iterate over all logical operators
        for i in range(self.K):
            #iterate over all support qubits
            for j in self.Lsupport:
                #copy values to self.truncatedXops
                if self.Xops[i][j]:
                    self.truncatedXops[i][self.Lsupport.index(j)] = 1
                if self.Xops[i][j+self.N]:
                    self.truncatedXops[i][self.Lsupport.index(j)+self.M] = 1
                #copy values to self.truncatedZops
                if self.Zops[i][j]:
                    self.truncatedZops[i][self.Lsupport.index(j)] = 1
                if self.Zops[i][j+self.N]:
                    self.truncatedZops[i][self.Lsupport.index(j)+self.M] = 1

        for j in range(self.M):
            self.truncatedL[j] = self.lowL[self.Lsupport[j]]
            self.truncatedL[j+self.M] = self.lowL[self.Lsupport[j]+self.N]

    def propogate(self):
    ### propogate truncated generators, Xops, and Zops

        self.propogatedGens = np.transpose(np.dot(self.A,np.transpose(self.truncatedGens)))
        self.propogatedXops = np.transpose(np.dot(self.A,np.transpose(self.truncatedXops)))
        self.propogatedZops = np.transpose(np.dot(self.A,np.transpose(self.truncatedZops)))
        self.propogatedVectors = np.concatenate((self.propogatedGens,self.propogatedZops,self.propogatedXops))
        self.propogatedVectors[self.N-self.K+self.logicalOpIndex] = np.zeros(2*self.M)

    def determineHBasis(self):
    ### take the propogated vectors and determine a basis for stabilizers of ancillary code
    ### generates and updates an array containing the entire span of the basis
    ### NOT EFFICIENT!!! EXPONENTIAL TIME PROCESS!!!

        # self.hBasis = np.zeros(2*self.M)
        # self.span = np.zeros(2*self.M)
        
        # for vector in self.propogatedVectors:
        #     if vector not in self.span:
        #         # vector not in span, add it to the basis
        #         self.hBasis = np.concatenate((self.hBasis,vector)
        #         # update the new span
        #         spanUpdate = np.mod(self.span + vector,2)
        #         self.span = np.concatenate((self.span,spanUpdate))

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

    def checkInSpan(self, matrix):
    ### performs Gaussian elimination mod 2 to determine if a vector is in the span of a basis
    ### input: matrix - a np.array with basis as as columns and last column containing the vector in question

        (rows,cols) = matrix.shape
        # # perform row ops to achieve row-echelon form
        # for i in range(rows):
        #     for j in range(i,cols):
        #         # find first row with a leading 1 and bring it to the top
        #         for k in range(i,rows):
        #             if matrix[k][j]:
        #                 matrix = self.swapRows(matrix,i,k)
        #                 break
        #         # eliminate ones to make pivot
        #         for k in range(i,rows):
        #             if matrix[k][j]:
        #                 matrix[k] = np.mod(matrix[k]+matrix[i],2)

        self.REF(matrix)

        # # work backwards to determine if vector is in span
        
        # for i in reversed(range(rows)):

        for i in range(rows):
            # return False if a sum of zeros must be non zero
            # if np.array_equal(matrix[i][:cols-2],np.zeros(cols-1)) and matrix[i][cols-1]:

            if (matrix[i][:cols-1]==np.zeros(cols-1)).all() and matrix[i][-1]:
                return(False)

        return(True)

    def REF(self, matrix):
    ### reduces a matrix to row echelon form, mod 2

        (rows,cols) = matrix.shape

        for i in range(cols):
            # find row with leading one and bring it to the top
            for j in range(i,rows):
                if matrix[j][i]:
                    self.swapRows(matrix,i,j)
                    break
            # zero out the following rows in column i after leading one
            for j in range(i+1,rows):
                if matrix[j,i]:
                    matrix[j] = np.mod(matrix[i]+matrix[j],2)

        # return matrix

        # # perform row ops to achieve row-echelon form
        # for i in range(rows):
        #     for j in range(i,cols):
        #         # find first row with a leading 1 and bring it to the top
        #         for k in range(i,rows):
        #             if matrix[k][j]:
        #                 matrix = self.swapRows(matrix,i,k)
        #                 break
        #         # eliminate ones to make pivot
        #         for k in range(i,rows):
        #             if matrix[k][j]:
        #                 matrix[k] = np.mod(matrix[k]+matrix[i],2)

    def swapRows(self,matrix,row1,row2):
    ### swaps the rows of matrix
        
        temp = np.copy(matrix[row1])
        matrix[row1] = matrix[row2]
        matrix[row2] = temp


    def writeLogicalCircuit(self,circuitfile):
    ### writes the logical circuit to the file
    ###going to need to know what the block code is (parameters, stabilizer gnerators, logical operators
    #circuitfile must be an open (-w) file
    
    #define vectors a,b,c,e which describe the forward and backward propogation of pauli operators due to the transversal circuit
        for i in range(self.M):
            circuitfile.write("'ac_%d','and','a_%d','c_%d'\n" % (i,i,i))
            circuitfile.write("'be_%d','and','b_%d','e_%d'\n" % (i,i,i))
            circuitfile.write("'ac_%d','equal','be_%d'\n" % (i,i))
        ##main requirement: IxLa-->LxLa ==> BLa=L
        #write clauses defining B*La
        for i in range(self.M):
            #BLa_1_i is c_i*La_i
            circuitfile.write("'BLa_1_%d','and','c_%d','La_%d'\n" % (i,i,i))
            #BLa_2_i is e_i*La_i+M
            circuitfile.write("'BLa_2_%d','and','e_%d','La_%d'\n" % (i,i,i+self.M))
            circuitfile.write("'BLa_%d','xor','BLa_1_%d','BLa_2_%d'\n" % (i,i,i))
            circuitfile.write("'BLa_%d','equal','L_%d'\n" % (i,i))
        for i in range(self.M,2*self.M):
            #BLa_1_i is b_i*La_i
            circuitfile.write("'BLa_1_%d','and','b_%d','La_%d'\n" % (i,i-self.M,i-self.M))
            #BLa_2_i is a_i*La_i+M
            circuitfile.write("'BLa_2_%d','and','a_%d','La_%d'\n" % (i,i-self.M,i))
            circuitfile.write("'BLa_%d','xor','BLa_1_%d','BLa_2_%d'\n" % (i,i,i))
            circuitfile.write("'BLa_%d','equal','L_%d'\n" % (i,i))
        #write clauses restricting L to be the desired logical op
        for i in range(2*self.M):
        	if self.L[i]:
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

# def getValues(circuitfile,minisat_output,code):
# ### method to return satisfying values for a,b,c,e, etc.
# ### circuitfile must be a closed file
#     Rsat=np.ones([2*code.N,2*code.N],int)   #create empty np array
#     code.a = np.ones(code.M,int)
#     code.b = np.ones(code.M,int)
#     code.c = np.ones(code.M,int)
#     code.e = np.ones(code.M,int)

#     # determine satisfying assignment for a,b,c,e
#     for i in range(code.M):

#         lineIndex = variables['a_%d' % i]
#         if '-' in linecache.getline(minisat_output,lineIndex+1):
#             code.a[i]=0
#         lineIndex = variables['b_%d' % i]
#         if '-' in linecache.getline(minisat_output,lineIndex+1):
#             code.b[i]=0
#         lineIndex = variables['c_%d' % i]
#         if '-' in linecache.getline(minisat_output,lineIndex+1):
#             code.c[i]=0
#         lineIndex = variables['e_%d' % i]
#         if '-' in linecache.getline(minisat_output,lineIndex+1):
#             code.e[i]=0


