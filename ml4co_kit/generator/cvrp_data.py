import os
import time
import numpy as np
import pathlib
from tqdm import tqdm
from typing import Union
from multiprocessing import Pool
from ml4co_kit.solver.cvrp import CVRPSolver, CVRPPyVRPSolver


class CVRPDataGenerator:
    def __init__(
        self,
        num_threads: int = 1,
        nodes_num: int = 50,
        data_type: str = "uniform",
        solver: Union[str, CVRPSolver] = "pyvrp",
        train_samples_num: int = 128000,
        val_samples_num: int = 1280,
        test_samples_num: int = 1280,
        save_path: pathlib.Path = "data/cvrp/uniform",
        filename: str = None,
        # special for demand and capacity
        min_demand: float = 1.0,
        max_demand: float = 10.0,
        min_capacity: float = 40.0,
        max_capacity: float = 40.0,
        # special for gaussian
        gaussian_mean_x: float = 0.0,
        gaussian_mean_y: float = 0.0,
        gaussian_std: float = 1.0,
    ):
        """
        CVRPDataGenerator
        Args:
            num_threads (int, optional):
                The number of threads to generate datasets.
            nodes_num (int, optional):
                The number of nodes.
            data_type (str, optional):
                The data type.
            solver_type (str, optional):
                The solver type.
            train_samples_num (int, optional):
                The number of training samples.
            val_samples_num (int, optional):
                The number of validation samples.
            test_samples_num (int, optional):
                The number of test samples.
            save_path (pathlib.Path, optional):
                The save path.
            filename (str, optional):
                The filename.
            gaussian_mean_x (float, optional):
                The mean of the x-coordinate in Gaussian data generation.
            gaussian_mean_y (float, optional):
                The mean of the y-coordinate in Gaussian data generation.
            gaussian_std (float, optional):
                The standard deviation in Gaussian data generation.
        """
        # record variable data
        self.num_threads = num_threads
        self.nodes_num = nodes_num
        self.data_type = data_type
        self.solver = solver
        self.train_samples_num = train_samples_num
        self.val_samples_num = val_samples_num
        self.test_samples_num = test_samples_num
        self.save_path = save_path
        self.filename = filename
        # special for demand and capacity
        self.min_demand = min_demand
        self.max_demand = max_demand
        self.min_capacity = min_capacity
        self.max_capacity = max_capacity
        # special for gaussian
        self.gaussian_mean_x = gaussian_mean_x
        self.gaussian_mean_y = gaussian_mean_y
        self.gaussian_std = gaussian_std
        # check the input variables
        self.sample_types = ["train", "val", "test"]
        self.check_num_threads()
        self.check_data_type()
        self.check_solver()
        self.get_filename()

    def check_num_threads(self):
        self.samples_num = 0
        for sample_type in self.sample_types:
            self.samples_num += getattr(self, f"{sample_type}_samples_num")
            if self.samples_num % self.num_threads != 0:
                message = "``samples_num`` must be divisible by the number of threads. "
                raise ValueError(message)

    def check_data_type(self):
        generate_func_dict = {
            "uniform": self.generate_uniform,
            "gaussian": self.generate_gaussian,
        }
        supported_data_type = generate_func_dict.keys()
        if self.data_type not in supported_data_type:
            message = (
                f"The input data_type ({self.data_type}) is not a valid type, "
                f"and the generator only supports {supported_data_type}."
            )
            raise ValueError(message)
        self.generate_func = generate_func_dict[self.data_type]

    def check_solver(self):
        # get solver
        if type(self.solver) == str:
            self.solver_type = self.solver
            supported_solver_dict = {"pyvrp": CVRPPyVRPSolver}
            supported_solver_type = supported_solver_dict.keys()
            if self.solver_type not in supported_solver_type:
                message = (
                    f"The input solver_type ({self.solver_type}) is not a valid type, "
                    f"and the generator only supports {supported_solver_type}."
                )
                raise ValueError(message)
            self.solver = supported_solver_dict[self.solver_type]()
        else:
            self.solver: CVRPSolver
            self.solver_type = self.solver.solver_type

    def get_filename(self):
        self.filename = (
            f"cvrp{self.nodes_num}_{self.data_type}"
            if self.filename is None
            else self.filename
        )
        self.file_save_path = os.path.join(self.save_path, self.filename + ".txt")
        for sample_type in self.sample_types:
            setattr(
                self,
                f"{sample_type}_file_save_path",
                os.path.join(self.save_path, self.filename + f"_{sample_type}.txt"),
            )
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def generate(self):
        with open(self.file_save_path, "w") as f:
            start_time = time.time()
            for _ in tqdm(
                range(self.samples_num // self.num_threads),
                desc=f"Solving CVRP Using {self.solver_type}",
            ):
                batch_depots_coord, batch_nodes_coord= self.generate_func()
                batch_demands = self.generate_demands()
                batch_capacities = self.generate_capacities()
                with Pool(self.num_threads) as p1:
                    tours = p1.starmap(
                        self.solver.solve,
                        [(batch_depots_coord[idx],
                          batch_nodes_coord[idx],
                          batch_demands[idx],
                          batch_capacities[idx])
                         for idx in range(self.num_threads)],
                    )
                # write to txt
                for idx, tour in enumerate(tours):
                    depot = batch_depots_coord[idx]
                    points = batch_nodes_coord[idx]
                    demands = batch_demands[idx]
                    capicity = batch_capacities[idx][0]
                    f.write("depots " + str(" ").join(str(depot_coord) for depot_coord in depot))
                    f.write(" points" + str(" "))
                    f.write(
                        " ".join(
                            str(x) + str(" ") + str(y)
                            for x, y in points
                        )
                    )
                    f.write(" demands " + str(" ").join(str(demand) for demand in demands))
                    f.write(" capacity " + str(capicity))
                    f.write(str(" output "))
                    f.write(str(" ").join(str(node_idx) for node_idx in tour[0]))
                    f.write("\n")
            end_time = time.time() - start_time
            f.close()
            print(
                f"Completed generation of {self.samples_num} samples of CVRP{self.nodes_num}."
            )
            print(f"Total time: {end_time/60:.1f}m")
            print(f"Average time: {end_time/self.samples_num:.1f}s")
        self.devide_file()

    def devide_file(self):
        with open(self.file_save_path, "r") as f:
            data = f.readlines()
        train_end_idx = self.train_samples_num
        val_end_idx = self.train_samples_num + self.val_samples_num
        train_data = data[:train_end_idx]
        val_data = data[train_end_idx:val_end_idx]
        test_data = data[val_end_idx:]
        data = [train_data, val_data, test_data]
        for sample_type, data_content in zip(self.sample_types, data):
            filename = getattr(self, f"{sample_type}_file_save_path")
            with open(filename, "w") as file:
                file.writelines(data_content)

    def generate_demands(self) -> np.ndarray:
        return np.random.uniform(
            low=self.min_demand,
            high=self.max_demand,
            size=(self.num_threads, self.nodes_num)
        )
        
    def generate_capacities(self) -> np.ndarray:
        return np.random.uniform(
            low=self.min_capacity,
            high=self.max_capacity,
            size=(self.num_threads, 1)
        )
    
    def generate_uniform(self) -> np.ndarray:
        depots = np.random.random([self.num_threads, 2])
        points = np.random.random([self.num_threads, self.nodes_num, 2]) 
        return depots, points

    def generate_gaussian(self) -> np.ndarray:
        depots = np.random.normal(
            loc=[self.gaussian_mean_x, self.gaussian_mean_y],
            scale=self.gaussian_std,
            size=(self.num_threads, 2),
        )
        points = np.random.normal(
            loc=[self.gaussian_mean_x, self.gaussian_mean_y],
            scale=self.gaussian_std,
            size=(self.num_threads, self.nodes_num, 2),
        )
        return depots, points