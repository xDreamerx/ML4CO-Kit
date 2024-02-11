## Data4CO

[![PyPi version](https://badgen.net/pypi/v/data4co/)](https://pypi.org/pypi/data4co/)
[![PyPI pyversions](https://img.shields.io/badge/dynamic/json?color=blue&label=python&query=info.requires_python&url=https%3A%2F%2Fpypi.org%2Fpypi%2Fdata4co%2Fjson)](https://pypi.python.org/pypi/data4co/)
[![Downloads](https://static.pepy.tech/badge/data4co)](https://pepy.tech/project/data4co)
[![GitHub stars](https://img.shields.io/github/stars/heatingma/Data4CO.svg?style=social&label=Star&maxAge=8640)](https://GitHub.com/heatingma/Data4CO/stargazers/) 

A data generator tool for Combinatorial Optimization (CO) problems, enabling customizable, diverse, and scalable datasets for benchmarking optimization algorithms.

### Current support

**solver**
|Problem|Base|Impl.|First|Impl.|Second|Impl.|Third|Impl.|Fourth|Impl.|
| :---: |:--:|:---:|:---:|:---:| :--: |:---:|:---:|:---:| :--: |:---:|
|  TSP  |TSPSolver| ✔ | LKH | ✔ | Concorde | ✔ | NARSolver | 📆 | ARSolver | 📆 |
|  MIS  | MISSolver | ✔ |KaMIS | ✔ | Gurobi| ✔ | -- | -- | -- | -- |

**generator**
|Problem| Type1 |Impl.| Type2 |Impl.| Type3 |Impl.| Type4 |Impl.|
| :---: | :---: |:---:| :---: |:---:| :---: |:---:| :---: |:---:|
|  TSP  | uniform | ✔ | gaussian | ✔ | cluster | 📆 | -- | -- |
|  MIS  | ER | ✔ | BA | ✔ | HK | ✔ | WS | ✔ |


✔: Supported; 📆: Planned for future versions (contributions welcomed!).

### How to Install

#### Github
Clone with the url https://github.com/heatingma/Data4CO.git , and the following packages are required, and shall be automatically installed by ``pip``:
```
Python >= 3.8
numpy>=1.24.4
networkx==2.8.8
lkh>=1.1.1
tsplib95==0.7.1
tqdm>=4.66.1
pulp>=2.8.0, 
pandas>=2.2.0,
scipy>=1.12.0
```

#### PyPI
It is very convenient to directly use the following commands
```
pip install data4co
```

### How to Use

#### TSP

```python
from data4co import TSPDataGenerator

tsp_data_lkh = TSPDataGenerator(
    batch_size=16,
    nodes_num=50,
    data_type="uniform",
    solver_type="lkh",
    train_samples_num=128000,
    val_samples_num=1280,
    test_samples_num=1280,
    save_path="your/path/to/save"
)

tsp_data_lkh.generate()
```

#### MIS

```python
from data4co import MISDataGenerator

mis_data_kamis = MISDataGenerator(
    nodes_num_min=700, 
    nodes_num_max=800,
    data_type="er",
    solver_type="kamis",
    train_samples_num=128000,
    val_samples_num=1280,
    test_samples_num=1280,
    save_path="your/path/to/save",
    solve_limit_time=10.0
)

mis_data_kamis.generate()
mis_data_kamis.solve()
```