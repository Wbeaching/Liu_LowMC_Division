from lowMC import LowMC

if __name__ == "__main__":
    block_size = 128
    sbox_num = 10
    sbox_size = 3
    round_num = 1

    # input_DP = '0000000000000000000000000000000000000000000000000000000000000000' \
    #            '0000000011111111111111111111111111111111111111111111111111111111'
    input_DP = '1100000000000000000000000000000000000000000000000000000000000000' \
               '0000000000000000000000000000000000000000000000000000000000000000'
    activebits = 2
    filename_model = 'lowMC_%i_%i_model.lp' % (round_num, activebits)
    filename_result = "lowMC_%i_%i_result.txt" % (round_num, activebits)
    file_obj = open(filename_result, "w+")
    file_obj.close()
    lm = LowMC(block_size, sbox_num, sbox_size, round_num, filename_model, filename_result)
    # 最左边为最低位


    lm.create_model(input_DP)
    lm.solve_model()

