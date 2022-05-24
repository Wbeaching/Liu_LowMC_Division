import time

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


cipher_name = "LowMC_sbox"
filename = cipher_name + "_DivisionTrails.txt"
Points = ReadIne(filename)
print(Points)

time_start = time.time()
triangle = Polyhedron(vertices=Points)
filename = cipher_name + "_Inequalities.txt"
fileobj = open(filename, "w")

for l in triangle.inequality_generator():
    fileobj.write(str(l) + "\n")
fileobj.close()

time_end = time.time()
print("Time used = " + str(time_end - time_start) + " Seconds")