import gurobipy as gp
import time
from Pyjamask.constants import *


class Pyjamask96:

    def __init__(self, round, input_DP, filename_model, filename_result):
        self.block_size = 96  # 96
        self.round_num = round
        self.input_dp = input_DP
        self.file_model = filename_model
        self.file_result = filename_result

    # x2 + x1 + x0 + y2 + y1 + y0 + r >=0

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
        for group in range(4):
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

    def constraints_sbox3(self, in_vars, out_vars):
        """
            Generate the constraints by one sbox.
         """
        ineq = []
        for coff in SBOX3_INEQ:
            temp = ['%i %s' % (u, v) for u, v in zip(coff, in_vars.reverse() + out_vars.reverse())]
            temp_ineq = " + ".join(temp)
            temp_ineq += " >= %s" % (-coff[-1])
            ineq.append(temp_ineq)
        return ineq

    # def constraints_diffusion(self):

    def create_round_fn(self):
        # 1. Sbox Layer
        ineq = []
        for si in range(32):
            in_s = ['x_%i_%i' % (round, sij * 32 + si) for sij in range(3)]
            out_s = ['y_%i_%i' % (round, sij * 32 + si) for sij in range(3)]
            ineq += self.constraints_sbox3(in_s, out_s)
        # 2. Diffusion Layer
        in_m0 = ['y_%i_%i' % (round, mi) for mi in range(32)]
        out_m0 = ['x_%i_%i' % (round+1, mi) for mi in range(32)]

        in_m1 = ['y_%i_%i' % (round, mi) for mi in range(32, 64)]
        out_m1 = ['x_%i_%i' % (round + 1, mi) for mi in range(32, 64)]

        in_m2 = ['y_%i_%i' % (round, mi) for mi in range(64, 96)]
        out_m2 = ['x_%i_%i' % (round + 1, mi) for mi in range(64, 96)]


    def create_model(self, input_DP):
        self.create_target_fn()
        self.input_init(input_DP)
        self.create_round_fn()
        self.create_binary()


# 最左侧是低位

if __name__ == "__main__":
    block_size = 96
    input_DP = "111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111110"
    round = 12

    filename_model = 'Pyjamask96%i_model.lp' % (round)
    filename_result = "Pyjamask96%i_result.txt" % (round)
    file_r = open(filename_result, "w+")
    file_r.close()
    P96 = Pyjamask96(round, input_DP, filename_model, filename_result)
    # 最左边为最低位
    # Anf_m, index_w = fm.create_ANF_map_and_indexw()
    P96.create_model(input_DP)
    P96.solve_model()
