import os
import numpy as np
import pandas as pd
from ml4co_kit.data.tsp.tsplib_original import TSPLIBOriDataset
from ml4co_kit.solver.tsp.base import TSPSolver


class TSPLIBOriEvaluator:
    def __init__(self) -> None:
        self.dataset = TSPLIBOriDataset()
        self.support = self.dataset.support["resolved"]

    def evaluate(
        self,
        solver: TSPSolver,
        norm: str = "EUC_2D",
        normalize: bool = False,
        **solver_args
    ):
        # record
        solved_costs = dict()
        ref_costs = dict()
        gaps = dict()

        # get the evaluate files' dir and the problem name list
        evaluate_dir = self.support[norm]["path"]
        solution_dir = self.support[norm]["solution"]
        problem_list = self.support[norm]["problem"]

        # solve
        for problem in problem_list:
            # read problem
            file_path = os.path.join(evaluate_dir, problem + ".tsp")
            ref_tour_path = os.path.join(solution_dir, problem + ".opt.tour")
            solver.from_tsplib(
                tsp_file_path=file_path, tour_file_path=ref_tour_path,
                ref=True, norm=norm, normalize=normalize
            )

            # real solve
            solver.solve(**solver_args)
            solved_cost, ref_cost, gap, _ = solver.evaluate(calculate_gap=True)
            
            # record
            solved_costs[problem] = solved_cost
            ref_costs[problem] = ref_cost
            gaps[problem] = gap

        # average
        np_solved_costs = np.array(list(solved_costs.values()))
        np_ref_costs = np.array(list(ref_costs.values()))
        np_gaps = np.array(list(gaps.values()))
        avg_solved_cost = np.average(np_solved_costs)
        avg_ref_cost = np.average(np_ref_costs)
        avg_gap = np.average(np_gaps)
        solved_costs["AVG"] = avg_solved_cost
        ref_costs["AVG"] = avg_ref_cost
        gaps["AVG"] = avg_gap

        # output
        return_dict = {
            "solved_costs": solved_costs,
            "ref_costs": ref_costs,
            "gaps": gaps,
        }
        df = pd.DataFrame(return_dict)
        return df
