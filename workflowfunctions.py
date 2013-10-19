def newSolution(codeObject, dimacsfile):
	###
	### accepts dimacs file name as string and appends a new constraint requiring a new solution
	###

	newClause = ''

	### update number of clauses
	lines = open(dimacsfile).readlines()
	lines[0] = 'p cnf ' + lines[0].split()[-2] + ' ' + str(int(lines[0].split()[-1])+1) + '\n'

	f = open(dimacsfile,'w')
	for line in lines:
		f.write(line)
	f.close()

	### write newClause string to append to dimacsilfe
	for i in range(codeObject.M):
		lineIndex = codeObject.variables['a_%d' % i]
		if '-' in linecache.getline('lookup',lineIndex+1):
			newClause += str(lineIndex) + ' '
		else:
			newClause += '-' + str(lineIndex) + ' '
			
		lineIndex = codeObject.variables['b_%d' % i]
		if '-' in linecache.getline('lookup',lineIndex+1):
			newClause += str(lineIndex) + ' '
		else:
			newClause += '-' + str(lineIndex) + ' '
		
		lineIndex = codeObject.variables['c_%d' % i]
		if '-' in linecache.getline('lookup',lineIndex+1):
			newClause += str(lineIndex) + ' '
		else:
			newClause += '-' + str(lineIndex) + ' '

		lineIndex = codeObject.variables['e_%d' % i]
		if '-' in linecache.getline('lookup',lineIndex+1):
			newClause += str(lineIndex) + ' '
		else:
			newClause += '-' + str(lineIndex) + ' '

	### clear linecache and add terminating characters to final clause
	linecache.clearcache()
	newClause += '0\n'

	### append newClause
	f = open(dimacsfile, 'a')
	f.write(newClause)
	f.close()


def output(codeObject):
	###------------------------
	### 	* create output file
	### 	* write code information to file
	###		* write 
	###------------------------

	f = open("n%dk%dL%d_%d"%(codeObject.N,codeObject.K,codeObject.logicalOpIndex,i),"w")
	f.write("--------------------\n")
	f.write(codeObject.codeInfo + "\n")
	if codeObject.logicalOpIndex < codeObject.K:
		f.write("measuring logical X%d" % codeObject.logicalOpIndex + "\n")
	else:
		f.write("measuring logical Z%d" % (codeObject.logicalOpIndex - codeObject.K) + "\n")

	call(["/opt/local/bin/minisat",dimacsfile,"output"])
	call('cat output | tr " " "\n" > lookup',shell=True)
	codeObject.getValues('lookup')
	codeObject.propogate()
	codeObject.determineHBasis()
	f.write("--------------------\n")
	f.write("L:\n")
	f.write(str(codeObject.L) + "\n")
	f.write("lowest weight L:\n")
	f.write(str(codeObject.lowL) + "\n")
	f.write("support:\n")
	f.write(str(codeObject.Lsupport) + "\n")
	f.write("truncated L:\n")
	f.write(str(codeObject.truncatedL) + "\n")
	f.write("B:\n")
	f.write(str(codeObject.B) + "\n")
	f.write("La:\n")
	f.write(str(codeObject.La) + "\n")
	f.write("B*La:\n")
	f.write(str(np.dot(codeObject.B,codeObject.La)) + "\n")
	f.write("satisfying L:\n")
	f.write(str(codeObject.Lsat) + "\n")
	f.write("--------------------\n")

	f.write("Ancilla code stabilizer generators:\n")
	for basisVector in codeObject.hBasis[0:codeObject.M-1]:
		temp = ''
		for i in range(codeObject.M):
			if basisVector[i] and not basisVector[i+codeObject.M]:
				temp += "X"
			elif not basisVector[i] and basisVector[i+codeObject.M]:
				temp += "Z"
			elif basisVector[i] and basisVector[i+codeObject.M]:
				temp += "Y"
			else:
				temp += "I"

		f.write(temp + "\n")
		# print basisVector

	f.write("\na:")
	f.write(str(codeObject.a))
	f.write("\nb:")
	f.write(str(codeObject.b))
	f.write("\nc:")
	f.write(str(codeObject.c))
	f.write("\ne:")
	f.write(str(codeObject.e) + "\n")
	f.write("--------------------\n")
	f.close()