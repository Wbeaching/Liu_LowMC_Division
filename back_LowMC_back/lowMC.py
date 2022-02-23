import gurobipy as gp
import time


# from solve_model import *


class LowMC:
    # constant parameters

    def __init__(self, n, m, s, r, filename_model, filename_result):
        # block_size = 128
        # sbox_num = 10
        # # rounds = 2
        # sbox_size = 3
        self.block_size = n
        self.sbox_num = m
        self.sbox_size = s
        self.rounds = r
        self.filename_model = filename_model
        self.filename_result = filename_result

    # Linear inequalities for LowMC Sbox
    SBOX_INEQ = [[1, 1, 1, -1, -1, -1, 0],
                 [-1, -1, -2, 1, 1, 0, 2],
                 [-1, -1, 0, 1, 1, 2, 0],
                 [0, -1, -1, 0, -1, 1, 2],
                 [-1, 0, -1, -1, 0, 1, 2],
                 [0, -1, 0, -1, 1, -1, 2],
                 [-1, 0, 0, 1, -1, -1, 2],
                 [-1, 0, -1, 1, 2, 1, 0]]

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
        file_obj = open(self.filename_model, "w+")
        file_obj.write("Minimize\n")
        output_var = self.create_state_var('x', self.rounds)
        file_obj.write(' + '.join(output_var) + '\n')
        file_obj.close()

    def input_init(self, inputDP):
        """
        Generate constraints by the initial division property.
        """
        in_vars = self.create_state_var('x', 0)
        constraints = ['%s = %s' % (a, b) for a, b in zip(in_vars, inputDP)]
        file_obj = open(self.filename_model, "a")
        file_obj.write('Subject To\n')
        for enq in constraints:
            file_obj.write(enq + '\n')
        file_obj.close()

    def create_round_fn(self):
        for i in range(self.rounds):
            in_vars = self.create_state_var('x', i)
            mid_vars = self.create_state_var('t', i)
            out_vars = self.create_state_var('x', i + 1)
            # sbox
            self.constraints_sbox(in_vars, mid_vars)
            # Linearlayer
            self.constraints_linear_layer(mid_vars, out_vars)

    def constraints_sbox(self, in_vars, out_vars):
        """
        Generate the constraints by sbox layer.
        """
        file_obj = open(self.filename_model, "a")

        # An m-fold parallel application of the same 3-bit Sbox on the first 3m bits of the state.
        m = self.sbox_num
        for k in range(0, m):
            for coff in self.SBOX_INEQ:
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
                file_obj.write(temp_ineq)
                file_obj.write("\n")

        # For remaining n−3m bits, the SboxLayer is the identity.
        identity = 3 * self.sbox_num
        for i in range(identity, self.block_size):
            temp_ineq = in_vars[i] + " - " + out_vars[i] + " = 0"
            file_obj.write(temp_ineq)
            file_obj.write("\n")
        file_obj.close()

    def constraints_linear_layer(self, in_vars, out_vars):
        self.constraints_sbox(in_vars, out_vars)

    def create_binary(self):
        """
        Specify variable type.
        """
        file_obj = open(self.filename_model, "a")
        file_obj.write("Binary\n")
        for i in range(0, self.rounds):
            for j in self.create_state_var('x', i):
                file_obj.write(j)
                file_obj.write("\n")
            for j in self.create_state_var('t', i):
                file_obj.write(j)
                file_obj.write("\n")
        for j in self.create_state_var('x', self.rounds):
            file_obj.write(j)
            file_obj.write("\n")
        file_obj.write("END")
        file_obj.close()

    def create_model(self, inputDP):
        self.create_target_fn()
        self.input_init(inputDP)
        self.create_round_fn()
        self.create_binary()

    def solve_model(self):
        """
        Solve the MILP model to search the integral distinguisher of Present.
        """
        file_obj = open(self.filename_result, "w+")
        file_obj.write("Result!\n")
        file_obj.close()
        time_start = time.time()
        m = gp.read(self.filename_model)
        counter = 0
        set_zero = []
        global_flag = False
        while counter < self.block_size:
            m.optimize()
            # Gurobi syntax: m.Status == 2 represents the model is feasible.
            if m.Status == 2:
                obj = m.getObjective()
                if round(obj.getValue()) > 1:
                    global_flag = True
                    break
                else:
                    fileobj = open(self.filename_result, "a")
                    fileobj.write("************************************COUNTER = %d\n" % counter)
                    fileobj.close()
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

    # def SolveModelOptimize(self):
    #
    #     time_start = time.time()
    #     fileobj = open(self.filename_result, "w")
    #     m = gp.read(self.filename_model)
    #     # m.setParam("LazyConstraints", 1)
    #     set_zero = []
    #     set_zero_constraints = []
    #     for counter in range(0, self.block_size):
    #         m.optimize()
    #         # Gurobi syntax: m.Status == 2 represents the model is feasible.
    #         if m.Status == 2:
    #             obj = m.getObjective()
    #             if round(obj.getValue()) > 1:
    #                 break
    #             else:
    #                 for i in range(0, self.block_size):
    #                     u = obj.getVar(i)
    #                     temp = round(u.getAttr('x'))
    #                     if temp == 1:
    #                         fileobj.write("%03i" % counter + " (" + u.getAttr(
    #                             'VarName') + ") " + " -- UNKNOWN, run time: %f Seconds \n" % (m.Runtime))
    #                         print("%03i" % counter + " (" + u.getAttr(
    #                             'VarName') + ") " + " -- UNKNOWN, run time: %f Seconds \n" % (m.Runtime))
    #                         set_zero.append(u.getAttr('VarName'))
    #                         set_zero_constraints.append(m.addConstr(u == 0, 'tmp%i' % counter))
    #                         m.write("sol/%s.sol" % u.getAttr('VarName'))
    #                         m.update()
    #                         break
    #
    #         # Gurobi syntax: m.Status == 3 represents the model is infeasible.
    #         elif m.Status == 3:
    #             break
    #         # Gurobi syntax: m.Status == 9 represents the model is TimeLimit.
    #         elif m.Status == 9:
    #             fileobj.write("%03i" % counter + " (" + u.getAttr('VarName') + ") " + " -- TimeLimit \n")
    #             print("%03i" % counter + " (" + u.getAttr('VarName') + ") " + " -- TimeLimit \n")
    #             set_zero.append(u.getAttr('VarName'))
    #         else:
    #             fileobj.write("Unknown error!" + "\n")
    #             print("Unknown error!" + "\n")
    #             fileobj.close()
    #             return ([])
    #
    #     time_end = time.time()
    #     fileobj.write("run time: %f Seconds \n" % (time_end - time_start))
    #     fileobj.close()
    #
    #     if len(set_zero_constraints) > 0:
    #         m.remove(set_zero_constraints)
    #         m.update()
    #
    #     balanceBits = []
    #     for i in range(self.block_size):
    #         varName = m.getAttr('VarName')[i]
    #         if varName not in set_zero:
    #             balanceBits.append(varName)
    #     return (balanceBits)
