import time
import numpy as np
import tsplib95
import pathlib
from tqdm import tqdm
from multiprocessing import Pool
from typing import Union
from .base import TSPSolver
from .lkh_solver import lkh_solve


class TSPLKHSolver(TSPSolver):
    def __init__(
        self,
        lkh_max_trials: int = 1000,
        lkh_path: pathlib.Path = "LKH",
        scale: int = 1e6,
        lkh_runs: int = 10,
    ):
        """
        TSPLKHSolver
        Args:
            lkh_max_trials (int, optional): The maximum number of trials for
                the LKH solver. Defaults to 1000.
            lkh_path (pathlib.Path, optional): The path to the LKH solver.
                Defaults to "LKH".
            scale (int, optional): The scale factor for coordinates in the
                LKH solver. Defaults to 1e6.
            lkh_runs (int, optional): The number of runs for the LKH solver.
                Defaults to 10.
        """
        super(TSPLKHSolver, self).__init__(solver_type="lkh", scale=scale)
        self.lkh_max_trials = lkh_max_trials
        self.lkh_path = lkh_path
        self.scale = scale
        self.lkh_runs = lkh_runs

    def _solve(self, nodes_coord: np.ndarray) -> list:
        problem = tsplib95.models.StandardProblem()
        problem.name = "TSP"
        problem.type = "TSP"
        problem.dimension = self.nodes_num
        problem.edge_weight_type = self.norm
        problem.node_coords = {
            n + 1: nodes_coord[n] * self.scale for n in range(self.nodes_num)
        }
        solution = lkh_solve(
            solver=self.lkh_path,
            problem=problem,
            max_trials=self.lkh_max_trials,
            runs=self.lkh_runs,
        )
        tour = [n - 1 for n in solution[0]]
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
            if show_time:
                for idx in tqdm(range(num_points), desc="Solving TSP Using LKH"):
                    tours.append(self._solve(self.points[idx]))
            else:
                for idx in range(num_points):
                    tours.append(self._solve(self.points[idx]))
        else:
            batch_points = self.points.reshape(
                -1, num_threads, p_shape[-2], p_shape[-1]
            )
            if show_time:
                for idx in tqdm(
                    range(num_points // num_threads), desc="Solving TSP Using LKH"
                ):
                    with Pool(num_threads) as p1:
                        cur_tours = p1.map(
                            self._solve,
                            [
                                batch_points[idx][inner_idx]
                                for inner_idx in range(num_threads)
                            ],
                        )
                    for tour in cur_tours:
                        tours.append(tour)
            else:
                for idx in range(num_points // num_threads):
                    with Pool(num_threads) as p1:
                        cur_tours = p1.map(
                            self._solve,
                            [
                                batch_points[idx][inner_idx]
                                for inner_idx in range(num_threads)
                            ],
                        )
                    for tour in cur_tours:
                        tours.append(tour)

        # format
        tours = np.array(tours)
        zeros = np.zeros((tours.shape[0], 1))
        tours = np.append(tours, zeros, axis=1).astype(np.int32)
        if tours.ndim == 2 and tours.shape[0] == 1:
            tours = tours[0]
        self.read_tours(tours)
        end_time = time.time()
        if show_time:
            print(f"Use Time: {end_time - start_time}")
        return tours

    def regret_solve(
        self, points: np.ndarray, fixed_edges: tuple, norm: str = "EUC_2D"
    ):
        problem = tsplib95.models.StandardProblem()
        problem.name = "TSP"
        problem.type = "TSP"
        problem.dimension = points.shape[0]
        problem.edge_weight_type = norm
        problem.node_coords = {
            n + 1: self.scale * points[n] for n in range(points.shape[0])
        }
        problem.fixed_edges = [[n + 1 for n in fixed_edges]]
        solution = lkh_solve(
            solver=self.lkh_path,
            problem=problem,
            max_trials=self.lkh_max_trials,
            runs=self.lkh_runs,
        )
        tour = [n - 1 for n in solution[0]] + [0]
        np_tour = np.array(tour)
        return np_tour