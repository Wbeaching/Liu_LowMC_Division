import itertools
import numpy as np
import time

from linear_layer import sub_mtx_rownum

row_num1 = [
    [1, 6, 7, 8, 9, 13, 14],
    [0, 3, 6, 7, 8],
    [0, 2, 4, 9, 13, 14, 15],
    [0, 5, 6, 7, 14, 15],
    [0, 10],
    [2, 7, 11, 14],
]

time_start = time.time()
m = itertools.product(*row_num1)
index = 0
for i in m:
    # print(type(i))
    if len(i) == len(set(i)):
        index += 1
        t = np.linalg.matrix_rank(sub_mtx_rownum(matrix, i))
        print("index %i = %i" % (index, t))
time_end = time.time()
print(index)
print("Time1 used = " + str(time_end - time_start) + " Seconds")
print(m)


