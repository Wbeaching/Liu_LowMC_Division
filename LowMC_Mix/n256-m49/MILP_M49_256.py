import os

import gurobipy as gp
import time
import caculator as ca


class LowMCMILP:
    def __init__(self, n, r, input_DP, filename_model, filename_result):
        self.block_size = n
        # 256
        self.round_num = r
        self.input_dp = input_DP
        self.file_model = filename_model
        self.file_result = filename_result
        self.ANF_xi = self.clean_ANF()
        f_path, f_name = os.path.split(filename_model)
        if not os.path.exists(f_path):
            os.makedirs(f_path)

    def clean_ANF(self):
        file_ANF = 'anf_of_sbox+linear-49-128.txt'
        anf = open(file_ANF, "r")
        ANF_xi = []
        anf_str = ''
        for i in anf:
            anf_str += i.strip()

        ANF_yi_str = anf_str.rstrip(',').split(',')
        # ANF_yi_str = anf_str.split(',')
        for yi_str in ANF_yi_str:
            yi_list_m = yi_str.strip().split('+')
            yi_list = []
            for x_and_x in yi_list_m:
                yi_list.append(x_and_x.strip().split('*'))
            ANF_xi.append(yi_list)
        return ANF_xi

    def create_ANF_map_and_indexw(self):
        ANF_map = {}
        index_w = 0
        for wi in self.ANF_xi:
            # [['s0', 'b0'], ['s1', 'b7'], ['s2', 'b6'], ['s3', 'b5'], ['s4', 'b4'], ['s5', 'b3'], ['s5', 'b7'],
            # index_w = len(wi) + index_w
            for wij in wi:
                if len(wij) == 2:
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
                    index_w += 1
                else:
                    left = wij[0]
                    left_n = 0
                    if left in ANF_map:
                        left_n = ANF_map.get(left) + 1
                    ANF_map[left] = left_n
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
        output_var = []
        output_var += self.create_state_var('x', self.round_num)
        file_obj.write(' + '.join(output_var) + '\n')
        file_obj.close()

    def input_init(self, input_DP):
        """
        Generate constraints by the initial division property.
        """
        in_vars = self.create_state_var('x', 0)
        constraints = ['%s = %s' % (a, b) for a, b in zip(in_vars, input_DP)]
        file_obj = open(self.file_model, "a")
        file_obj.write('Subject To\n')
        for enq in constraints:
            file_obj.write(enq + '\n')
        file_obj.close()

    def constraint_fi(self, round):
        # y = x^3
        # x ---> s[0]
        # mid_num = [8, 11, 14, 17, 20, 24, 27, 30]
        # 0. calculate the num of si and ti ANF_map = {'si' : num_of_ai}
        #                                    ANF_st_round = [[[s0_r_0, s1_r_0,....],[t0_r_0, t7_r_0...]],[[],[]]]

        # 0. generate map
        ANF_map = {}
        ANF_x_round = []
        for wi in self.ANF_xi:
            # [['x1'], ['x2', 'x65'], ['x2', 'x127'], ['x2', 'x128'], ['x3', 'x126'], ['x3', 'x129'], ['x4', 'x64']],
            vars_left = []
            vars_right = []
            for wij in wi:
                if len(wij) == 2:
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
                    vars_left.append('f_' + left + '_r%i' % round + '_%i' % left_n)
                    vars_right.append('f_' + right + '_r%i' % round + '_%i' % right_n)
                else:
                    left = wij[0]
                    right = 'one'
                    left_n = 0
                    if left in ANF_map:
                        left_n = ANF_map.get(left) + 1
                    ANF_map[left] = left_n
                    vars_left.append('f_' + left + '_r%i' % round + '_%i' % left_n)
                    vars_right.append(right)

            ANF_x_round.append([vars_left, vars_right])

        eqn_all = []

        # 1. write copy in ANF
        var_in_x = self.create_state_var('x', round)
        var_mid_fx = []
        enq_fx_copy = []
        for i in range(self.block_size):
            xi = 'x' + str(i)
            var_mid_fxi = ['f_' + xi + '_r%i' % round + '_%i' % xi_num for xi_num in range(ANF_map.get(xi) + 1)]
            enq_fx_copy.append(ca.constraint_copy_n(var_in_x[i], var_mid_fxi))
            var_mid_fx.append(var_mid_fxi)
        eqn_all += enq_fx_copy

        # 2. write and in ANF
        var_out_x = self.create_state_var('x', round + 1)
        index_w = 0
        eqn_and = []
        eqn_xor = []
        for lfi, zi in zip(ANF_x_round, var_out_x):
            vars_wi = lfi[0]
            for i in range(len(vars_wi)):
                xl = lfi[0][i]
                xr = lfi[1][i]
                if xr != 'one':
                    wi = 'f_w' + '_r%i' % round + '_%i' % index_w
                    index_w += 1
                    # 2.1 and in each line
                    eqn_and += ca.constraint_and_1(xl, xr, wi)
                    vars_wi[i] = wi
            # 2.2 xor in each line in ANF
            eqn_xor.append(' + '.join(vars_wi) + ' - ' + zi + " = " + str(0))
        eqn_all += eqn_and

        # 3. write xor in ANF
        eqn_all += eqn_xor

        # 4. write file
        file_obj = open(self.file_model, "a")
        # file_obj.write('[Begin] x^3 in [round_%i]!! [Begin]\n' % (round))
        for ieq in eqn_all:
            file_obj.write(ieq)
            file_obj.write("\n")

        # file_obj.write('[END] x^3 in [round_%i]!! [END]\n' % (round))
        file_obj.close()

    def create_round_fn(self):
        # 1/4 rounds

        for rnd in range(self.round_num):
            self.constraint_fi(rnd)

    def create_model(self, inputDP):
        self.create_target_fn()
        self.input_init(inputDP)
        self.create_round_fn()
        ANF_map, index_w = self.create_ANF_map_and_indexw()
        self.create_binary(ANF_map, index_w)

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
            for i in self.create_state_var('x', ro):
                file_obj.write(i)
                file_obj.write("\n")
            for k in range(self.block_size):
                xi = 'x' + str(k)
                tmp = ['f_' + xi + '_r%i' % ro + '_%i' % t for t in range(ANF_map.get(xi) + 1)]
                for j in tmp:
                    file_obj.write(j)
                    file_obj.write("\n")
            for k in range(index_w):
                file_obj.write('f_w' + '_r%i' % ro + '_%i' % k)
                file_obj.write("\n")
        for j in self.create_state_var('x', self.round_num):
            file_obj.write(j)
            file_obj.write("\n")
        file_obj.write("END")
        file_obj.close()

    def solve_model(self):
        """
        Solve the MILP model to search the integral distinguisher.
        """
        file_obj = open(self.file_result, "w+")
        file_obj.write("Result!\n")
        file_obj.close()
        time_start = time.time()
        m = gp.read(self.file_model)
        # 设置整数精度
        m.setParam("IntFeasTol", 1e-7)
        m.setParam("LazyConstraints", 1)
        m.setParam("Threads", 16)
        # m.setParam('OutputFlag', False)
        counter = 0
        set_zero = []
        MILP_trails = []
        global_flag = False
        while counter < self.block_size:
            m.optimize()
            # Gurobi syntax: m.Status == 2 represents the model is feasible.
            if m.Status == 2:
                all_vars = m.getVars()
                MILP_trails = []
                for v in all_vars:
                    name = v.getAttr('VarName')
                    valu = v.getAttr('x')
                    MILP_trails.append(name + ' = ' + str(valu))
                obj = m.getObjective()
                if round(obj.getValue()) > 1:
                    global_flag = True
                    break

                else:
                    file_obj = open(self.file_result, "a")
                    file_obj.write("************************************COUNTER = %d\n" % counter)
                    file_obj.close()
                    self.write_obj(obj)
                    for i in range(0, self.block_size):
                        u = obj.getVar(i)
                        temp = round(u.getAttr('x'))
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
        file_obj.write("The last division trails is : \n")
        for v in MILP_trails:
            file_obj.write(v + '\n')
        # file_obj.write("\n")
        file_obj.write("\n")
        time_end = time.time()
        file_obj.write(("Time used = " + str(time_end - time_start)))
        file_obj.close()
        return len(set_zero)

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
            if round(u.getAttr("x")) != 0:
                eqn1.append(u.getAttr('VarName'))
                eqn2.append(u.getAttr('x'))
        length = len(eqn1)
        for i in range(0, length):
            s = eqn1[i] + "=" + str(eqn2[i])
            file_obj.write(s)
            file_obj.write("\n")
        file_obj.close()


if __name__ == "__main__":
    block_size = 256
    len_zero = []
    rounds = 2
    filepath = 'result/LowMC_division_R%i/' % (rounds)
    filename_all = filepath + '---LowMC_division----R%i_AllResult.txt' % (rounds)
    for active_point in range(1, block_size):
    # for active_point in range(1):
    #     active_point = 2
        vector = ['1'] * block_size
        vector[active_point] = '0'
        input_DP = ''.join(vector)
        # 最左边为最低位
        filename_model = filepath + 'LowMC_division_R%i_A%i_model.lp' % (rounds, active_point)
        filename_result = filepath + 'LowMC_division_R%i_A%i_result.txt' % (rounds, active_point)

        fm = LowMCMILP(block_size, rounds, input_DP, filename_model, filename_result)
        fm.create_model(input_DP)
        zero_ = fm.solve_model()
        # len_zero.append('active_point = %i, len of zero = %i' % (active_point, zero_))
        file_r = open(filename_all, "a")
        file_r.write('active_point = %i, len of zero = %i' % (active_point, zero_))
        file_r.write('\n')
        file_r.close()
