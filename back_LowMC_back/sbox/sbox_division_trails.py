#  create the division trails of LowMC SBox

from sbox.process_sbox import Sbox
import time
import numpy as np


def SBox(a, b, c):
    x = a ^ (b & c)
    y = a ^ b ^ (a & c)
    z = a ^ b ^ c ^ (a & b)
    return [x, y, z]


'''
i = 0
dict = {}
for a in range(2):
    for b in range(2):
        for c in range(2):
            dict[i]= SBox(a, b, c)
            i += 1

print(dict)
# {0: [0, 0, 0], 1: [0, 0, 1], 2: [0, 1, 1], 3: [1, 1, 0], 4: [1, 1, 1], 5: [1, 0, 0], 6: [1, 0, 1], 7: [0, 1, 0]}\
'''


def createDivisionTrails():
    cipher_example = "test"
    # {0: [0, 0, 0], 1: [0, 0, 1], 2: [0, 1, 1], 3: [1, 1, 0], 4: [1, 1, 1], 5: [1, 0, 0], 6: [1, 0, 1], 7: [0, 1, 0]}
    sbox = [1,3,6,5,2,4,7,0]
    time_start = time.time()
    present = Sbox(sbox)
    filename = cipher_example + "_DivisionTrails.txt"
    present.PrintfDivisionTrails(filename)
    time_end = time.time()
    print("Time used = " + str(time_end - time_start) + " Seconds")


if __name__ == "__main__":
    # ma = [[1, 1, 0, 0],
    #       [0, 1, 1, 0],
    #       [0, 1, 1, 1],
    #       [0, 1, 0, 1]]
    #
    # mart = np.array(ma, dtype=np.int8)
    # for i in range(16):
    #     a = np.array(list(format(i, "0256b")[-4:]),dtype=np.int8)
    #     y = np.dot(mart,a)
    #     y2 = [str(j%2) for j in y]
    #     y16 = hex(int(''.join(y2), 2))
    #     # print(y2)
    #     print(y16)
    #     print(',')
    # createDivisionTrails()

    # cipher_example = "zhangwenying_sbox"
    # filename = cipher_example + "_DivisionTrails.txt"
    # fileobj = open(filename, "r")
    # ine = []
    # for i in fileobj:
    #     ine.append(list(map(str, (i.strip()).split())))
    # fileobj.close()

    # out_trails = {}
    # for i in ine:
    #     input_x = str(hex(int(''.join(i[:4]), 2)))
    #     output = str(hex(int(''.join(i[-4:]), 2)))
    #     if input_x in out_trails:
    #         out_trails[input_x] = out_trails.get(input_x) + [output]
    #     else:
    #         out_trails[input_x] = [output]
    # print(out_trails)

    # trails = {(0, 0, 0, 0): [(0, 0, 0, 0)], (1, 0, 0, 0): [(1, 0, 0, 0), (0, 1, 0, 0)],
    #           (0, 1, 0, 0): [(0, 0, 1, 0), (0, 1, 0, 0)], (1, 1, 0, 0): [(1, 0, 1, 0), (1, 1, 0, 0), (0, 1, 1, 0)],
    #           (0, 0, 1, 0): [(1, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0)],
    #           (1, 0, 1, 0): [(1, 0, 1, 0), (1, 0, 0, 1), (0, 1, 1, 0), (0, 1, 0, 1)],
    #           (0, 1, 1, 0): [(1, 0, 1, 0), (1, 1, 0, 0), (0, 1, 0, 1), (0, 0, 1, 1)],
    #           (1, 1, 1, 0): [(1, 1, 0, 1), (1, 0, 1, 1), (1, 1, 1, 0), (0, 1, 1, 1)], (0, 0, 0, 1): [(0, 0, 0, 1)],
    #           (1, 0, 0, 1): [(1, 0, 0, 1), (0, 1, 0, 1)], (0, 1, 0, 1): [(0, 0, 1, 1), (0, 1, 0, 1)],
    #           (1, 1, 0, 1): [(1, 1, 0, 1), (0, 1, 1, 1), (1, 0, 1, 1)],
    #           (0, 0, 1, 1): [(1, 0, 0, 1), (0, 0, 1, 1), (0, 1, 0, 1)],
    #           (1, 0, 1, 1): [(1, 0, 1, 1), (0, 1, 1, 1)], (0, 1, 1, 1): [(1, 1, 0, 1), (1, 0, 1, 1)],
    #           (1, 1, 1, 1): [(1, 1, 1, 1)]}
    # out_trails = {}
    # for keyi in trails:
    #     input_x = str(hex(int(''.join(list(map(str, keyi))), 2)))
    #     output = []
    #     for v in trails.get(keyi):
    #         output.append(str(hex(int(''.join(list(map(str, v))), 2))))
    #
    #     out_trails[input_x] = output
    #
    # A = sorted(out_trails.items(), key=lambda mydict: mydict[1], reverse=False)
    # print(A)
    createDivisionTrails()