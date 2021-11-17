import numpy as np
from time import *
from itertools import compress
from lowMC_constant import Matrix

"""
    生成一个n*n矩阵的所有子矩阵；
        eg：
        輸入[0, 0, 1, 1], 返回后兩列；
        輸出[0, 0, 1, 1], 返回後兩行；
        最后输一个 后两列和后两行组成的2*2的子矩阵
"""

matrix = [[1, 0, 0, 0, 0, 0, 0, 0],
          [1, 1, 0, 0, 1, 0, 0, 0],
          [0, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 0, 0, 0],
          [0, 1, 0, 0, 1, 1, 0, 0],
          [1, 1, 0, 0, 0, 0, 1, 0],
          [0, 0, 1, 1, 0, 0, 0, 1]]


def sub_column(matrix, inV):
    # 輸入[0, 0, 1, 1], 返回后兩列；
    return [list(compress(row, inV)) for row in matrix]


def sub_row(matrix, outV):
    # 輸出[0, 0, 1, 1], 返回後兩行；
    return [list(row) for row, out_value in zip(matrix, outV) if out_value == 1]


def binArray(num, length):
    return list(map(int, list(bin(num)[2:].zfill(length))))
    """ 
        Return the binary representation of an integer.
        >>> bin(2796202)
            '0b1010101010101010101010'
    """


def create_submtx(matrix, inV, outV):
    return [list(compress(row, inV)) for row, v_item in zip(matrix, outV) if v_item == 1]


if __name__ == '__main__':
    subm = [[1, 0, 0, 0, 0],
            [1, 1, 0, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 1, 0, 0, 1],
            [1, 1, 0, 0, 0],
            [0, 0, 1, 1, 0]]
    intemp = [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1]
    outtemp = [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1]
    # sub_mtx = [Matrix[i][:16] for i in range(16)]
    mtx = [[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1],
               [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
               [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
               [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
               [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0],
               [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1],
               [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0],
               [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0],
               [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1],
               [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0],
               [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
               [0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0],
               [0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0],
               [1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1],
               [0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0],
               [1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1]]
    # print(sub_mtx)
    sub_col = sub_column(mtx, intemp)
    for i in sub_col:
        

    A = [[1, 1, 1, 1, 1, 1],
         [0, 1, 1, 0, 1, 0],
         [0, 0, 0, 1, 1, 0],
         [0, 1, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 1],
         [1, 1, 0, 1, 1, 1]
         ]
    print(np.linalg.matrix_rank(A))

    '''
        0: 
        1: 11
        2: 3 
        3: 
        4:
        5: 4+3
    '''
