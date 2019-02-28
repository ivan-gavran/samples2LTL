from smtEncoding.dagSATEncoding import DagSATEncoding
from z3 import *
import sys
import pdb
import traceback

def get_models_fixed_size(z3Encoding, maxNumModels):

    num_found_models = 0
    results = []

    while num_found_models < maxNumModels and z3Encoding.solver.check() == sat:
        m = z3Encoding.solver.model()
        formula = z3Encoding.reconstructWholeFormula(m)
        print(str(formula))
        results.append(formula)
        num_found_models += 1
        block = []
        #pdb.set_trace()
        #print(m)
        infVariables = z3Encoding.getInformativeVariables()

        for v in infVariables:
            print((v, m[v]))
        for d in m:
            # d is a declaration
            if d.arity() > 0:
                raise Z3Exception("uninterpreted functions are not supported")
            # create a constant from declaration
            c = d()
            if is_array(c) or c.sort().kind() == Z3_UNINTERPRETED_SORT:
                raise Z3Exception("arrays and uninterpreted sorts are not supported")
            block.append(c != m[d])
        z3Encoding.solver.add(Or(block))
    return results

def get_models(finalDepth, traces, startValue, step, encoder, maxNumModels=1):
    num_found_formulas = 0
    results = []
    try:



        for i in range(startValue, finalDepth + 1, step):
            print("====== size ===== {}".format(i))

            fg = encoder(i, traces)
            fg.encodeFormula()
            fixed_size_results = get_models_fixed_size(fg, maxNumModels - num_found_formulas)
            results += fixed_size_results

            num_found_formulas += len(fixed_size_results)
         #   pdb.set_trace()
            if num_found_formulas >= maxNumModels:
                break

        return results

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        sys.exit(1)

        
    