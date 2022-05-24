import json

import sympy
import lowMC_constant
import matrices_and_constants_n256_k80_r11
import matrices_and_constants_n192

def anf(block_size, matrix_r):

    x = sympy.MatrixSymbol('x', block_size, 1)
    y = sympy.Matrix(matrix_r)
    result = y * x
    filename = 'anf_of_linear_m(any)-n_%d.txt' % (block_size)
    # filename = 'anf_of_sbox+linear-m_%i-n_%i.txt' % (m, block_size)
    obj = open(filename, 'w+')
    obj.close()
    for i in result:
        anf_i = str(i).replace('x[', 'x').replace(', 0]', '')
        obj = open(filename, 'a')
        obj.write(anf_i + ',\n')
        obj.close()

file_ANF = 'preprocess/matrices_and_constants_n%d.json' % self.block_size
# 保存了文本，我们在通过load读取出来
with open(file_ANF, 'r', encoding='utf-8') as f:
    data = json.load(f)
matrix_name = 'Linear_layer_%d' % 1
matrix = data[matrix_name]

anf(block_size=192, matrix_r=matrix)
