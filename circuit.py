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
