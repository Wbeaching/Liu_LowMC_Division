import itertools

import numpy as np
import time
from itertools import compress
from lowMC_constant import Matrix128

"""
    生成一个n*n矩阵的所有子矩阵；
        eg：
        輸入[0, 0, 1, 1], 返回后兩列；
        輸出[0, 0, 1, 1], 返回後兩行；
        最后输一个 后两列和后两行组成的2*2的子矩阵
        
    最左边为低位[x0, x1, x2, ..., x126, x127]
"""


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


def sub_mtx_rownum(matrix, row_num):
    submtx = []
    for index in row_num:
        submtx.append(matrix[index])
    return submtx


def linear_layer_division(intemp128, trials):
    sub_col = sub_column(Matrix128, intemp128)
    width = sum(intemp128)
    len_m = len(sub_col)
    trials_set = set(trials)
    m = itertools.combinations(range(len_m), width)
    for i in m:
        if len(i) == len(set(i)):
            t = np.linalg.matrix_rank(sub_mtx_rownum(sub_col, i))
            if t == width:
                trials_set.add(i)
    return sorted(trials_set)


def exchange2vextor(locationlist):
    width = len(Matrix128)
    invec = np.zeros(width, dtype=int)
    for i in locationlist:
        invec[i] = 1
    return invec

def sbox_divisoin(trials):
    trials_s = trials
    for in_loc in trials:
        # (0, 1) (0, 8)
        # trials_next =[]
        if 0 in in_loc :
            tmp = list(in_loc).remove(0)
            if tmp.count(1) > 0:
                tmp = tmp.remove(1)
                if tmp.count(2) == 0:
                    # (0,1) --> 2
                    trials_s.append(sorted(tmp + [2]))
            elif tmp.count(2) > 0:
                # (0,2)  ---> 1
                tmp = tmp.remove(2)
                trials_s.append(sorted(tmp + [1]))
            else:
                # 0 ----> 1, 2
                trials_s.append(sorted(tmp + [1]))
                trials_s.append(sorted(tmp + [2]))
        elif 1 in in_loc:
            tmp = list(in_loc).remove(1)
            if 2 in tmp:
                # (1,2) ----> 0
                tmp = tmp.remove(2)
                trials_s.append(sorted(tmp + [0]))
            else:
                # 1 ----> 0, 2
                trials_s.append(sorted(tmp + [2]))
                trials_s.append(sorted(tmp + [0]))
        elif 2 in in_loc:
            # 2 ----> 0, 1
            tmp = list(in_loc).remove(2)
            trials_s.append(sorted(tmp + [1]))
            trials_s.append(sorted(tmp + [0]))
        else:
            break
    return sorted(trials_s)

if __name__ == '__main__':
    intemp128 = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # intemp64 = [0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1,
    #             1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1]
    # outtemp = [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1]
    # sub_mtx = [Matrix[i][:16] for i in range(16)]
    # matrix16 = [[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1],
    #             [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
    #             [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    #             [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
    #             [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0],
    #             [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1],
    #             [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0],
    #             [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1],
    #             [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0],
    #             [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    #             [0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0],
    #             [0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0],
    #             [1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1],
    #             [0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0],
    #             [1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1]]
    # row_num = {
    #     1: [1, 6, 7, 8, 9, 13, 14],
    #     3: [0, 3, 6, 7, 8],
    #     4: [0, 2, 4, 9, 13, 14, 15],
    #     5: [0, 5, 6, 7, 14, 15],
    #     10: [0, 10],
    #     11: [2, 7, 11, 14]
    # }
    # row_num1 = [
    #     [1, 6, 7, 8, 9, 13, 14],
    #     [0, 3, 6, 7, 8],
    #     [0, 2, 4, 9, 13, 14, 15],
    #     [0, 5, 6, 7, 14, 15],
    #     [0, 10],
    #     [2, 7, 11, 14]
    # ]
    time_start = time.time()
    trials = []
    trials = linear_layer_division(intemp128, trials)

    # sbox
    SBOX_D = {
        # "0": [[0], [1], [2]],
        # "1": [[0], [1], [2]],
        # "2": [[0], [1], [2]],
        # "01": [[0, 1], [2]],
        # "02": [[1], [0, 2]],
        # "12": [[0], [1, 2]],
        # "012": [[0, 1, 2]]
        "0": [[1], [2]],
        "1": [[0], [2]],
        "2": [[0], [1]],
        "01": [[2]],
        "02": [[1]],
        "12": [[0]],
    }
    trials_s = trials
    for in_loc in trials:
        # (0, 1) (0, 8)
        # trials_next =[]
        if 0 in in_loc :
            tmp = list(in_loc).remove(0)
            if tmp.count(1) > 0:
                tmp = tmp.remove(1)
                if tmp.count(2) == 0:
                    # (0,1) --> 2
                    trials_s.append(sorted(tmp + [2]))
            elif tmp.count(2) > 0:
                # (0,2)  ---> 1
                tmp = tmp.remove(2)
                trials_s.append(sorted(tmp + [1]))
            else:
                # 0 ----> 1, 2
                trials_s.append(sorted(tmp + [1]))
                trials_s.append(sorted(tmp + [2]))
        elif 1 in in_loc:
            tmp = list(in_loc).remove(1)
            if 2 in tmp:
                # (1,2) ----> 0
                tmp = tmp.remove(2)
                trials_s.append(sorted(tmp + [0]))
            else:
                # 1 ----> 0, 2
                trials_s.append(sorted(tmp + [2]))
                trials_s.append(sorted(tmp + [0]))
        elif 2 in in_loc:
            # 2 ----> 0, 1
            tmp = list(in_loc).remove(2)
            trials_s.append(sorted(tmp + [1]))
            trials_s.append(sorted(tmp + [0]))
        else:
            break
    time_end = time.time()

    # linear layer
    trials_r = []
    for in_loc in trials:
        in_vex_r = exchange2vextor(in_loc)
        trials_r = linear_layer_division(in_vex_r, trials_r)
    time_end = time.time()
    # print(index)
    # print(trials_r)
    print(len(trials_r))
    print("Time 2 round used = " + str(time_end - time_start) + " Seconds")
