import json
import os

import sympy

def sbox(n):
    """
    ANF_OF_SBOX = [
        ['x0 + x1*x2'],
        ['x0 + x1 + x0*x2'],
        ['x0 + x1 + x2 + x0*x1']
    ]
    """
    if n % 3 == 0:
        return 'x%i + x%i*x%i' % (n, n + 1, n + 2)
    elif n % 3 == 1:
        return 'x%i + x%i + x%i*x%i' % (n - 1, n, n - 1, n + 1)
    else:
        return 'x%i + x%i + x%i + x%i*x%i' % (n - 2, n - 1, n, n - 2, n - 1)


def anf(block_size, m, matrix_r):
    map_s = {}
    # block_size = 8
    for i in range(m * 3):
        k = 'z' + str(i)
        v = sbox(i)
        map_s[k] = v
        # else:
        #     v = 'x' + str(i)

    print(map_s)
    x = sympy.MatrixSymbol('z', block_size, 1)
    y = sympy.Matrix(matrix_r)
    result = y * x
    filename = 'anf_of_sbox+linear-m_%d-n_%d.txt' % (m, block_size)
    # filename = 'anf_of_sbox+linear-m_%i-n_%i.txt' % (m, block_size)
    obj = open(filename, 'w+')
    obj.close()
    for i in result:
        anf_i = str(i).replace('z[', 'z').replace(', 0]', '')
        print(anf_i)
        list_i = anf_i.replace(' ', '').split('+')
        list_i_temp = list_i.copy()
        for j in list_i:
            if j in map_s.keys():
                list_i_temp.remove(j)
                v = map_s[j].replace(' ', '').split('+')
                for k in v:
                    if k in list_i_temp:
                        list_i_temp.remove(k)
                    else:
                        list_i_temp.append(k)
                # anf_i = anf_i.replace(j, map_s[j])
        anf_i = ' + '.join(list_i_temp).replace('z', 'x')
        obj = open(filename, 'a')
        obj.write(anf_i + ',\n')
        obj.close()

if __name__ == "__main__":
    # 计算每一列的汉明重量
    # matrix_r = np.array(lowMC_constant.Matrix128)
    # column_weight = []
    # for i in range(len((matrix_r))):
    #     column_weight.append((sum(matrix_r[:, i])))
    # print(column_weight)

    # anf(block_size=256, m=49, matrix_r=matrices_and_constants_n256_k80_r11.Linear_layer_1)
    # anf(block_size=8, m=2, matrix_r=lowMC_constant.matrix_8)
    block_size = 256
    file_ANF = 'matrices_and_constants_n%d.json' % block_size
    with open(file_ANF, 'r', encoding='utf-8') as f:
        data = json.load(f)
    matrix_name = 'Linear_layer_%d' % 1
    matrix = data[matrix_name]
    anf(block_size=256, m=63, matrix_r=matrix)