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
