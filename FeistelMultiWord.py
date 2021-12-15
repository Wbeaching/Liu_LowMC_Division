import gurobipy as gp
import time


class FeistelMultiWord:
    # constant parameters

    def __init__(self, n, r, file_model, file_result):
        # word_num = 4
        self.word_num = n
        self.rounds = r
        self.file_model = file_model
        self.file_result = file_result

    def create_state_var(self, x, r, group, num):
        # return [x_r_0, x_r_1, x_r_2, ....]
        state = []
        for iByte in range(num):
            state.append(x + '_%i' % r + '_%i' % group + '_%i' % iByte)
        return state

    def create_target_fn(self):
        """
        Create Objective function of the MILP model.
        Minimize
        """

        file_obj = open(self.file_model, "w+")
        file_obj.write("Minimize\n")
        # group = 0
        output_var = []
        for group in range(4):
            output_var = output_var + self.create_state_var('x', self.rounds, group, self.word_num)
        file_obj.write(' + '.join(output_var) + '\n')
        file_obj.close()

    def input_init(self, inputDP):
        """
        Generate constraints by the initial division property.
        """

        in_vars = []
        for group in range(4):
            in_vars = in_vars + self.create_state_var('x', 0, group, self.word_num)
        constraints = ['%s = %s' % (a, b) for a, b in zip(in_vars, inputDP)]
        file_obj = open(self.file_model, "a")
        file_obj.write('Subject To\n')
        for enq in constraints:
            file_obj.write(enq + '\n')
        file_obj.close()

    def create_round_fn(self):

        # x1 + x2 * x3 + x4 + c

        for i in range(self.rounds):
            # copy x_i_1--
            group = 0
            in_0 = self.create_state_var('x', i, group, 4)
            out_3 = self.create_state_var('x', i + 1, 3, 4)
            mid_f_0 = self.create_state_var('f', i, group, 4)
            mid_a_0 = self.create_state_var('a', i, group, 9)
            mid_b_0 = self.create_state_var('b', i, group, 9)
            mid_c_0 = self.create_state_var('c', i, group, 9)
            mid_d_0 = self.create_state_var('d', i, group, 9)

            # x_i_0 copy ---->(f, x_i+1_3)
            self.constraint_copy(in_0, mid_f_0, out_3)
            # f(f) --->d
            self.constraints_fi(mid_f_0, mid_a_0)
            self.constraints_fi(mid_a_0, mid_b_0)
            self.constraints_fi(mid_b_0, mid_c_0)
            self.constraints_fi(mid_c_0, mid_d_0)

            group = 1
            in_1 = self.create_state_var('x', i, group, 4)
            out_0 = self.create_state_var('x', i + 1, 0, 4)
            self.constraint_xor(in_1, mid_d_0[:4], out_0)

            group = 2
            in_2 = self.create_state_var('x', i, group, 4)
            out_1 = self.create_state_var('x', i + 1, 1, 4)
            mid_f_2 = self.create_state_var('f', i, group, 4)
            mid_a_2 = self.create_state_var('a', i, group, 9)
            mid_b_2 = self.create_state_var('b', i, group, 9)
            mid_c_2 = self.create_state_var('c', i, group, 9)
            mid_d_2 = self.create_state_var('d', i, group, 9)

            # x_i_0 copy ---->(f, x_i+1_3)
            self.constraint_copy(in_2, mid_f_2, out_1)
            # f(f) --->d
            self.constraints_fi(mid_f_2, mid_a_2)
            self.constraints_fi(mid_a_2, mid_b_2)
            self.constraints_fi(mid_b_2, mid_c_2)
            self.constraints_fi(mid_c_2, mid_d_2)

            group = 3
            in_3 = self.create_state_var('x', i, group, 4)
            out_2 = self.create_state_var('x', i + 1, 2, 4)
            self.constraint_xor(in_3, mid_d_2[:4], out_2)

    def constraint_xor(self, s, t, x_out):
        """
        Generate the constraints by Xor operation.
        s xor t xor w = x_out
        xout - s - t - w = 0
        """
        file_obj = open(self.file_model, "a")
        for i in range(0, len(x_out)):
            eqn = []
            eqn.append(x_out[i])
            eqn.append(s[i])
            eqn.append(t[i])
            temp = " - ".join(eqn)
            temp = temp + " = " + str(0)
            file_obj.write(temp)
            file_obj.write("\n")
        file_obj.close()

    def constraint_copy(self, x, s, t):
        """
        Generate the constraints by Copy operation.
        x -- (s,t)
        """
        file_obj = open(self.file_model, "a")
        for i in range(0, len(x)):
            eqn = []
            eqn.append(x[i])
            eqn.append(s[i])
            eqn.append(t[i])
            temp = " - ".join(eqn)
            temp = temp + " = " + str(0)
            file_obj.write(temp)
            file_obj.write("\n")
        file_obj.close()

    def constraints_fi(self, x, a):
        """
        Generate the constraints by sbox layer.
        """
        # copy
        ineq = []
        ineq.append(str(x[1]) + " - " + str(a[0]) + " - " + str(a[4]) + " = 0\n")
        ineq.append(str(x[2]) + " - " + str(a[1]) + " - " + str(a[5]) + " = 0\n")
        ineq.append(str(x[3]) + " - " + str(a[2]) + " - " + str(a[6]) + " = 0\n")
        ineq.append(str(a[7]) + " - " + str(a[4]) + " - " + str(a[5]) + " = 0\n")
        ineq.append(str(a[7]) + " - 2 " + str(a[8]) + " <= 0\n")
        ineq.append(str(a[7]) + " - 2 " + str(a[8]) + " >= -1\n")
        ineq.append(str(a[3]) + " - " + str(a[6]) + " - " + str(a[8]) + " - " + str(x[0]) + " = 0\n")
        ineq.append(str(a[3]) + " <= 8\n")

        file_obj = open(self.file_model, "a")
        for i in ineq:
            file_obj.write(i)
        file_obj.close()

    def create_general(self):
        """
        Specify variable type.
        by default, each variable has a lower bound of 0 and an infinite upper bound.
        """
        file_obj = open(self.file_model, "a")
        file_obj.write("general\n")
        for i in range(0, self.rounds):
            for group in range(4):
                for j in self.create_state_var('x', i, group, 4):
                    file_obj.write(j)
                    file_obj.write("\n")
            for group in [0, 2]:
                for j in self.create_state_var('f', i, group, 9):
                    file_obj.write(j)
                    file_obj.write("\n")
                for j in self.create_state_var('a', i, group, 9):
                    file_obj.write(j)
                    file_obj.write("\n")
                for j in self.create_state_var('b', i, group, 9):
                    file_obj.write(j)
                    file_obj.write("\n")
                for j in self.create_state_var('c', i, group, 9):
                    file_obj.write(j)
                    file_obj.write("\n")
                for j in self.create_state_var('d', i, group, 9):
                    file_obj.write(j)
                    file_obj.write("\n")
        for group in range(4):
            for j in self.create_state_var('x', self.rounds, group, 4):
                file_obj.write(j)
                file_obj.write("\n")
        file_obj.write("END")
        file_obj.close()

    def create_model(self, inputDP):
        self.create_target_fn()
        self.input_init(inputDP)
        self.create_round_fn()
        self.create_general()

    def solve_model(self):
        """
        Solve the MILP model to search the integral distinguisher.
        """
        time_start = time.time()
        m = gp.read(self.file_model)
        counter = 0
        set_zero = []
        MILP_trials = []
        global_flag = False
        while counter < self.word_num * 4:
            m.optimize()
            # Gurobi syntax: m.Status == 2 represents the model is feasible.
            if m.Status == 2:
                all_vars = m.getVars()
                MILP_trial = []
                for v in all_vars:
                    name = v.getAttr('VarName')
                    valu = v.getAttr('x')
                    MILP_trial.append(name + ' = ' + str(valu))
                MILP_trials.append(MILP_trial)
                obj = m.getObjective()
                if obj.getValue() > 1:
                    global_flag = True
                    break

                else:
                    fileobj = open(self.file_result, "a")
                    fileobj.write("************************************COUNTER = %d\n" % counter)
                    fileobj.close()
                    self.write_obj(obj)
                    for i in range(0, self.word_num * 4):
                        u = obj.getVar(i)
                        temp = u.getAttr('x')
                        if temp == 1:
                            set_zero.append(u.getAttr('VarName'))
                            u.ub = 0
                            m.update()
                            counter += 1
                            break
            # Gurobi syntax: m.Status == 3 represents the model is infeasible.
            elif m.Status == 3:
                global_flag = True
                break
            else:
                print("Unknown error!")

        fileobj = open(self.file_result, "a")
        if global_flag:
            fileobj.write("\nIntegral Distinguisher Found!\n\n")
            print("Integral Distinguisher Found!\n")
        else:
            fileobj.write("\nIntegral Distinguisher do NOT exist\n\n")
            print("Integral Distinguisher do NOT exist\n")

        fileobj.write("Those are the coordinates set to zero: \n")
        for u in set_zero:
            fileobj.write(u)
            fileobj.write("\n")
        fileobj.write("The division trials is : \n")
        for index, Mi in enumerate(MILP_trials):
            fileobj.write("The division trials [%i] :\n" % index)
            for v in Mi:
                fileobj.write(v + '\n')
            # fileobj.write("\n")
        fileobj.write("\n")
        time_end = time.time()
        fileobj.write(("Time used = " + str(time_end - time_start)))
        fileobj.close()

    def write_obj(self, obj):
        """
        Write the objective value into file_result.
        """
        file_obj = open(self.file_result, "a")
        file_obj.write("The objective value = %d\n" % obj.getValue())
        eqn1 = []
        eqn2 = []
        for i in range(0, self.word_num * 4):
            u = obj.getVar(i)
            if u.getAttr("x") != 0:
                eqn1.append(u.getAttr('VarName'))
                eqn2.append(u.getAttr('x'))
        length = len(eqn1)
        for i in range(0, length):
            s = eqn1[i] + "=" + str(eqn2[i])
            file_obj.write(s)
            file_obj.write("\n")
        file_obj.close()


if __name__ == "__main__":
    # block size = 16*8 = 128
    word_num = 16
    input_DP = [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7]
    # fn_word_num = word_num / 4
    fn_word_num = 4
    round_num = 9
    activebits = 1
    file_model = 'Feistel_Word%i_%i_model.lp' % (round_num, activebits)
    file_result = "Feistel_Word%i_%i_result.txt" % (round_num, activebits)
    file_obj = open(file_result, "w+")
    file_obj.close()
    lm = FeistelMultiWord(fn_word_num, round_num, file_model, file_result)
    # 最左边为最低位
    lm.create_model(input_DP)
    lm.solve_model()
