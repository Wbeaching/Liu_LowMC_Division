import sys
sys.path.append("..")
from LowMC_S_L_MILP import LowMCMILP
from LowMC_S_L_MILP_i import LowMCMILP_i


if __name__ == "__main__":
    block_size = 192
    sbox_num = 10
    rounds = 24
    active_height = 191
 # 第一种，输入division不确定
    '''
    filepath = 'result/LowMC_division_R%i/' % (rounds)
    filename_all = filepath + '---LowMC_division----R%i_AllResult.txt' % (rounds)

    # 最左边为最低位
    filename_model = filepath + 'LowMC_division_R%i_A%i_model.lp' % (rounds, active_height)
    filename_result = filepath + 'LowMC_division_R%i_A%i_result.txt' % (rounds, active_height)

    fm = LowMCMILP(n=block_size, m=sbox_num, r=rounds, active_height=active_height, filename_model=filename_model, filename_result=filename_result)
    fm.create_model(active_height)
    zero_ = fm.solve_model()
    '''

    # 第二种，输入division为input_DP
    filepath = 'result/LowMC_division_R%i/' % (rounds)
    filename_all = filepath + '---LowMC_division----R%i_AllResult.txt' % (rounds)

    for active_point in range(1):
        active_point = 191
        vector = ['1'] * block_size
        vector[active_point] = '0'
        input_DP = ''.join(vector)

        # 最左边为最低位
        filename_model = filepath + 'LowMC_division_R%i_AP%i_model.lp' % (rounds, active_point)
        filename_result = filepath + 'LowMC_division_R%i_AP%i_result.txt' % (rounds, active_point)
        fm = LowMCMILP_i(n=block_size, m=sbox_num, r=rounds, filename_model=filename_model,
                       filename_result=filename_result)
        fm.create_model(input_DP)
        zero_ = fm.solve_model()

