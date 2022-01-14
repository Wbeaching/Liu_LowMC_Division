def constraint_and(u, v, t):
    """
    Generate constraints by and operation.
    u and v -----> t
    """
    enq_copy = []
    for i in range(0, len(t)):
        temp_u = u[i]
        temp_v = v[i]
        temp_t = t[i]
        if 'zero' == temp_u or 'zero' == temp_v:
            temp = temp_u if 'zero' == temp_v else temp_v
            enq_copy.append(temp_t + " - " + temp + " = " + str(0))
        else:
            enq_copy.append(temp_t + " - " + temp_u + " >= " + str(0))
            # enq_copy.append("\n")
            enq_copy.append((temp_t + " - " + temp_v + " >= " + str(0)))
            # enq_copy.append("\n")
            enq_copy.append((temp_t + " - " + temp_u + " - " + temp_v + " <= " + str(0)))
        # enq_copy.append("\n")
    return enq_copy

def constraint_and_1(u, v, t):
    """
    Generate constraints by and operation.
    u and v -----> t
    """
    enq_copy = []
    enq_copy.append(t + " - " + u + " >= " + str(0))
    enq_copy.append((t + " - " + v + " >= " + str(0)))
    enq_copy.append((t + " - " + u + " - " + v + " <= " + str(0)))
    return enq_copy


def constraint_xor3(file_model, s, t, w, x_out):
    """
    Generate the constraints by Xor operation.
    s xor t xor w = x_out
    xout - s - t - w = 0
    """
    file_obj = open(file_model, "a")
    for i in range(0, len(x_out)):
        eqn = [x_out[i], s[i], t[i], w[i]]
        temp = " - ".join(eqn)
        temp = temp + " = " + str(0)
        file_obj.write(temp)
        file_obj.write("\n")
    file_obj.close()


def constraint_xor2(file_model, s, t, x_out):
    """
    Generate the constraints by Xor operation.
    s xor t = x_out
    xout - s - t = 0
    """
    file_obj = open(file_model, "a")
    for i in range(0, len(x_out)):
        eqn = [x_out[i], s[i], t[i]]
        temp = " - ".join(eqn)
        temp = temp + " = " + str(0)
        file_obj.write(temp)
        file_obj.write("\n")
    file_obj.close()


def constraint_copy2(file_model, x, s, t):
    """
    Generate the constraints by Copy operation.
    x -- (s,t)
    """
    file_obj = open(file_model, "a")
    for i in range(0, len(x)):
        eqn = [x[i], s[i], t[i]]
        temp = " - ".join(eqn)
        temp = temp + " = " + str(0)
        file_obj.write(temp)
        file_obj.write("\n")
    file_obj.close()


def constraint_copy_n(x, y):
    """
    Generate the constraints by Copy operation.
    y=[y1, y2, ...yn]
    x -- y
    """
    x_y = [x] + y
    eqn = " - ".join(x_y)
    eqn += " = " + str(0)
    return eqn


def read_file(file_name_):
    """
    Read the linear inequalites from filename to a list
    """
    file_obj = open(file_name_, "r")
    ine = []
    for i in file_obj:
        ine.append(list(map(int, (i.strip()).split())))
    file_obj.close()
    return ine


def clean_data(file_name):
    anf = open(file_name, "r")
    ANF_xi = []
    anf_str = ''
    for i in anf:
        anf_str += i.strip()

    ANF_yi_str = anf_str.lstrip('[').rstrip(']').replace('$.', 'x').split(',')
    for yi_str in ANF_yi_str:
        yi_list_m = yi_str.strip().split('+')
        yi_list = []
        for x_and_x in yi_list_m:
            yi_list.append(x_and_x.strip().split('*'))
        ANF_xi.append(yi_list)
    return ANF_xi


if __name__ == '__main__':
    file_name = 'ANF_of_x3.txt'
    ANF_xi = clean_data(file_name)
    print(ANF_xi)
