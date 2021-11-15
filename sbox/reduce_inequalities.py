from sbox.reducelin import Reduce

def simplify_ine(cipher):
    """
    Reshape the linear inequalites from file to a new file
    """
    filename = cipher + "_Inequalities.txt"
    fileobj = open(filename, "r")
    simpfilename = cipher + "_Simplified_Inequalities.txt"
    simfileobj = open(simpfilename, "w")
    ine = []
    for i in fileobj:
        # if(i!= "\n"):
        temp = str(i)[15:-6].replace(",","").replace(") x +","")
        simfileobj.write(temp + "\n")
    fileobj.close()
    simfileobj.close()
    return simpfilename

if __name__ == "__main__":

    cipher = "LowMC_sbox"
    sbox = [0x0, 0x1, 0x3, 0x6, 0x7, 0x4, 0x5, 0x2]
    simplifiedFile = simplify_ine(cipher)

    present = Reduce(simplifiedFile, sbox)

    rine = present.InequalitySizeReduce()

    filename_result = cipher + "_Reduced_Inequalities.txt"

    fileobj = open(filename_result, "w")
    for l in rine:
        fileobj.write(str(l) + "\n")
    fileobj.close()