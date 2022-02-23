from sage.crypto.boolean_function import BooleanFunction
import sys
import time
from sbox.process_sbox import Sbox
from sbox.reducelin import Reduce
import sage
import time

def createDivisionTrails(cipher_name, sbox):
    time_start = time.time()
    present = Sbox(sbox)
    filename = cipher_name + "_DivisionTrails.txt"
    present.PrintfDivisionTrails(filename)
    time_end = time.time()
    print("Time used = " + str(time_end - time_start) + " Seconds")


def ReadIne(filename):
    """
    Read the linear inequalites from filename to a list
    """
    fileobj = open(filename, "r")
    ine = []
    for i in fileobj:
        ine.append(list(map(int, (i.strip()).split())))
    fileobj.close()
    return ine


def simplify_ine(cipher):
    """
    Reshape the linear inequalites from file to a new file
    """
    filename = cipher + "_Inequalities.txt"
    fileobj = open(filename, "r")
    simpfilename = cipher + "_Simplified_Inequalities.txt"
    simfileobj = open(simpfilename, "w")
    for i in fileobj:
        # if(i!= "\n"):
        temp = str(i)[15:-6].replace(",", "").replace(") x +", "")
        simfileobj.write(temp + "\n")
    fileobj.close()
    simfileobj.close()
    return simpfilename




def SBOX_ANF(SBOX):
    """
    Given a list SBOX of 2^n value
    return (P, y) where
    y is a list of n ANF for each output coordinate
    P is a common BooleanPolynomialRing for all element of y
    !!Has a memory leak, use custom_ANF if this is a problem
    """

    # size of the sbox
    n = max([x.nbits() for x in SBOX])

    # Get the bit representation of each value
    SBOX_bits = [x.bits() + [0 for i in range(n - len(x.bits()))] for x in SBOX]
    # print("SBOX_bits:")
    # print(SBOX_bits)
    # Create the boolean function corresponding to each bit of the output from its truth table
    # i.e. all bits of index i in SBOX-table for the i-th output bit
    B = [BooleanFunction([x[i] for x in SBOX_bits]) for i in range(n)]
    # print("B:-----------")
    print(B)

    # Set a common BooleanPolynomialRing for each output function
    y0 = B[0].algebraic_normal_form()
    # print("y0:-----------")
    # print(y0)
    P = y0.ring()

    # Compute the ANF of each output bit
    y = [P(b.algebraic_normal_form()) for b in B]

    return (P, y)


def SboxDivTrailTable(y):
    """
    Return a dict containing all possible division propagation of the SBOX, where y is a list containing the ANF of each output bits
    """

    P = y[0].ring()
    n = P.n_variables()

    D = dict()
    # print("--------------[SboxDivTrailTable]:D-----------")
    # print(D)

    for c in range(2 ^ n):
        k = Integer(c).bits() + [0 for i in range(n - Integer(c).nbits())]
        k = tuple(k)
        # print("----k=:" + str(k))
        D[k] = SboxDivTrail(y, k)

    return D


def SboxDivTrail(y, k):
    """
    input :
    - y list of BooleanPolynomial representing the output ANF of the SBox
    - k the input division property
    output :
     K the set of output division property
    """
    n = len(k)
    P = y[0].ring()
    x = P.gens()

    S = set()
    for e in range(2 ^ n):
        kbar = Integer(e).bits() + [0 for i in range(n - Integer(e).nbits())]
        if greater(kbar, k):
            S.add(tuple(kbar))

    F = set()
    for kbar in S:
        F.add(P(prod([x[i] for i in range(n) if kbar[i] == 1])))

    Kbar = set()

    for e in range(2 ^ n):
        u = Integer(e).bits() + [0 for i in range(n - Integer(e).nbits())]
        # print("--------------[SboxDivTrail]:1-----------")
        puy = prod([y[i] for i in range(n) if u[i] == 1])
        # print("--------------[SboxDivTrail]:2-----------")
        puyMon = P(puy).monomials()
        # print("--------------[SboxDivTrail]:3-----------")
        contains = False
        for mon in F:
            if mon in puyMon:
                contains = True
                break
        # print("--------------[SboxDivTrail]:4-----------")
        if contains:
            Kbar.add(tuple(u))
    # print("--------------[SboxDivTrail]:5-----------")
    K = []
    for kbar in Kbar:
        great = False
        for kbar2 in Kbar:
            if (kbar != kbar2 and greater(kbar, kbar2)):
                great = True
                break
        if not great:
            K.append(kbar)

    return K


def greater(a, b):
    # return True if a[i] >= b[i] for all i
    # False otherwise
    for i in range(len(a)):
        if a[i] < b[i]:
            return False
    return True




if __name__ == "__main__":

    cipher_name = "sbox_4"
    sbox = [0x2, 0xD, 0x3, 0x9, 0x7, 0xB, 0xA, 0x6, 0xE, 0x0, 0xF, 0x4, 0x8, 0x5, 0x1, 0xC]
    time_start = time.time()
    (P, y) = SBOX_ANF(sbox)
    D = SboxDivTrailTable(y)
    time_end = time.time()
    # print("Time used = " + str(time_end - time_start) + " Seconds")
    # print("------------------------------")
    # print("P:")
    # print(P)
    # print("y:")
    # print(y)
    print("D:")
    print(type(D))
    print(D)

    # 1. sbox to Division Trails
    # createDivisionTrails(cipher_name, sbox)

    # 2. Division Trails to Inequalities
    # filename = cipher_name + "_DivisionTrails.txt"
    # Points = ReadIne(filename)
    # print("Points:")
    # print(type(Points))
    # print(Points)
    # -----------
    Points = []
    for key in D.keys():
        for v in D.get(key):
            Points.append(key + v)
    print("Points:")
    print(type(Points))
    print(Points)
    # ----------------
    triangle = Polyhedron(vertices=Points)
    filename = cipher_name + "_Inequalities.txt"
    fileobj = open(filename, "w")
    for l in triangle.inequality_generator():
        fileobj.write(str(l) + "\n")
    fileobj.close()

    # 3. Inequalities to Simplified Inequalities
    simplifiedFile = simplify_ine(cipher_name)
    present = Reduce(simplifiedFile, sbox)
    rine = present.InequalitySizeReduce()
    filename_result = cipher_name + "_Reduced_Inequalities.txt"
    fileobj = open(filename_result, "w")
    for l in rine:
        fileobj.write(str(l) + "\n")
    fileobj.close()