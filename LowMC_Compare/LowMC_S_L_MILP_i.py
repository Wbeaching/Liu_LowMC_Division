import json
import os
import gurobipy as gp
import time

from preprocess import caculator as ca

class LowMCMILP_i:
    def __init__(self, n, m, r, filename_model, filename_result):
        self.block_size = n
        # 128
        self.sbox_num = m
        self.round_num = r
        self.file_model = filename_model
        self.file_result = filename_result
        self.ANF_xi = self.get_ANF_of_linearlayer(1)
        f_path, f_name = os.path.split(filename_model)
        if not os.path.exists(f_path):
            os.makedirs(f_path)

    # [x0, x1, x2, y0, y1, y2, a] where x -> y
    sbox_ineq = [[1, 1, 1, -1, -1, -1, 0],
                 [-1, -1, -2, 1, 1, 0, 2],
                 [-1, -1, 0, 1, 1, 2, 0],
                 [0, -1, -1, 0, -1, 1, 2],
                 [-1, 0, -1, -1, 0, 1, 2],
                 [0, -1, 0, -1, 1, -1, 2],
                 [-1, 0, 0, 1, -1, -1, 2],
                 [-1, 0, -1, 1, 2, 1, 0]]

    def get_ANF_of_linearlayer(self, r):
        file_ANF = os.path.abspath('..') + '/preprocess/matrices_and_constants_n%d.json' % self.block_size
        # file_ANF = 'preprocess/matrices_and_constants_n%d.json' % self.block_size
        # 保存了文本，我们在通过load读取出来
        with open(file_ANF, 'r', encoding='utf-8') as f:
            data = json.load(f)
        matrix_name = 'Linear_layer_%d' % r
        matrix = data[matrix_name]
        ANF_xi = []
        for row in matrix:
            yi_list = []
            for index, value in enumerate(row):
                if value == 1:
                    yi_list.append('x%d' % index)
            ANF_xi.append(yi_list)
        return ANF_xi

    def create_ANF_map_and_indexw(self):
        ANF_map = {}
        for wi in self.ANF_xi:
            # [['s0', 'b0'], ['s1', 'b7'], ['s2', 'b6'], ['s3', 'b5'], ['s4', 'b4'], ['s5', 'b3'], ['s5', 'b7'],
            # index_w = len(wi) + index_w
            for left in wi:
                left_n = 0
                if left in ANF_map:
                    left_n = ANF_map.get(left) + 1
                ANF_map[left] = left_n
        return ANF_map

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

    # def input_init_new(self, input_weight):
    #     """
    #     Generate constraints by the initial division property.
    #     """
    #     # in_vars = self.create_state_var('x', 0)
    #     # constraints = ['%s = %s' % (a, b) for a, b in zip(in_vars, input_DP)]
    #     file_obj = open(self.file_model, "a")
    #     file_obj.write('Subject To\n')
    #     output_var = []
    #     output_var += self.create_state_var('x', 0)
    #     file_obj.write(' + '.join(output_var) + ' = ' + str(input_weight) + '\n')
    #     file_obj.close()

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
            for left in wi:
                left_n = 0
                if left in ANF_map:
                    left_n = ANF_map.get(left) + 1
                ANF_map[left] = left_n
                vars_left.append('f_' + left + '_r%i' % round + '_%i' % left_n)
            ANF_x_round.append(vars_left)

        eqn_all = []

        # 1. write copy in ANF
        var_in_x = self.create_state_var('s', round)
        # var_mid_fx = []
        enq_fx_copy = []
        for i in range(self.block_size):
            xi = 'x' + str(i)
            var_mid_fxi = ['f_' + xi + '_r%i' % round + '_%i' % xi_num for xi_num in range(ANF_map.get(xi) + 1)]
            enq_fx_copy.append(ca.constraint_copy_n(var_in_x[i], var_mid_fxi))
            # var_mid_fx.append(var_mid_fxi)
        eqn_all += enq_fx_copy

        # 2. xor in each line in ANF
        var_out_x = self.create_state_var('x', round + 1)
        eqn_xor = []
        for vars_wi, zi in zip(ANF_x_round, var_out_x):
            # xor in each line in ANF
            eqn_xor.append(' + '.join(vars_wi) + ' - ' + zi + " = " + str(0))

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

    def constraints_sbox(self, in_vars, out_vars):
        """
        Generate the constraints by sbox layer.
        """
        constraints = []
        # An m-fold parallel application of the same 3-bit Sbox on the first 3m bits of the state.
        m = self.sbox_num
        for k in range(0, m):
            for coff in self.sbox_ineq:
                temp = []
                for u in range(0, 3):
                    temp.append(str(coff[u]) + " " + in_vars[(k * 3) + 2 - u])
                for v in range(0, 3):
                    temp.append(str(coff[v + 3]) + " " + out_vars[(k * 3) + 2 - v])
                temp_ineq = " + ".join(temp)
                temp_ineq = temp_ineq.replace("+ -", "- ")
                s = str(-coff[-1])
                s = s.replace("--", "")
                temp_ineq += " >= " + s
                constraints.append(temp_ineq)
                # file_obj.write("\n")

        # For remaining n−3m bits, the SboxLayer is the identity.
        identity = 3 * self.sbox_num
        for i in range(identity, self.block_size):
            temp_ineq = in_vars[i] + " - " + out_vars[i] + " = 0"
            constraints.append(temp_ineq)
        return constraints

    def constraints_SboxLayer(self, round):
        X = self.create_state_var('x', round)
        Y = self.create_state_var('s', round)
        constraints = self.constraints_sbox(X, Y)
        file_obj = open(self.file_model, "a")
        for ieq in constraints:
            file_obj.write(ieq)
            file_obj.write("\n")

        # file_obj.write('[END] x^3 in [round_%i]!! [END]\n' % (round))
        file_obj.close()

    def create_round_fn(self):
        for rnd in range(self.round_num):
            # 1. sbox layer
            self.constraints_SboxLayer(rnd)
            self.constraint_fi(rnd)

    def create_model(self, input_DP):
        self.create_target_fn()
        self.input_init(input_DP)
        self.create_round_fn()
        ANF_map = self.create_ANF_map_and_indexw()
        self.create_binary(ANF_map)

    def create_binary(self, ANF_map):
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
            for i in self.create_state_var('s', ro):
                file_obj.write(i)
                file_obj.write("\n")
            for k in range(self.block_size):
                xi = 'x' + str(k)
                tmp = ['f_' + xi + '_r%i' % ro + '_%i' % t for t in range(ANF_map.get(xi) + 1)]
                for j in tmp:
                    file_obj.write(j)
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
        m.setParam("Threads", 32)
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
                MILP_trail = []
                for v in all_vars:
                    name = v.getAttr('VarName')
                    valu = v.getAttr('x')
                    MILP_trail.append(name + ' = ' + str(valu))
                if len(MILP_trails) <= 3:
                    MILP_trails.append(MILP_trail)
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
        file_obj.write("The division trails is : \n")
        for index, Mi in enumerate(MILP_trails):
            file_obj.write("The division trails [%i] :\n" % index)
            for v in Mi:
                file_obj.write(v + '\n')
            # fileobj.write("\n")
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

#
if __name__ == "__main__":
    block_size = 192
    len_zero = []
    rounds = 1
    filepath = 'result/LowMC_division_R%i/' % (rounds)
    filename_all = filepath + '---LowMC_division----R%i_AllResult.txt' % (rounds)
#
    active_height = 127
#     # 最左边为最低位
    filename_model = filepath + 'LowMC_division_R%i_A%i_model.lp' % (rounds, active_height)
    filename_result = filepath + 'LowMC_division_R%i_A%i_result.txt' % (rounds, active_height)
#
    fm = LowMCMILP_i(n=block_size, m=31, r=rounds, active_height=active_height, filename_model=filename_model, filename_result=filename_result)
    for active_point in range(1):
        active_point = 95
        vector = ['1'] * block_size
        vector[active_point] = '0'
        input_DP = ''.join(vector)
        fm.create_model(input_DP)
        zero_ = fm.solve_model()
#     fm.create_model(active_height)
#     zero_ = fm.solve_model()

