#  create the division trials of LowMC SBox

from sbox import Sbox
import time

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

def createDivisionTrials():
    cipher_example = "LowMC"
    # {0: [0, 0, 0], 1: [0, 0, 1], 2: [0, 1, 1], 3: [1, 1, 0], 4: [1, 1, 1], 5: [1, 0, 0], 6: [1, 0, 1], 7: [0, 1, 0]}
    sbox = [0x0, 0x1, 0x3, 0x6, 0x7, 0x4, 0x5, 0x2]
    time_start = time.time()
    present = Sbox(sbox)
    filename = cipher_example + "_DivisionTrails.txt"
    present.PrintfDivisionTrails(filename)
    time_end = time.time()
    print("Time used = " + str(time_end - time_start) + " Seconds")

if __name__ == "__main__":
    createDivisionTrials()