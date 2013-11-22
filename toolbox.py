# R. Scout Kingery, 2013
# University of Southern California
# Ming Hsieh Dept. of Electrical Engineering
# Communication Sciences Institiute
#
#
#
# toolbox.py
# toolbox contains all the functions/routines that are needed in various parts of the program.

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

def isSAT(self,minisatOutput):
### checks minisat file and returns True is SAT, Flase otherwise
    f = open(minisatOutput,'r')
    check = f.getline().strip()
    f.close()

    return(check == 'SAT')
