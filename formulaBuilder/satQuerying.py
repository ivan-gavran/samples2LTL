from smtEncoding.dagSATEncoding import DagSATEncoding
from smtEncoding.SATOfLTLEncoding import SATOfLTLEncoding
from z3 import *
import sys
import pdb
import traceback
import logging
from utils.SimpleTree import Formula


def get_models_with_safety_restrictions(safety_restrictions, traces, final_depth, literals, encoder, operators,
                                        start_value = 1, step=1, max_num_solutions = 10):


    init_part_length = 3
    lasso_part_length = 3

    consistent_with_safety_restrictions = False
    results = []
    i = start_value
    fg = encoder(i, traces)
    fg.encodeFormula()
    num_solutions = 0
    while not consistent_with_safety_restrictions and i < final_depth and len(results) < max_num_solutions:
        solverRes = fg.solver.check()
        if not solverRes == sat:
            logging.debug("not sat for i = {}".format(i))
            i += step
            fg = encoder(i, traces)
            fg.encodeFormula()
        else:
            solverModel = fg.solver.model()
            formula = fg.reconstructWholeFormula(solverModel)
            logging.info("found formula {}".format(formula.prettyPrint()))

            formula = Formula.normalize(formula)
            logging.info("normalized formula: {}".format(formula))
            logging.info("=====\n")
            num_solutions += 1



            if formula not in results:
                results.append(formula)

            # prevent current result from being found again
            block = []
            infVariables = fg.getInformativeVariables()

            logging.debug("informative variables of the model:")
            for v in infVariables:
                logging.debug((v, solverModel[v]))
            logging.debug("===========================")
            for d in solverModel:
                # d is a declaration
                if d.arity() > 0:
                    raise Z3Exception("uninterpreted functions are not supported")
                # create a constant from declaration
                c = d()
                if is_array(c) or c.sort().kind() == Z3_UNINTERPRETED_SORT:
                    raise Z3Exception("arrays and uninterpreted sorts are not supported")
                block.append(c != solverModel[d])

            fg.solver.add(Or(block))


            counterexamples = []
            counterexample_found = False
            for safety_restriction in traces.safety_restrictions:
                test_formula = Formula(["&", formula, Formula(["!", safety_restriction])])

                cex_fg = SATOfLTLEncoding(test_formula, init_part_length, lasso_part_length, operators, literals)
                cex_fg.encodeFormula()
                cex_solverRes = cex_fg.solver.check()
                if cex_solverRes == sat:
                    cexSolverModel = cex_fg.solver.model()
                    cexTraces = cex_fg.reconstructCounterexampleTraces(cexSolverModel)
                    counterexamples += (cexTraces)

                if len(counterexamples) > 0:
                    counterexample_found = True
                    #pdb.set_trace()
                    traces.rejectedTraces += counterexamples


            if not counterexample_found:
                consistent_with_safety_restrictions = True
    return results


def get_models(finalDepth, traces, startValue, step, encoder, maxNumModels=1):
    results = []
    i = startValue
    fg = encoder(i, traces)
    fg.encodeFormula()
    while len(results) < maxNumModels and i < finalDepth:
        solverRes = fg.solver.check()
        if not solverRes == sat:
            logging.debug("not sat for i = {}".format(i))
            i += step
            fg = encoder(i, traces)
            fg.encodeFormula()
        else:
            solverModel = fg.solver.model()
            formula = fg.reconstructWholeFormula(solverModel)
            logging.info("found formula {}".format(formula.prettyPrint()))

            formula = Formula.normalize(formula)
            logging.info("normalized formula {}".format(formula))
            if formula not in results:
                results.append(formula)

            # prevent current result from being found again
            block = []

            infVariables = fg.getInformativeVariables()

            logging.debug("informative variables of the model:")
            for v in infVariables:
                logging.debug((v, solverModel[v]))
            logging.debug("===========================")
            for d in solverModel:
                # d is a declaration
                if d.arity() > 0:
                    raise Z3Exception("uninterpreted functions are not supported")
                # create a constant from declaration
                c = d()
                if is_array(c) or c.sort().kind() == Z3_UNINTERPRETED_SORT:
                    raise Z3Exception("arrays and uninterpreted sorts are not supported")
                block.append(c != solverModel[d])

            fg.solver.add(Or(block))
    return results
