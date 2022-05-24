import sys
sys.path.append("..")
from LowMC_SL_ANF_MILP import LowMCMILP



if __name__ == "__main__":
    block_size = 256
    rounds = 15
    active_height = 191
    sbox_num = 10
    filepath = 'result/LowMC_division_R%i/' % (rounds)
    filename_all = filepath + '---LowMC_division----R%i_AllResult.txt' % (rounds)

    # 最左边为最低位
    filename_model = filepath + 'LowMC_division_R%i_A%i_model.lp' % (rounds, active_height)
    filename_result = filepath + 'LowMC_division_R%i_A%i_result.txt' % (rounds, active_height)

    fm = LowMCMILP(n=block_size, m=sbox_num, r=rounds, active_height=active_height, filename_model=filename_model, filename_result=filename_result)
    fm.create_model()
    zero_ = fm.solve_model()

