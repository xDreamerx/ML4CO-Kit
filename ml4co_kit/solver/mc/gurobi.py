import os
import numpy as np
import gurobipy as gp
from typing import List
from multiprocessing import Pool
from ml4co_kit.solver.mc.base import MCSolver
from ml4co_kit.utils.graph.mc import MCGraphData
from ml4co_kit.utils.type_utils import SOLVER_TYPE
from ml4co_kit.utils.time_utils import iterative_execution, Timer


class MCGurobiSolver(MCSolver):
    def __init__(
        self, licence_path: str, weighted: bool = False, time_limit: float = 60.0
    ):
        super(MCGurobiSolver, self).__init__(
            solver_type=SOLVER_TYPE.GUROBI, weighted=weighted, time_limit=time_limit
        )
        self.licence_path = licence_path

    def solve(
        self,
        graph_data: List[MCGraphData] = None,
        num_threads: int = 1,
        show_time: bool = False
    ) -> np.ndarray:
        # preparation
        if graph_data is not None:
            self.graph_data = graph_data
        timer = Timer(apply=show_time)
        timer.start()
        
        # solve
        solutions = list()
        graph_num = len(self.graph_data)
        if num_threads == 1:
            for idx in iterative_execution(range, graph_num, self.solve_msg, show_time):
                solutions.append(self._solve(idx=idx))
        else:
            for idx in iterative_execution(
                range, graph_num // num_threads, self.solve_msg, show_time
            ):
                with Pool(num_threads) as p1:
                    cur_sols = p1.map(
                        self._solve,
                        [
                            idx * num_threads + inner_idx
                            for inner_idx in range(num_threads)
                        ],
                    )
                for sol in cur_sols:
                    solutions.append(sol)
            
        # restore solutions
        self.from_graph_data(nodes_label=solutions, ref=False, cover=False)
        
        # show time
        timer.end()
        timer.show_time()
        
        return self.graph_data
    
    def _solve(self, idx: int) -> np.ndarray:
        # graph
        mc_graph: MCGraphData = self.graph_data[idx]
        
        # number of graph's nodes
        nodes_num = mc_graph.nodes_num
        
        # edge_attr 
        mc_graph.check_edge_attr()
            
        # create gurobi model
        model = gp.Model(f"MC-{idx}")
        model.setParam("OutputFlag", 0)
        model.setParam("TimeLimit", self.time_limit)
        model.setParam("Threads", 1)
        
        # edges
        senders = mc_graph.edge_index[0]
        receivers = mc_graph.edge_index[1]
        edge_attr = mc_graph.edge_attr

        # Object
        var_dict = model.addVars(nodes_num, vtype=gp.GRB.BINARY)
        object = gp.quicksum( 
            (2 * var_dict[int(s)] - 1) * weight * (2 * var_dict[int(r)] - 1) / 2 
            for s, r, weight in zip(senders, receivers, edge_attr)
        )
        model.setObjective(object, gp.GRB.MINIMIZE)
        
        # Solve
        model.write(f"MC-{idx}.lp")
        model.optimize()
        os.remove(f"MC-{idx}.lp")
        
        # return
        return np.array([int(var_dict[key].X) for key in var_dict])
    
    def __str__(self) -> str:
        return "MCGurobiSolver"
