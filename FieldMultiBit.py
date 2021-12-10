import gurobipy as gp
import time


class FieldMultiBit:
    def __init__(self, block_size, round, input_DP, filename_model, filename_result):
        self.block_size = block_size
        self.word_size = int(block_size / 4)
        self.round_num = round
        self.input_dp = input_DP
        self.file_model = filename_model
        self.file_result = filename_result

    ANF_ab = [[['a0', 'b0'], ['a1', 'b7'], ['a2', 'b6'], ['a3', 'b5'], ['a4', 'b4'], ['a5', 'b3'], ['a5', 'b7'],
               ['a6', 'b2'], ['a6', 'b6'], ['a6', 'b7'], ['a7', 'b1'], ['a7', 'b5'], ['a7', 'b6']],
              [['a0', 'b1'], ['a1', 'b0'], ['a1', 'b7'], ['a2', 'b6'], ['a2', 'b7'], ['a3', 'b5'], ['a3', 'b6'],
               ['a4', 'b4'], ['a4', 'b5'], ['a5', 'b3'], ['a5', 'b4'], ['a5', 'b7'], ['a6', 'b2'], ['a6', 'b3'],
               ['a6', 'b6'], ['a7', 'b1'], ['a7', 'b2'], ['a7', 'b5'], ['a7', 'b7']],
              [['a0', 'b2'], ['a1', 'b1'], ['a2', 'b0'], ['a2', 'b7'], ['a3', 'b6'], ['a3', 'b7'], ['a4', 'b5'],
               ['a4', 'b6'], ['a5', 'b4'], ['a5', 'b5'], ['a6', 'b3'], ['a6', 'b4'], ['a6', 'b7'], ['a7', 'b2'],
               ['a7', 'b3'], ['a7', 'b6']],
              [['a0', 'b3'], ['a1', 'b2'], ['a1', 'b7'], ['a2', 'b1'], ['a2', 'b6'], ['a3', 'b0'], ['a3', 'b5'],
               ['a3', 'b7'], ['a4', 'b4'], ['a4', 'b6'], ['a4', 'b7'], ['a5', 'b3'], ['a5', 'b5'], ['a5', 'b6'],
               ['a5', 'b7'], ['a6', 'b2'], ['a6', 'b4'], ['a6', 'b5'], ['a6', 'b6'], ['a6', 'b7'], ['a7', 'b1'],
               ['a7', 'b3'], ['a7', 'b4'], ['a7', 'b5'], ['a7', 'b6'], ['a7', 'b7']],
              [['a0', 'b4'], ['a1', 'b3'], ['a1', 'b7'], ['a2', 'b2'], ['a2', 'b6'], ['a2', 'b7'], ['a3', 'b1'],
               ['a3', 'b5'], ['a3', 'b6'], ['a4', 'b0'], ['a4', 'b4'], ['a4', 'b5'], ['a4', 'b7'], ['a5', 'b3'],
               ['a5', 'b4'], ['a5', 'b6'], ['a6', 'b2'], ['a6', 'b3'], ['a6', 'b5'], ['a7', 'b1'], ['a7', 'b2'],
               ['a7', 'b4'], ['a7', 'b7']],
              [['a0', 'b5'], ['a1', 'b4'], ['a2', 'b3'], ['a2', 'b7'], ['a3', 'b2'], ['a3', 'b6'], ['a3', 'b7'],
               ['a4', 'b1'], ['a4', 'b5'], ['a4', 'b6'], ['a5', 'b0'], ['a5', 'b4'], ['a5', 'b5'], ['a5', 'b7'],
               ['a6', 'b3'], ['a6', 'b4'], ['a6', 'b6'], ['a7', 'b2'], ['a7', 'b3'], ['a7', 'b5']],
              [['a0', 'b6'], ['a1', 'b5'], ['a2', 'b4'], ['a3', 'b3'], ['a3', 'b7'], ['a4', 'b2'], ['a4', 'b6'],
               ['a4', 'b7'], ['a5', 'b1'], ['a5', 'b5'], ['a5', 'b6'], ['a6', 'b0'], ['a6', 'b4'], ['a6', 'b5'],
               ['a6', 'b7'], ['a7', 'b3'], ['a7', 'b4'], ['a7', 'b6']],
              [['a0', 'b7'], ['a1', 'b6'], ['a2', 'b5'], ['a3', 'b4'], ['a4', 'b3'], ['a4', 'b7'], ['a5', 'b2'],
               ['a5', 'b6'], ['a5', 'b7'], ['a6', 'b1'], ['a6', 'b5'], ['a6', 'b6'], ['a7', 'b0'], ['a7', 'b4'],
               ['a7', 'b5'], ['a7', 'b7']]]

    def create_ANF_map_and_indexw(self):
        ANF_map = {}
        index_w = 0
        for wi in self.ANF_ab:
            # [['a0', 'b0'], ['a1', 'b7'], ['a2', 'b6'], ['a3', 'b5'], ['a4', 'b4'], ['a5', 'b3'], ['a5', 'b7'],
            index_w = len(wi) + index_w
            for wij in wi:
                left = wij[0]
                right = wij[1]
                left_n = 0
                right_n = 0
                if left in ANF_map:
                    left_n = ANF_map.get(left) + 1
                if right in ANF_map:
                    right_n = ANF_map.get(right) + 1
                ANF_map[left] = left_n
                ANF_map[right] = right_n
        return ANF_map, index_w

    def create_state_var(self, x, r):
        # return [x_r_0, x_r_1, x_r_2, ....]
        state = []
        for iByte in range(self.block_size):
            state.append(x + '_%i' % r + '_%i' % iByte)
        return state

    def create_target_fn(self):
        """
        Create Objective function of the MILP model.
        Minimize
        """
        file_obj = open(self.file_model, "w+")
        file_obj.write("Minimize\n")
        output_var = self.create_state_var('x', self.round_num)
        file_obj.write(' + '.join(output_var) + '\n')
        file_obj.close()

    def input_init(self, inputDP):
        """
        Generate constraints by the initial division property.
        """
        in_vars = self.create_state_var('x', 0)
        constraints = ['%s = %s' % (a, b) for a, b in zip(in_vars, inputDP)]
        file_obj = open(self.file_model, "a")
        file_obj.write('Subject To\n')
        for enq in constraints:
            file_obj.write(enq + '\n')
        file_obj.close()

    def constraint_and(self, u, v, t):
        """
        Generate constraints by and operation.
        u and v -----> t
        """
        file_obj = open(self.file_model, "a")
        for i in range(0, len(t)):
            file_obj.write((t[i] + " - " + u[i] + " >= " + str(0)))
            file_obj.write("\n")
            file_obj.write((t[i] + " - " + v[i] + " >= " + str(0)))
            file_obj.write("\n")
            file_obj.write((t[i] + " - " + u[i] + " - " + v[i] + " <= " + str(0)))
            file_obj.write("\n")
        file_obj.close()

    def constraint_xor(self, s, t, w, x_out):
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
            eqn.append(w[i])
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

    def create_round_mid_var(self, r):
        mid_num = [8, 11, 14, 17, 20, 24, 27, 30]
        mid_varx = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        min_vary = ['o', 'p', 'q', 'r', 's', 't', 'u', 'v']
        state = []
        for iByte in zip(mid_varx, min_vary, mid_num):
            for i in range(iByte[2]):
                state.append(iByte[0] + '_%i' % r + '_%i' % i)
                state.append(iByte[1] + '_%i' % r + '_%i' % i)
        return state

    def constraint_multi(self, round):
        # z0 * z1 = z3
        # x ---> a[0]
        # mid_num = [8, 11, 14, 17, 20, 24, 27, 30]
        # 0. calculate the num of ai and bi ANF_map = {'ai' : num_of_ai}
        #                                    ANF_ab_round = [[[a0_r_0, a1_r_0,....],[b0_r_0, b7_r_0...]],[[],[]]]
        ANF_map = {}
        ANF_ab_round = []
        for wi in self.ANF_ab:
            # [['a0', 'b0'], ['a1', 'b7'], ['a2', 'b6'], ['a3', 'b5'], ['a4', 'b4'], ['a5', 'b3'], ['a5', 'b7'],
            #  ['a6', 'b2'], ['a6', 'b6'], ['a6', 'b7'], ['a7', 'b1'], ['a7', 'b5'], ['a7', 'b6']],
            vars_ai = []
            vars_bi = []
            for wij in wi:
                left = wij[0]
                right = wij[1]
                left_n = 0
                right_n = 0
                if left in ANF_map:
                    left_n = ANF_map.get(left) + 1
                if right in ANF_map:
                    right_n = ANF_map.get(right) + 1
                ANF_map[left] = left_n
                ANF_map[right] = right_n
                vars_ai.append(left + '_%i' % round + '_%i' % left_n)
                vars_bi.append(right + '_%i' % round + '_%i' % right_n)
            ANF_ab_round.append([vars_ai, vars_bi])

        # 1. write copy in ANF
        mid_varx = ['z' + '_%i' % round + '_%i' % i for i in range(self.word_size)]
        mid_vary = ['z' + '_%i' % round + '_%i' % i for i in range(self.word_size, self.word_size * 2)]
        mid_varz = ['z' + '_%i' % round + '_%i' % i for i in range(self.word_size * 3, self.word_size * 4)]
        mid_all = []
        for i in range(self.word_size):
            ai = 'a' + str(i)
            mid_all.append([ai + '_%i' % round + '_%i' % i for i in range(ANF_map.get(ai) + 1)])
        for i in range(self.word_size):
            bi = 'b' + str(i)
            mid_all.append([bi + '_%i' % round + '_%i' % i for i in range(ANF_map.get(bi) + 1)])
        file_obj = open(self.file_model, "a")
        for ieq in zip(mid_varx + mid_vary, mid_all):
            eqn = [ieq[0]]  # z_r_0
            for i in ieq[1]:
                eqn.append(i)  # a0_r_1
            temp = " - ".join(eqn)
            temp = temp + " = " + str(0)
            file_obj.write(temp)
            file_obj.write("\n")
        file_obj.close()

        # 2. write and in ANF
        index_w = 0
        eqn_z = []
        for wi, zi in zip(ANF_ab_round, mid_varz):
            vars_wi = ['w' + '_%i' % round + '_%i' % i for i in range(index_w, len(wi[0]) + index_w)]
            index_w = len(wi[0]) + index_w
            vars_ai = wi[0]
            vars_bi = wi[1]
            self.constraint_and(vars_ai, vars_bi, vars_wi)
            # zor in each line in ANF
            eqn_zi = [zi]
            for i in vars_wi:
                eqn_zi.append(i)  # w_r_i
            eqn_z.append(" - ".join(eqn_zi) + " = " + str(0))

        # 3. write xor in ANF
        file_obj = open(self.file_model, "a")
        for ieq in eqn_z:
            file_obj.write(ieq)
            file_obj.write("\n")
        file_obj.close()

    def create_round_fn(self):
        # 1/4 rounds
        for i in range(self.round_num):
            x_vars = self.create_state_var('x', i)
            y_vars = self.create_state_var('x', i + 1)
            z_vars = self.create_state_var('z', i)
            # 1. copy
            word_s = self.word_size
            self.constraint_copy(x_vars[word_s:], z_vars[:-word_s], y_vars[:-word_s])
            # 2. z0*z1 = z3
            self.constraint_multi(i)
            # 3. xor
            self.constraint_xor(x_vars[:word_s], z_vars[word_s * 2:word_s * 3], z_vars[-word_s:], y_vars[-word_s:])
            # mid_var = self.create_round_mid_var(0)

    def create_binary(self, ANF_map, index_w):
        """
        Specify variable type.
        """
        file_obj = open(self.file_model, "a")
        file_obj.write("Binary\n")
        for ro in range(0, self.round_num):
            for j in self.create_state_var('x', ro):
                file_obj.write(j)
                file_obj.write("\n")
            for j in self.create_state_var('z', ro):
                file_obj.write(j)
                file_obj.write("\n")
            for k in range(self.word_size):
                ai = 'a' + str(k)
                tmp = [ai + '_%i' % ro + '_%i' % t for t in range(ANF_map.get(ai) + 1)]
                for j in tmp:
                    file_obj.write(j)
                    file_obj.write("\n")
            for k in range(self.word_size):
                bi = 'b' + str(k)
                tmp = [bi + '_%i' % ro + '_%i' % t for t in range(ANF_map.get(bi) + 1)]
                for j in tmp:
                    file_obj.write(j)
                    file_obj.write("\n")
            for k in range(index_w):
                file_obj.write('w' + '_%i' % ro + '_%i' % k)
                file_obj.write("\n")
        for j in self.create_state_var('x', self.round_num):
            file_obj.write(j)
            file_obj.write("\n")
        file_obj.write("END")
        file_obj.close()

    def create_model(self, inputDP):
        self.create_target_fn()
        self.input_init(inputDP)
        self.create_round_fn()
        ANF_map, index_w = self.create_ANF_map_and_indexw()
        self.create_binary(ANF_map, index_w)

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
        while counter < self.block_size:
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
                    file_obj = open(self.file_result, "a")
                    file_obj.write("************************************COUNTER = %d\n" % counter)
                    file_obj.close()
                    self.write_obj(obj)
                    for i in range(0, self.block_size):
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

        file_obj = open(self.file_result, "a")
        if global_flag:
            file_obj.write("\nIntegral Distinguisher Found!\n\n")
            print("Integral Distinguisher Found!\n")
        else:
            file_obj.write("\nIntegral Distinguisher do NOT exist\n\n")
            print("Integral Distinguisher do NOT exist\n")

        file_obj.write("Those are the coordinates set to zero: \n")
        for u in set_zero:
            file_obj.write(u)
            file_obj.write("\n")
        # file_obj.write("The division trials is : \n")
        # for index, Mi in enumerate(MILP_trials):
        #     file_obj.write("The division trials [%i] :\n" % index)
        #     for v in Mi:
        #         file_obj.write(v + '\n')
        #     # file_obj.write("\n")
        # file_obj.write("\n")
        time_end = time.time()
        file_obj.write(("Time used = " + str(time_end - time_start)))
        file_obj.close()

    def write_obj(self, obj):
        """
        Write the objective value into filename_result.
        """
        file_obj = open(self.file_result, "a")
        file_obj.write("The objective value = %d\n" % obj.getValue())
        eqn1 = []
        eqn2 = []
        for i in range(0, self.block_size):
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
    block_size = 32
    input_DP = "01111111111111111111111111111111"
    activebits = 31
    rounds = 19

    filename_model = 'FieldMulti_bit%i_%i_model.lp' % (rounds, activebits)
    filename_result = "FieldMulti_bit%i_%i_result.txt" % (rounds, activebits)
    file_r = open(filename_result, "w+")
    file_r.close()
    fm = FieldMultiBit(block_size, rounds, input_DP, filename_model, filename_result)
    # 最左边为最低位
    # Anf_m, index_w = fm.create_ANF_map_and_indexw()
    fm.create_model(input_DP)
    fm.solve_model()
