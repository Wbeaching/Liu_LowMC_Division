import gurobipy as gp
import time


class FeistelMultiBit:
    def __init__(self, block_size, round, input_DP, filename_model, filename_result):
        self.block_size = block_size  # 128
        self.grp_block_size = int(block_size / 4)  # 32
        self.word_size = int(self.grp_block_size / 4)  # 8
        self.round_num = round
        self.input_dp = input_DP
        self.file_model = filename_model
        self.file_result = filename_result

    ANF_st = [
        [['s0', 't0'], ['s1', 't3'], ['s2', 't2'], ['s3', 't1']],
        [['s0', 't1'], ['s1', 't0'], ['s1', 't3'], ['s2', 't2'], ['s2', 't3'], ['s3', 't1'], ['s3', 't2']],
        [['s0', 't2'], ['s1', 't1'], ['s2', 't0'], ['s2', 't3'], ['s3', 't2'], ['s3', 't3']],
        [['s0', 't3'], ['s1', 't2'], ['s2', 't1'], ['s3', 't0'], ['s3', 't3']]
    ]

    def create_ANF_map_and_indexw(self):
        ANF_map = {}
        index_w = 0
        for wi in self.ANF_st:
            # [['s0', 'b0'], ['s1', 'b7'], ['s2', 'b6'], ['s3', 'b5'], ['s4', 'b4'], ['s5', 'b3'], ['s5', 'b7'],
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

    def create_state_var(self, x, r, group):
        # return [x_r_0, x_r_1, x_r_2, ....]
        state = []
        start = group * self.grp_block_size
        for iByte in range(start, start + self.grp_block_size):
            state.append(x + '_%i' % r + '_%i' % iByte)
        return state

    def create_target_fn(self):
        """
        Create Objective function of the MILP model.
        Minimize
        """
        file_obj = open(self.file_model, "w+")
        file_obj.write("Minimize\n")
        output_var = []
        for group in range(4):
            output_var += self.create_state_var('x', self.round_num, group)
        file_obj.write(' + '.join(output_var) + '\n')
        file_obj.close()

    def input_init(self, inputDP):
        """
        Generate constraints by the initial division property.
        """
        in_vars = []
        for group in range(4):
            in_vars += self.create_state_var('x', 0, group)
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

    def constraint_xor3(self, s, t, w, x_out):
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

    def constraint_xor2(self, s, t, x_out):
        """
        Generate the constraints by Xor operation.
        s xor t = x_out
        xout - s - t = 0
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

    def constraint_fi(self, round, step, group, z_vars):
        # z0 * z1 = z3
        # x ---> s[0]
        # mid_num = [8, 11, 14, 17, 20, 24, 27, 30]
        # 0. calculate the num of si and ti ANF_map = {'si' : num_of_ai}
        #                                    ANF_st_round = [[[s0_r_0, s1_r_0,....],[t0_r_0, t7_r_0...]],[[],[]]]
        ANF_map = {}
        ANF_st_round = []
        for wi in self.ANF_st:
            # [['s0', 't0'], ['s1', 't7'], ['s2', 't6'], ['s3', 't5'], ['s4', 't4'], ['s5', 't3'], ['s5', 't7'],
            #  ['s6', 't2'], ['s6', 't6'], ['s6', 't7'], ['s7', 't1'], ['s7', 't5'], ['s7', 't6']],
            vars_si = []
            vars_ti = []
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
                vars_si.append('f%i_' % step + 'g%i_' % group + left + '_%i' % round + '_%i' % left_n)
                vars_ti.append('f%i_' % step + 'g%i_' % group + right + '_%i' % round + '_%i' % right_n)
            ANF_st_round.append([vars_si, vars_ti])

        # 1. write copy in ANF
        mid_varx = z_vars[:self.word_size]
        mid_vary = z_vars[self.word_size: self.word_size * 2]
        mid_varz = z_vars[self.word_size * 3:self.word_size * 4]
        mid_all = []
        for i in range(self.word_size):
            si = 's' + str(i)
            mid_all.append(
                ['f%i_' % step + 'g%i_' % group + si + '_%i' % round + '_%i' % i for i in range(ANF_map.get(si) + 1)])
        for i in range(self.word_size):
            ti = 't' + str(i)
            mid_all.append(
                ['f%i_' % step + 'g%i_' % group + ti + '_%i' % round + '_%i' % i for i in range(ANF_map.get(ti) + 1)])
        file_obj = open(self.file_model, "a")
        # file_obj.write('[BEGIN]  Multi in [group_%i], [round_%i], [step_%i]!! [BEGIN]\n' % (round, group, step))
        for ieq in zip(mid_varx + mid_vary, mid_all):
            eqn = [ieq[0]]  # z_r_0
            for i in ieq[1]:
                eqn.append(i)  # s0_r_1
            temp = " - ".join(eqn)
            temp = temp + " = " + str(0)
            file_obj.write(temp)
            file_obj.write("\n")
        file_obj.close()

        # 2. write and in ANF
        index_w = 0
        eqn_z = []
        for wi, zi in zip(ANF_st_round, mid_varz):
            vars_wi = ['f%i_' % step + 'g%i_' % group + 'w' + '_%i' % round + '_%i' % i for i in
                       range(index_w, len(wi[0]) + index_w)]
            index_w = len(wi[0]) + index_w
            vars_si = wi[0]
            vars_ti = wi[1]
            self.constraint_and(vars_si, vars_ti, vars_wi)
            # xor in each line in ANF
            eqn_zi = [zi]
            for i in vars_wi:
                eqn_zi.append(i)  # w_r_i
            eqn_z.append(" - ".join(eqn_zi) + " = " + str(0))

        # 3. write xor in ANF
        file_obj = open(self.file_model, "a")
        for ieq in eqn_z:
            file_obj.write(ieq)
            file_obj.write("\n")

        # file_obj.write('[END] Multi in [group_%i], [round_%i], [step_%i]!! [END]\n' % (round, group, step))
        file_obj.close()

    def create_sbox(self, rnd, step, in_vars, out_vars, group):
        z_vars = self.create_state_var('f%i_' % step + 'z', rnd, group)
        # 1. copy
        word_s = self.word_size
        self.constraint_copy(in_vars[word_s:], z_vars[:-word_s], out_vars[:-word_s])
        # 2. z0*z1 = z3
        # step = 0
        self.constraint_fi(rnd, step, group, z_vars)
        # 3. xor
        self.constraint_xor3(in_vars[:word_s], z_vars[word_s * 2:word_s * 3], z_vars[-word_s:], out_vars[-word_s:])

    def create_round_fn(self):
        # 1/4 rounds
        for rnd in range(self.round_num):
            group = 0
            # copy : x_0_0 -- a_0_0, x_1_4
            xi_vars0 = self.create_state_var('x', rnd, group)
            yi_vars3 = self.create_state_var('x', rnd + 1, group + 3)
            a_vars = self.create_state_var('a', rnd, group)
            self.constraint_copy(xi_vars0, yi_vars3, a_vars)
            # round function = 4 sbox, input = a, output = e
            b_vars = self.create_state_var('b', rnd, group)
            c_vars = self.create_state_var('c', rnd, group)
            d_vars = self.create_state_var('d', rnd, group)
            e_vars = self.create_state_var('e', rnd, group)
            step = 0
            self.create_sbox(rnd, step, a_vars, b_vars, group)
            step = 1
            self.create_sbox(rnd, step, b_vars, c_vars, group)
            step = 2
            self.create_sbox(rnd, step, c_vars, d_vars, group)
            step = 3
            self.create_sbox(rnd, step, d_vars, e_vars, group)

            group = 1
            xi_vars1 = self.create_state_var('x', rnd, group)
            yi_vars0 = self.create_state_var('x', rnd + 1, 0)
            self.constraint_xor2(xi_vars1, e_vars, yi_vars0)

            group = 2
            xi_vars2 = self.create_state_var('x', rnd, group)
            yi_vars1 = self.create_state_var('x', rnd + 1, 1)

            a_vars_2 = self.create_state_var('a', rnd, group)
            self.constraint_copy(xi_vars2, yi_vars1, a_vars_2)
            # fi = 4 sbox
            b_vars_2 = self.create_state_var('b', rnd, group)
            c_vars_2 = self.create_state_var('c', rnd, group)
            d_vars_2 = self.create_state_var('d', rnd, group)
            e_vars_2 = self.create_state_var('e', rnd, group)
            step = 0
            self.create_sbox(rnd, step, a_vars_2, b_vars_2, group)
            step = 1
            self.create_sbox(rnd, step, b_vars_2, c_vars_2, group)
            step = 2
            self.create_sbox(rnd, step, c_vars_2, d_vars_2, group)
            step = 3
            self.create_sbox(rnd, step, d_vars_2, e_vars_2, group)

            group = 3
            xi_vars3 = self.create_state_var('x', rnd, group)
            yi_vars2 = self.create_state_var('x', rnd + 1, 2)
            self.constraint_xor2(xi_vars3, e_vars_2, yi_vars2)

    def create_binary(self, ANF_map, index_w):
        """
        Specify variable type.
        """
        '''
        all = 256 (x = 128, y = 128)
        all0 = 2100
            all = 517 (a = 32 , z = 32, s=8+11+14+17+20+24+27+30=151, t = 151, w = 151,  all = 517)
            all = 517 (b)  
            all = 517 (c)
            all = 549 (d + e32) 
        all2 = 2100
        1 -round vars num = 4328 + 128(output)
        '''
        file_obj = open(self.file_model, "a")
        file_obj.write("\n")
        file_obj.write("binaries\n")
        for ro in range(0, self.round_num):
            for group in range(4):
                for j in self.create_state_var('x', ro, group):
                    file_obj.write(j)
                    file_obj.write("\n")
            for group in [0, 2]:
                for j in self.create_state_var('a', ro, group):
                    file_obj.write(j)
                    file_obj.write("\n")
                for j in self.create_state_var('b', ro, group):
                    file_obj.write(j)
                    file_obj.write("\n")
                for j in self.create_state_var('c', ro, group):
                    file_obj.write(j)
                    file_obj.write("\n")
                for j in self.create_state_var('d', ro, group):
                    file_obj.write(j)
                    file_obj.write("\n")
                for j in self.create_state_var('e', ro, group):
                    file_obj.write(j)
                    file_obj.write("\n")
                for step in range(4):
                    for j in self.create_state_var('f%i_' % step + 'z', ro, group):
                        file_obj.write(j)
                        file_obj.write("\n")
                    for k in range(self.word_size):
                        si = 's' + str(k)
                        tmp = ['f%i_' % step + 'g%i_' % group + si + '_%i' % ro + '_%i' % t for t in
                               range(ANF_map.get(si) + 1)]
                        for j in tmp:
                            file_obj.write(j)
                            file_obj.write("\n")
                    for k in range(self.word_size):
                        ti = 't' + str(k)
                        tmp = ['f%i_' % step + 'g%i_' % group + ti + '_%i' % ro + '_%i' % t for t in
                               range(ANF_map.get(ti) + 1)]
                        for j in tmp:
                            file_obj.write(j)
                            file_obj.write("\n")
                    for k in range(index_w):
                        file_obj.write('f%i_' % step + 'g%i_' % group + 'w' + '_%i' % ro + '_%i' % k)
                        file_obj.write("\n")
        for group in range(4):
            for j in self.create_state_var('x', self.round_num, group):
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
        # 设置整数精度
        m.setParam("IntFeasTol", 1e-7)
        counter = 0
        set_zero = []
        MILP_trails = []
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
                MILP_trails.append(MILP_trial)
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
        file_obj.write("The division trails is : \n")
        for index, Mi in enumerate(MILP_trails):
            file_obj.write("The division trails [%i] :\n" % index)
            for v in Mi:
                file_obj.write(v + '\n')
            # file_obj.write("\n")
        file_obj.write("\n")
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
    block_size = 64
    input_DP = "1111111111111111111111111111111111111111111111111111111111111110"
    rounds = 1

    filename_model = 'Feistel_64Bit%i_model.lp' % (rounds)
    filename_result = "Feistel_64Bit%i_result.txt" % (rounds)
    file_r = open(filename_result, "w+")
    file_r.close()
    fm = FeistelMultiBit(block_size, rounds, input_DP, filename_model, filename_result)
    # 最左边为最低位
    # Anf_m, index_w = fm.create_ANF_map_and_indexw()
    fm.create_model(input_DP)
    fm.solve_model()
