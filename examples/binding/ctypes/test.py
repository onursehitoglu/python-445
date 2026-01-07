
# ctest.c contains following functions in C
# compile as 'gcc -shared -o libctest.so ctest.c' to create libctest.so
# struct Complex add(struct Complex , struct Complex );
# void swap(struct Complex *, struct Complex *);
# double sum(double f[], int n);
# void titlecase(char *);
# int tokenize(char sep, char *str, char t[][20]);
# void mult(double a[][100], double b[][100], double c[][100], int n, int r , int n);
# get the python library. searched in system path, specify full or
# relative path if not in system library

cprototypes = '''
struct Complex { double x; double y; };

struct Complex add(struct Complex c, struct Complex d);
void swap(struct Complex *c, struct Complex *d);
void mult(double a[][100], double b[][100], double c[][100], int m, int r, int n) ;
void titlecase(char *str);
int tokenize(char sep, char *str, char t[][20]);
double sum(double f[], int n);
'''

from ctypes import *

lib = CDLL('./libctest.so')

class Complex(Structure):
	_fields_ = [("x", c_double), ("y", c_double)]

# struct Complex add(struct Complex , struct Complex );
lib.add.restype = Complex
print("1-add\n3.1+4.2j + 1.9+2.8j")
r = lib.add(Complex(3.1, 4.2), Complex(1.9, 2.8))
print('result:',r, r.x, r.y)
a = Complex(3, 4)
b = Complex(2, 7)
# void swap(struct Complex *, struct Complex *);
# send pointers to values to pass by pointer
print('2-swap\n',a.x, a.y, b.x, b.y)
lib.swap(byref(a), byref(b))
print('result:\n',a.x, a.y, b.x, b.y)
# double sum(double f[], int n);
# Array type. You can pass pointers as in C. BE CAREFULL ABOUT STORAGE
# YOU CAN GET A SEGFAULT in PYTHON!!!
print('3-sum\n','C array from',[1,2,1,6,4,2,7,3,1,5])
lib.sum.restype = c_double
lib.sum.argtypes = POINTER(c_double), c_int
myarr = (c_double * 10)( * [1, 2, 1, 6, 4, 2, 7, 3, 1, 5])
print('result:\n',lib.sum(myarr, 10))
# void titlecase(char *);
# c_char_p can be use to 0 terminated C strings. Make sure the storage is sufficient
# use value field to get the content
print('4-titlecase\n','the advantages of script languages over OTHER languages') 
lib.titlecase.argtypes = (c_char_p,)
name = c_char_p(b'the advantages of script languages over OTHER languages')
lib.titlecase(name)
print('result:\n', name.value)

# int tokenize(char sep, char *str, char t[][20]);
# this is slightly tricky t needs to store resulting tokens, so need sufficient storage
print('5-tokenize\n')
lib.tokenize.restype = c_int
tokenstype = (c_char * 20) * 20
lib.tokenize.argtypes = c_char, c_char_p, tokenstype
# create an array for the tokenize result array of 20 strings
res = tokenstype ( )
for i in range(20):
	res[i] = create_string_buffer(20)
n = lib.tokenize(b' ', b'the advantages of script languages over OTHER languages', res)
tokens = [tok.value for tok in res[:n]]
print('result:\n',n,tokens)


# void mult(double a[][100], double b[][100], double c[][100], int n, int r , int n);
a = [[ 1, 2, 3, 4, 5], [11, 12, 13, 14, 15]]
b = [[1, 2], [2, 3],[4, 5], [6, 7],[8,9]]
13

arrtype = (c_double * 100) * 100
# initialize matrix a
matA = arrtype()
i = 0
for row in a:
	matA[i] = (c_double * 100)( * row)
	i += 1
# initialize matrix B
matB = arrtype()
i = 0
for row in b:
	matB[i] = (c_double * 100)( * row)
	i += 1
matC = arrtype()
# multiply
print('6-multiply\n',a, b)
lib.mult.argtypes = arrtype, arrtype, arrtype, c_int, c_int, c_int
lib.mult(matA, matB, matC, 2, 5, 2)
# result
print('result:\n',[[matC[i][j] for i in range(2)] for j in range(2)])
