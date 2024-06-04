import os
import time
import uuid
import numpy as np
from typing import Union
from multiprocessing import Process
from ml4co_kit.solver.tsp.pyconcorde import TSPConSolver
from ml4co_kit.solver.tsp.concorde import TSPConcordeSolver
from ml4co_kit.utils.run_utils import iterative_execution


class TSPConcordeLargeSolver(TSPConcordeSolver):
    def __init__(
        self,
        scale: int = 1e6,
        time_limit: float = 3600
    ):
        """
        TSPConcordeSolver
        Args:
            scale (int, optional):
                The scale factor for coordinates in the Concorde solver.
        """
        super(TSPConcordeLargeSolver, self).__init__(scale=scale)
        self.solver_type = "Concorde-Large"
        self.time_limit = time_limit

    def read_from_sol(self, filename: str) -> np.ndarray:
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
        # prepare
        self.from_data(points, norm, normalize)
        start_time = time.time()

        # solve
        tours = list()
        p_shape = self.points.shape
        num_points = p_shape[0]
        if num_threads == 1:
            for idx in iterative_execution(
                range, num_points, "Solving TSP Using Concorde-Large", show_time
            ):
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
        if tours.ndim == 2 and tours.shape[0] == 1:
            tours = tours[0]
        self.read_tours(tours)
        end_time = time.time()
        if show_time:
            print(f"Use Time: {end_time - start_time}")
        return tours