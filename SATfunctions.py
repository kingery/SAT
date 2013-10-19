# Copyright (C) R. Scout Kingery, 2013
# University of Southern California
# Ming Hsieh Dept. of Electrical Engineering
# Communication Sciences Institiute
#
#
#
# SATfunctions
# a module containing functions for the project.

def writeLogicalCircuit(circuitfile,code):
    ###going to need to know what the block code is (parameters, stabilizer gnerators, logical operators
    ###circuitfile must be an open (writable) file

    #write clauses restricting L to be the desired logical op
    for i in range(2*code.M):
        if code.truncatedL[i]:
            circuitfile.write("'L_%d','equal','one'\n" %i)
        else:
            circuitfile.write("'L_%d','equal','zero'\n" %i)
    #define vectors a,b,c,e which describe the forward and backward propogation of pauli operators due to the transversal circuit
    for i in range(code.M):
        circuitfile.write("'ac_%d','and','a_%d','c_%d'\n" % (i,i,i))
        circuitfile.write("'be_%d','and','b_%d','e_%d'\n" % (i,i,i))
        circuitfile.write("'ac_%d','equal','be_%d'\n" % (i,i))
    ##main requirement: IxLa-->LxLa ==> BLa=L
    #write clauses defining B*La
    for i in range(code.M):
        #BLa_i_1 is c_i*La_i
        circuitfile.write("'BLa_%d_1','and','c_%d','La_%d'\n" % (i,i,i))
        #BLa_i_2 is e_i*La_i+M
        circuitfile.write("'BLa_%d_2','and','e_%d','La_%d'\n" % (i,i,i+code.M))

        circuitfile.write("'BLa_%d','xor','BLa_%d_1','BLa_%d_2'\n" % (i,i,i))
        circuitfile.write("'BLa_%d','equal','L_%d'\n" % (i,i))
    for i in range(code.M,2*code.M):
        #BLa_i_1 is b_i*La_i
        circuitfile.write("'BLa_%d_1','and','b_%d','La_%d'\n" % (i,i-code.M,i-code.M))
        #BLa_i_2 is a_i*La_i+M
        circuitfile.write("'BLa_%d_2','and','a_%d','La_%d'\n" % (i,i-code.M,i))

        circuitfile.write("'BLa_%d','xor','BLa_%d_1','BLa_%d_2'\n" % (i,i,i))
        circuitfile.write("'BLa_%d','equal','L_%d'\n" % (i,i))

def getA(circuitfile,minisat_output,code):
    ##### method to return satisfying matrix A
    ### circuitfile must be a closed file
    C=[]
    A=np.zeros([2*code.M,2*code.M],int)   #create empty np array
    
    for line in file(circuitfile):
        if line.strip():
            C.append(eval(line))

    (cnf,variables) = circuit_to_cnf(C)

    # determine satisfying assignment for A
    for i in range(code.M):        
        lineIndex = variables['a_%d' % i]
        if '-' not in linecache.getline(minisat_output,lineIndex+1):
            A[i][i] = 1
    for i in range(code.M):        
        lineIndex = variables['b_%d' % i]
        if '-' not in linecache.getline(minisat_output,lineIndex+1):
            A[i+code.M][i] = 1
    for i in range(code.M):        
        lineIndex = variables['c_%d' % i]
        if '-' not in linecache.getline(minisat_output,lineIndex+1):
            A[i+code.M][i+code.M] = 1
    for i in range(code.M):        
        lineIndex = variables['e_%d' % i]
        if '-' not in linecache.getline(minisat_output,lineIndex+1):
            A[i][i+code.M] = 1
            
    return(A)

def weight(pauli):
###method taking a pauli operator in symplectic form and returning that operators weight

    N = len(pauli)/2
    weight = 0
    for i in range(N):
        if pauli[i]+pauli[i+N]:
            weight = weight + 1

    return(weight)
        

