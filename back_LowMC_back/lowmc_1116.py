import gurobipy as gp


# import time


# from solve_model import *


class LowMC:
    # constant parameters

    def __init__(self, n, m, s, r, filename_model):
        # block_size = 128
        # sbox_num = 10
        # # rounds = 2
        # sbox_size = 3
        self.block_size = n
        self.sbox_num = m
        self.sbox_size = s
        self.round_num = r
        self.filename_model = filename_model

    def create_state_var(self, x, r):
        # return [X0, X1, X2, ....] where X0 is LSB, X0 = [X07, X06, X05, ... , X00] where X00 is lsb
        state = []
        for iByte in range(self.block_size):
            state.append(x + '_%i' % r + '_%i' % iByte)
        return state

    def create_round_fn(self, r):
        variables = []
        constraints = []
        inputOutputVariablesLinearLayer = []
        # constrat
        return (variables, constraints, inputOutputVariablesLinearLayer)

    @staticmethod
    def get_vars_by_name(model, var_list):
        return [model.getVarByName(var) for var in var_list]

    def create_model1(self, inputDP, filename_model):
        # 变量
        variables = []
        # 不等式
        constraints = []
        # 不等式
        InputOutputVariablesLinearLayer = []

        XinSerialized = self.create_state_var('x', 0)
        variables += XinSerialized
        input_vars = XinSerialized
        output_vars = self.create_state_var('x', self.round_num)

        constraints += ['%s = %s' % (a, b) for a, b in zip(XinSerialized, inputDP)]
        constraints += [' + '.join(output_vars) + ' >= 1']

        for r in range(0, self.round_num):
            i = 0
            # round construct
            tmpVariables, tmpConstraints, tmpInputOutputVariablesLinearLayer = self.create_round_fn(r)
            variables += tmpVariables
            constraints += tmpConstraints
            InputOutputVariablesLinearLayer += tmpInputOutputVariablesLinearLayer

        Xout = self.create_state_var('x', self.round_num)
        # output variables
        variables += Xout
        self.write_model(constraints, variables, output_vars, filename_model)

        model = gp.read(filename_model)
        model._InputVariables = self.get_vars_by_name(model, input_vars)
        model._OutputVariables = self.get_vars_by_name(model, output_vars)
        model._InputOutputVariablesLinearLayer = [(self.get_vars_by_name(model, X), self.get_vars_by_name(model, Y)) for
                                                  X, Y in
                                                  InputOutputVariablesLinearLayer]

        return model

    @staticmethod
    def write_model(constraints, variables, output_var, filename_model):
        file_co = open(filename_model, 'w+')

        file_co.write('Minimize\n')
        file_co.write(' + '.join(output_var) + '\n')

        file_co.write('Subject To\n')
        for enq in constraints:
            file_co.write(enq + '\n')

        file_co.write('Binary\n')
        for v in variables:
            file_co.write(v + '\n')
        file_co.close()

    def create_target_fn(self):
        """
        Create Objective function of the MILP model.
        """
        file_co = open(self.filename_model, "w+")
        file_co.write("Minimize\n")
        output_var = self.create_state_var('x', self.round_num)
        file_co.write(' + '.join(output_var) + '\n')
        file_co.close()

    def inputInit(self, inputDP):
        """
        Generate constraints by the initial division property.
        """
        XinSerialized = self.create_state_var('x', 0)
        constraints = ['%s = %s' % (a, b) for a, b in zip(XinSerialized, inputDP)]
        file_co = open(self.filename_model, "a")
        file_co.write('Subject To\n')
        for enq in constraints:
            file_co.write(enq + '\n')
        file_co.close()

    def createBinaryVars(self):
        """
        Specify variable type.
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Binary\n")
        for i in range(0, self.round_num):
            for j in self.create_state_var('x', i):
                fileobj.write(j)
                fileobj.write("\n")
        for j in self.create_state_var('x', self.round_num):
            fileobj.write(j)
            fileobj.write("\n")
        fileobj.write("END")
        fileobj.close()

    def create_model(self, inputDP):
        self.create_target_fn()
        self.inputInit(inputDP)
        self.createBinaryVars()
