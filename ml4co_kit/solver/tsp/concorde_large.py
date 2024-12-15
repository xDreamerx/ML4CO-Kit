r"""
A TSP solver with condorde for large-scale problems.
"""

# Copyright (c) 2024 Thinklab@SJTU
# ML4CO-Kit is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
# http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import os
import time
import uuid
import numpy as np
from typing import Union
from multiprocessing import Process
from ml4co_kit.utils.type_utils import SOLVER_TYPE
from ml4co_kit.solver.tsp.pyconcorde import TSPConSolver
from ml4co_kit.solver.tsp.concorde import TSPConcordeSolver
from ml4co_kit.utils.time_utils import iterative_execution, Timer


class TSPConcordeLargeSolver(TSPConcordeSolver):
    r"""
    This class is a subclass of `TSPconcordeSolver` designed to solve the larger scale Traveling Salesman 
    Problem using the Concorde solver.

    :param scale: int, the scale factor for coordinates in the Concorde solver. Defaults to `1e6`.
    :param time_limit: float, the time limit in seconds for solving the TSP instance. Defaults to `3600` seconds.
    """
    def __init__(
        self,
        scale: int = 1e6,
        time_limit: float = 3600
    ):
        super(TSPConcordeLargeSolver, self).__init__(scale=scale)
        self.solver_type = SOLVER_TYPE.CONCORDE_LARGE
        self.time_limit = time_limit

    def read_from_sol(self, filename: str) -> np.ndarray:
        r"""
        Reads the solution from a `.sol` file generated by the Concorde solver.

        :param filename: string, the basic filename of the '.sol' files.

        .. dropdown:: Example

            ::
        """
        with open(filename, 'r') as file:
            ref_tour = list()
            first_line = True
            for line in file:
                if first_line:
                    first_line = False
                    continue
                line = line.strip().split(' ')
                for node in line:
                    ref_tour.append(int(node))
            ref_tour.append(0)
        return np.array(ref_tour)
   
    def _solve(self, nodes_coord: np.ndarray, name: str) -> np.ndarray:
        r"""
        Solves a single TSP instance using the Concorde solver.
        """
        solver = TSPConSolver.from_data(
            xs=nodes_coord[:, 0] * self.scale,
            ys=nodes_coord[:, 1] * self.scale,
            norm=self.norm,
            name=name,
        )
        solution = solver.solve(verbose=False, name=name)
        tour = solution.tour
        return tour

    def solve(
        self,
        points: Union[np.ndarray, list] = None,
        norm: str = "EUC_2D",
        normalize: bool = False,
        num_threads: int = 1,
        show_time: bool = False,
    ) -> np.ndarray:
        r"""
        Solves the TSP problem using the Concorde solver, with options for normalization,
        threading, and timing.
        
        :param points: np.ndarray or list, the coordinates of the nodes.
        :param norm: string, the normalization type for node coordinates (default is "EUC_2D").
        :param normalize: boolean, Whether to normalize node coordinates, (default is 'False').
        :param num_threads: int, the number of threads to use for solving, (default is '1') .
        :param show_time: boolean, whether to display the time taken for solving, (default is 'False').

        .. dropdown:: Example

            ::
        """
        # preparation
        self.from_data(points=points, norm=norm, normalize=normalize)
        timer = Timer(apply=show_time)
        timer.start()

        # solve
        tours = list()
        p_shape = self.points.shape
        num_points = p_shape[0]
        if num_threads == 1:
            for idx in iterative_execution(range, num_points, self.solve_msg, show_time):
                name = uuid.uuid4().hex
                filename = f"{name[0:9]}.sol"
                proc = Process(target=self._solve, args=(self.points[idx], name))
                proc.start()
                start_time = time.time()
                solve_finished = False
                while(time.time() - start_time < self.time_limit):
                    if os.path.exists(filename):
                        time.sleep(1)
                        solve_finished = True
                        break
                proc.terminate()
                proc.join(timeout=1)
                if solve_finished:
                    tour = self.read_from_sol(filename)
                    tours.append(tour)
                    self.clear_tmp_files(name)
                else:
                    self.clear_tmp_files(name)
                    raise TimeoutError()
        else:
            raise ValueError("TSPConcordeLargeSolver Only supports single threading!")

        # format
        tours = np.array(tours)
        self.from_data(tours=tours, ref=False)
        
        # show time
        timer.end()
        timer.show_time()
        
        # return
        return self.tours
    
    def __str__(self) -> str:
        return "TSPConcordeLargeSolver"