def writeXORclauses(variables,row,col,matrixlabel,count,openfile):
###Function for writing clauses for XOR of a list of input variables.
#  variables is a list of variables to be xor'ed stored as string e.g. variables=['variable1','variable2']
    odds = []
    if len(variables)==1:
        openfile.write("'" + matrixlabel + "%d_%d','equal','" %(row,col) + variables[0] + "'\n")
        return()
    if len(variables)==2:
        openfile.write("'" + matrixlabel + "%d_%d','xor','" %(row,col) + variables[0] +"','"+ variables[1] + "'\n")
        return()
    if len(variables)%2:
        for k in range(len(variables)/2):
            openfile.write("'" + matrixlabel + "%d_%d_%d_%d','xor','" %(row,col,count,k) + variables[2*k] + "','" + variables[2*k+1] + "'\n")
            odds.append(matrixlabel + "%d_%d_%d_%d" %(row,col,count,k))
        odds.append(variables[-1])
    else:
        for k in range(len(variables)/2):
            openfile.write("'" + matrixlabel + "%d_%d_%d_%d','xor','" %(row,col,count,k) + variables[2*k] + "','" + variables[2*k+1] + "'\n")
            odds.append(matrixlabel + "%d_%d_%d_%d" %(row,col,count,k))
    
    count = count+1
    writeXORclauses(odds,row,col,matrixlabel,count,openfile)
    
def getR(circuitfile,minisat_output,N):
##### method to return satisfying matrix Rsat
### circuitfile must be a closed file
    C=[]
    Rsat=np.ones([2*N,2*N],int)   #create empty np array
    
    for line in file(circuitfile):
        if line.strip():
            C.append(eval(line))

    (cnf,variables) = circuit_to_cnf(C)

    # determine satisfying assignment for Rsat
    for i in range(2*N):
        for j in range(2*N):
                
            lineIndex = variables['r_%d_%d' % (i+1,j+1)]

            if '-' in linecache.getline(minisat_output,lineIndex+1):
                Rsat[i][j]=0

    return(Rsat)

def getBlock(circuitfile,minisat_output,label,rows,cols):
##### method to print the satisfying matrix
        
    C=[]
    block=np.ones([rows,cols],int)   #create empty np array
    
    for line in file(circuitfile):
        if line.strip():
            C.append(eval(line))

    (cnf,variables) = circuit_to_cnf(C)

    # determine satisfying assignment for Rsat
    for i in range(rows):
        for j in range(cols):
                
            lineIndex = variables[label + '_%d_%d' % (i+1,j+1)]

            if '-' in linecache.getline(minisat_output,lineIndex+1):
                block[i][j]=0

    return(block)

def symplecticInnerProduct(vec1,vec2,N):
#####returns the symplectic inner product between two symplectic vectors Vec1 and Vec2 of length N
    return np.dot(vec1[0:N],vec2[N:2*N]) + np.dot(vec1[N:2*N],vec2[0:N])            
                        
def getDimacs(circuitfile, dimacsfile):
### input closed file 'circuitfile' and write to a new file 'dimacsfile'
    C=[]

    for line in file(circuitfile):
        if line.strip():
            C.append(eval(line))

    (cnf,variables) = circuit_to_cnf(C)
    dimacs = cnf_to_dimacs(cnf)

    f = open(dimacsfile,'w')
    f.write(dimacs)
    f.close()

    
################################################################################################ 
################################################################################################     
################################################################################################    
####CIRCUIT.PY, included here###

# Copyright (C) 2011 by Henry Yuen, Joseph Bebel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# ToughSat Project

def bin(i):
     s = ""
     while i != 0:
             if i % 2 == 0:
                     s = "0" + s
             else:
                     s = "1" + s
             i = i >> 1
     s = "0b" + s
     return s

def num_var(cnf):
    vars = set()
    for clause in cnf:
        for literal in clause:
            vars.add(abs(literal))
    return len(vars)

