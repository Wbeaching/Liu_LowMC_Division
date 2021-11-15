sbox = [0x0, 0x1, 0x3, 0x6, 0x7, 0x4, 0x5, 0x2]

# [x0, x1, x2, y0, y1, y2, a] where x -> y
sbox_ineq = [[1, 1, 1, -1, -1, -1, 0],
             [-1, -1, -2, 1, 1, 0, 2],
             [-1, -1, 0, 1, 1, 2, 0],
             [0, -1, -1, 0, -1, 1, 2],
             [-1, 0, -1, -1, 0, 1, 2],
             [0, -1, 0, -1, 1, -1, 2],
             [-1, 0, 0, 1, -1, -1, 2],
             [-1, 0, -1, 1, 2, 1, 0]]
