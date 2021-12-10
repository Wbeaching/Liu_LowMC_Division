
import gurobipy as gp
import time


class FieldMultiWord:
    # constant parameters

    def __init__(self, n, r, filename_model, filename_result):
        # word_num = 4
        self.word_num = n
        self.rounds = r
        self.filename_model = filename_model
        self.filename_result = filename_result

    def create_state_var(self, x, r, num):
        # return [x_r_0, x_r_1, x_r_2, ....]
        state = []
        for iByte in range(num):
            state.append(x + '_%i' % r + '_%i' % iByte)
        return state

    def create_target_fn(self):
        """
        Create Objective function of the MILP model.
        Minimize
        """
        file_obj = open(self.filename_model, "w+")
        file_obj.write("Minimize\n")
        output_var = self.create_state_var('x', self.rounds, self.word_num)
        file_obj.write(' + '.join(output_var) + '\n')
        file_obj.close()

    def input_init(self, inputDP):
        """
        Generate constraints by the initial division property.
        """
        in_vars = self.create_state_var('x', 0, self.word_num)
        constraints = ['%s = %s' % (a, b) for a, b in zip(in_vars, inputDP)]
        file_obj = open(self.filename_model, "a")
        file_obj.write('Subject To\n')
        for enq in constraints:
            file_obj.write(enq + '\n')
        file_obj.close()

    def create_round_fn(self):

        # x1 + x2 * x3 + x4 + c
        for i in range(self.rounds):
            # copy x_i_1--
            in_vars = self.create_state_var('x', i, 4)
            mid_a = self.create_state_var('a', i, 9)
            mid_b = self.create_state_var('b', i, 9)
            mid_c = self.create_state_var('c', i, 9)
            out_vars = self.create_state_var('x', i + 1, 9)

            self.constraints_fi(in_vars, mid_a)
            self.constraints_fi(mid_a, mid_b)
            self.constraints_fi(mid_b, mid_c)
            self.constraints_fi(mid_c, out_vars)

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

        file_obj = open(self.filename_model, "a")
        for i in ineq:
            file_obj.write(i)
        file_obj.close()

    def create_general(self):
        """
        Specify variable type.
        by default, each variable has a lower bound of 0 and an infinite upper bound.
        """
        file_obj = open(self.filename_model, "a")
        file_obj.write("general\n")
        for i in range(0, self.rounds):
            for j in self.create_state_var('x', i, 9):
                file_obj.write(j)
                file_obj.write("\n")
            for j in self.create_state_var('a', i, 9):
                file_obj.write(j)
                file_obj.write("\n")
            for j in self.create_state_var('b', i, 9):
                file_obj.write(j)
                file_obj.write("\n")
            for j in self.create_state_var('c', i, 9):
                file_obj.write(j)
                file_obj.write("\n")
        for j in self.create_state_var('x', self.rounds, 9):
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
        m = gp.read(self.filename_model)
        counter = 0
        set_zero = []
        MILP_trials = []
        global_flag = False
        while counter < self.word_num:
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
                    fileobj = open(self.filename_result, "a")
                    fileobj.write("************************************COUNTER = %d\n" % counter)
                    fileobj.close()
                    self.write_obj(obj)
                    for i in range(0, self.word_num):
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

        fileobj = open(self.filename_result, "a")
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
        Write the objective value into filename_result.
        """
        file_obj = open(self.filename_result, "a")
        file_obj.write("The objective value = %d\n" % obj.getValue())
        eqn1 = []
        eqn2 = []
        for i in range(0, self.word_num):
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
    word_num = 4
    round_num = 4
    input_DP = [8, 8, 8, 7]
    activebits = 1
    filename_model = 'FieldMultibWord%i_%i_model.lp' % (round_num, activebits)
    filename_result = "FieldMultiWord%i_%i_result.txt" % (round_num, activebits)
    file_obj = open(filename_result, "w+")
    file_obj.close()
    lm = FieldMultiWord(word_num, round_num, filename_model, filename_result)
    # 最左边为最低位
    lm.create_model(input_DP)
    lm.solve_model()