def cnf_to_dimacs(cnf):
    dimacs = "p cnf " + str(num_var(cnf)) + " " + str(len(cnf)) + "\n"
    #dimacs += "c Factors encoded in variables 1-" + str(n) + " and " + str(n+1) + "-" + str(2*n) + "\n"
    for clause in cnf:
        for literal in clause:
            dimacs += str(literal) + " "
        dimacs += "0\n"
    return dimacs

def circuit_to_cnf(circuit):
    #make a dict of the variables used
    variables = dict()
    cnf_formula = []

    next_var = 1
    #add inputs so they're the first
    #for i in range(n):
    #    variables["x" + str(i)] = next_var
    #    next_var += 1
    #for i in range(n):
    #    variables["y" + str(i)] = next_var
    #    next_var += 1

    #cnf_formula.append( tuple(variables["x" + str(i)] for i in range(1,n)) )
    #cnf_formula.append( tuple(variables["y" + str(i)] for i in range(1,n)) )

    variables["zero"] = next_var
    cnf_formula.append( (-next_var,) )
    next_var += 1
    variables["one"] = next_var
    cnf_formula.append( (next_var,) )
    next_var += 1

    for line in circuit:
        op = line[1]
        if op in ("equal", "not"): #(op1, "equal", op2) ) set op1 = op2
            if line[0] not in variables:
                variables[line[0]] = next_var
                next_var += 1
            if line[2] not in variables:
                variables[line[2]] = next_var
                next_var += 1
        if op in ("and", "or", "xor"): #(op1, "and", op2, op3) op1 = op2 and op3
            if line[0] not in variables:
                variables[line[0]] = next_var
                next_var += 1
            if line[2] not in variables:
                variables[line[2]] = next_var
                next_var += 1
            if line[3] not in variables:
                variables[line[3]] = next_var
                next_var += 1
        if op == "plus": #(op1, "plus", op2, op3, op4, op5) where op1 = op2+op3+op4 and op5 is carryout
            if line[0] not in variables:
                variables[line[0]] = next_var
                next_var += 1
            if line[2] not in variables:
                variables[line[2]] = next_var
                next_var += 1
            if line[3] not in variables:
                variables[line[3]] = next_var
                next_var += 1
            if line[4] not in variables:
                variables[line[4]] = next_var
                next_var += 1
            if line[5] not in variables:
                variables[line[5]] = next_var
                next_var += 1
        if op == "halfplus": #(op1, "halfplus", op2, op3, op4) where op1 = op2+op3 and op4 is carryout
            if line[0] not in variables:
                variables[line[0]] = next_var
                next_var += 1
            if line[2] not in variables:
                variables[line[2]] = next_var
                next_var += 1
            if line[3] not in variables:
                variables[line[3]] = next_var
                next_var += 1
            if line[4] not in variables:
                variables[line[4]] = next_var
                next_var += 1

    #implement circuit operations

    for line in circuit:
        op = line[1]
        if op == "plus": #(op1, "plus", op2, op3, op4, op5) where op1 = op2+op3+op4 and op5 is carryout
            cnf_formula.append( (-variables[line[0]], variables[line[2]], variables[line[3]], variables[line[4]]) )
            cnf_formula.append( (-variables[line[0]], -variables[line[2]], -variables[line[3]], variables[line[4]]) )
            cnf_formula.append( (-variables[line[0]], -variables[line[2]], variables[line[3]], -variables[line[4]]) )
            cnf_formula.append( (-variables[line[0]], variables[line[2]], -variables[line[3]], -variables[line[4]]) )

            cnf_formula.append( (variables[line[0]], -variables[line[2]], -variables[line[3]], -variables[line[4]]) )
            cnf_formula.append( (variables[line[0]], variables[line[2]], variables[line[3]], -variables[line[4]]) )
            cnf_formula.append( (variables[line[0]], variables[line[2]], -variables[line[3]], variables[line[4]]) )
            cnf_formula.append( (variables[line[0]], -variables[line[2]], variables[line[3]], variables[line[4]]) )

            cnf_formula.append( (-variables[line[2]], -variables[line[3]], variables[line[5]]) )
            cnf_formula.append( (-variables[line[2]], -variables[line[4]], variables[line[5]]) )
            cnf_formula.append( (-variables[line[3]], -variables[line[4]], variables[line[5]]) )

            cnf_formula.append( (variables[line[2]], variables[line[3]], -variables[line[5]]) )
            cnf_formula.append( (variables[line[2]], variables[line[4]], -variables[line[5]]) )
            cnf_formula.append( (variables[line[3]], variables[line[4]], -variables[line[5]]) )
        if op == "halfplus": #(op1, "plus", op2, op3, op4) where op1 = op2+op3 and op4 is carryout
            cnf_formula.append( (-variables[line[0]], variables[line[2]], variables[line[3]]) )
            cnf_formula.append( (-variables[line[0]], -variables[line[2]], -variables[line[3]]) )
            cnf_formula.append( (variables[line[0]], variables[line[2]], -variables[line[3]]) )
            cnf_formula.append( (variables[line[0]], -variables[line[2]], variables[line[3]]) )

            cnf_formula.append( (-variables[line[2]], -variables[line[3]], variables[line[4]]) )
            cnf_formula.append( (variables[line[2]], variables[line[3]], -variables[line[4]]) )
            cnf_formula.append( (variables[line[2]], -variables[line[4]]) )
            cnf_formula.append( (variables[line[3]], -variables[line[4]]) )

    for line in circuit:
        op = line[1]
        if op == "xor": #(op1, "xor", op2, op3) where op1 = op2 xor op3
            not_a = next_var
            variables["dummy" + str(not_a) + "not_a"] = not_a
            next_var += 1
            circuit.append( ("dummy" + str(not_a) + "not_a", "not", line[2]) )
            not_b = next_var
            variables["dummy" + str(not_b) + "not_b"] = not_b
            circuit.append( ("dummy" + str(not_b) + "not_b", "not", line[3],) )
            next_var += 1
            and1 = next_var
            variables["dummy" + str(and1) + "and1"] = and1
            circuit.append( ("dummy" + str(and1) + "and1", "and", line[2], "dummy" + str(not_b) + "not_b" ) )
            next_var += 1
            and2 = next_var
            variables["dummy" + str(and2) + "and2"] = and2
            circuit.append( ("dummy" + str(and2) + "and2", "and", line[3], "dummy" + str(not_a) + "not_a") )
            next_var += 1
            circuit.append( (line[0], "or", "dummy" + str(and1) + "and1", "dummy" + str(and2) + "and2") )

    for line in circuit:
        op = line[1]
        if op == "equal": #(op1, "equal", op2)
            # x = a iff
            # (x or -a) AND (-x or a)
            cnf_formula.append( (variables[line[0]], -variables[line[2]]) )
            cnf_formula.append( (-variables[line[0]], variables[line[2]]) )
        if op == "not": #(op1, "not", op2) op1 = not op2
            # x = -a iff
            # (x or a) AND (-x or -a)
            cnf_formula.append( (variables[line[0]], variables[line[2]]) )
            cnf_formula.append( (-variables[line[0]], -variables[line[2]]) )
        if op == "and": #(op1, "and", op2, op3)
            #add in dummy_variable = (dummy_variable-1) AND v
            # x = a AND B iff
            # (x or -a or -b) AND (-x or a) AND (-x or b)
            cnf_formula.append( (variables[line[0]], -variables[line[2]], -variables[line[3]]) )
            cnf_formula.append( (-variables[line[0]], variables[line[2]]) )
            cnf_formula.append( (-variables[line[0]], variables[line[3]]) )
        if op == "or": #(op1, "or", op2, op3)
            #add in dummy_variable = (dummy_variable-1) AND v
            # x = a OR B iff
            # (-x or a or b) AND (x or -a) AND (x or -b)
            cnf_formula.append( (-variables[line[0]], variables[line[2]], variables[line[3]]) )
            cnf_formula.append( (variables[line[0]], -variables[line[2]]) )
            cnf_formula.append( (variables[line[0]], -variables[line[3]]) )

    return cnf_formula,variables
