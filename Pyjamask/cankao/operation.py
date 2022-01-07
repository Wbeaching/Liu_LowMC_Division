class Operation:
    def DAnd(self, m, in1, in2, out ): 
        pass

    def DXor(self, m, in1, in2, out ):
        m.addConstr( in1 + in2 - out == 0 )
        return m

    def General_DXor(self, m, in_list, out ):
        m.addConstr( sum( in_list ) - out == 0 )
        return m

    def DCopy( self, m, inv, outv1, outv2 ):
        m.addConstr( inv <= outv1 - outv2 )
        m.addConstr( inv >= outv1 )
        m.addConstr( inv >= outv2 )
        return m

    def General_DCopy(self, m, inv, outv_list ):
        m.addConstr( inv <= sum( outv_list ) )
        for x in outv_list:
            m.addConstr( inv >= x )
        return m
   
    def pure_list( self, lst ):
        pureL = []
        for x in lst:
            if x is not 0:
                pureL.append( x )
        return pureL

    def vector_mul( self, coff, vecs ):
        return 



