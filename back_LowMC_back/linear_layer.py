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


def linear_layer_division(intemp128, trails):
    # intemp128 = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    sub_col = sub_column(Matrix128, intemp128)
    width = sum(intemp128)
    len_m = len(sub_col)
    trails_set = set(trails)
    m = itertools.combinations(range(len_m), width)
    for i in m:
        # if len(i) == len(set(i)):
        t = np.linalg.matrix_rank(sub_mtx_rownum(sub_col, i))
        if t == width:
            trails_set.add(i)
    return sorted(trails_set)


def exchange2vextor(locationlist):
    width = len(Matrix128)
    invec = np.zeros(width, dtype=int)
    for i in locationlist:
        invec[i] = 1
    return invec


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
    "12": [[0]]
}


def sbox_divisoin(trails):
    # only one s-box in s-layer
    trails_s = []
    for in_loc in trails:
        # (0, 1) (0, 8)
        # trails_next =[]
        tmp = list(in_loc)
        if 0 in in_loc:
            if tmp.count(1) > 0:
                if tmp.count(2) > 0:
                    # (0, 1, 2, x) --> (0, 1, 2, x)
                    trails_s.append(tuple(tmp))
                else:
                    # (0, 1, x) --> (2, x)
                    tmp.remove(0)
                    tmp.remove(1)
                    trails_s.append(tuple(sorted(tmp + [2])))
            elif tmp.count(2) > 0:
                # (0, 2, x)  ---> (1, x)
                tmp.remove(0)
                tmp.remove(2)
                trails_s.append(tuple(sorted(tmp + [1])))
            else:
                # 0 ----> 1, 2
                tmp.remove(0)
                trails_s.append(tuple(sorted(tmp + [1])))
                trails_s.append(tuple(sorted(tmp + [2])))
        elif 1 in in_loc:
            if tmp.count(2) > 0:
                # (1,2,x) ----> (0,x)
                tmp.remove(1)
                tmp.remove(2)
                trails_s.append(tuple(sorted(tmp + [0])))
            else:
                # 1 ----> 0, 2
                tmp.remove(1)
                trails_s.append(tuple(sorted(tmp + [0])))
                trails_s.append(tuple(sorted(tmp + [2])))
        elif 2 in in_loc:
            # 2 ----> 0, 1
            tmp.remove(2)
            trails_s.append(tuple(sorted(tmp + [1])))
            trails_s.append(tuple(sorted(tmp + [0])))
        else:
            break
    # trialr_r = set(trails)
    return sorted(set(trails + trails_s))


def size_reduce(before):
    # before = [(0,),  (0, 1), (0, 2), (1, 2), (1, 3), (2, 8), (2, 9), (3,),(3, 5)]
    index = 0
    reduced_trails = before.copy()
    len_now = len(reduced_trails)
    while (index < len_now):
        loc_tmp = set(before[index])
        for i in range(index + 1, len_now):
            tmp = before[i]
            if set(tmp) > loc_tmp:
                reduced_trails.remove(tmp)
            else:
                break
        index += 1
        if len(reduced_trails) != len(before):
            before = reduced_trails.copy()
            len_now = len(reduced_trails)
    return reduced_trails


def write_file(filename, r, length, trails, time_used):
    file_obj = open(filename, "a")
    file_obj.write("%i-Round result begin-----------------------------!\n" % r)
    file_obj.write("The length of result is %i\n" % length)
    file_obj.write("Time used = " + time_used + " Seconds\n")
    file_obj.write(str(trails) + "\n")
    file_obj.write("%i-Round result end-----------------------------!\n" % r)
    file_obj.close()


if __name__ == '__main__':

    input_active = [(0, 1, 2)]
    r = 3
    time_start = time.time()
    # 1 round
    # S-Box
    time_start1 = time.time()
    trails = size_reduce(sbox_divisoin(input_active))
    # linear layer
    trails_r = []
    for in_loc in trails:
        in_vex_r = exchange2vextor(in_loc)
        trails_r = linear_layer_division(in_vex_r, trails_r)
    trails_r = size_reduce(trails_r)
    # wtite file
    time_end1 = time.time()
    time_used = str(time_end1 - time_start1)
    filename = 'lowMC_%iround_result_input=%s.txt' % (r, str(input_active))
    file_obj = open(filename, "w+")
    file_obj.close()
    write_file(filename, 1, len(trails_r),  trails_r, time_used)

    # 2- r rounds
    for i in range(2, r+1):
        time_starti = time.time()

        trails = size_reduce(sbox_divisoin(trails_r))
        trails_r = []
        for in_loc in trails:
            in_vex_r = exchange2vextor(in_loc)
            trails_r = linear_layer_division(in_vex_r, trails_r)

        trails_r = size_reduce(trails_r)

        time_endi = time.time()
        time_usedi = str(time_endi - time_starti)
        write_file(filename, i, len(trails_r), trails_r, time_usedi)

    time_end = time.time()
    time_used = str(time_end - time_start)
    print(str(r)+ "-Round Time Used = " + time_used + "Second!")
