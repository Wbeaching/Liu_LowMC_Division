import os

from FieldMultiplication.Feistel2_Multi4_Bit64 import Feistel2Multi4Bit64
from FieldMultiplication.Feistel4_Multi4_Bit128 import FeistelMultiBit


def find_bit_integral_distinguisher(block_size, rounds, cipher_name, CIPHER_CLASS_NAME):

    filepath = 'result/' + cipher_name + '_R%i/' % (rounds)
    len_zero = []
    for active_point in range(6, block_size):
    # for active_point in range(1):
        vector = ['1'] * block_size
        vector[active_point] = '0'
        input_DP = ''.join(vector)

        filename_model = filepath + cipher_name + '_R%i_A%i_model.lp' % (rounds, active_point)
        filename_result = filepath + cipher_name + '_R%i_A%i_result.txt' % (rounds, active_point)
        file_r = open(filename_result, "w+")
        file_r.close()
        fm = CIPHER_CLASS_NAME(block_size, rounds, input_DP, filename_model, filename_result)
        # 最左边为最低位
        fm.create_model(input_DP)
        zero_ = fm.solve_model()
        len_zero.append('active_point = %i, len of zero = %i' % (active_point, zero_))

    filename_result = filepath + '---' + cipher_name +'----R%i_AllResult.txt' % (rounds)
    file_r = open(filename_result, "w+")
    for i in len_zero:
        file_r.write(i)
        file_r.write('\n')
    file_r.close()


block_size = 64
rounds = 11
cipher_name = 'Feistel2_Bit64'
find_bit_integral_distinguisher(block_size, rounds, cipher_name, Feistel2Multi4Bit64)
