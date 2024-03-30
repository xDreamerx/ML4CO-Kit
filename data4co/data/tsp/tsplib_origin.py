import os
from data4co.utils import download, extract_archive


TSPLIB_LARGE_EUC_2D_PATH = "dataset/tsplib_origin/large/EUC_2D"
TSPLIB_LARGE_EUC_2D = [
    'u1060', 'vm1084', 'pcb1173', 'd1291', 'rl1304', 'rl1323', 
    'nrw1379', 'fl1400', 'u1432', 'fl1577', 'd1655', 'vm1748', 
    'u1817', 'rl1889', 'd2103', 'u2152', 'u2319', 'pcb3038', 
    'fl3795', 'fnl4461', 'rl5915', 'rl5934', 'rl11849', 
    'usa13509', 'brd14051', 'd15112', 'd18512'
]

TSPLIB_LARGE_CEIL_2D_PATH = "dataset/tsplib_origin/large/CEIL_2D"
TSPLIB_LARGE_CEIL_2D = [
    'pla7397', 'pla33810', 'pla85900'
]

TSPLIB_RESOLVE_EUC_2D_PATH = "dataset/tsplib_origin/resolved/EUC_2D/problem"
TSPLIB_RESOLVE_EUC_2D_SOLUTION = "dataset/tsplib_origin/resolved/EUC_2D/solution"
TSPLIB_RESOLVE_EUC_2D = [
    'att48', 'eil51', 'berlin52', 'st70', 'pr76', 'kroC100', 'eil101', 
    'lin105', 'ch130', 'ch150', 'tsp225', 'a280', 'pr1002', 'pr2392'
]

TSPLIB_RESOLVE_EXPLICIT_PATH = "dataset/tsplib_origin/resolved/EXPLICIT/problem"
TSPLIB_RESOLVE_EXPLICIT_SOLUTION = "dataset/tsplib_origin/resolved/EXPLICIT/solution"
TSPLIB_RESOLVE_EXPLICIT = [
    'gr24', 'fri26', 'bayg29', 'gr48', 'gr120', 'brg180', 'pa561'
]

TSPLIB_RESOLVE_GEO_PATH = "dataset/tsplib_origin/resolved/GEO/problem"
TSPLIB_RESOLVE_GEO_SOLUTION = "dataset/tsplib_origin/resolved/GEO/solution"
TSPLIB_RESOLVE_GEO = [
    'ulysses16', 'ulysses22', 'gr96', 'gr202', 'gr666'
]

TSPLIB_UNRESOLVE_EUC_2D_PATH = "dataset/tsplib_origin/unresolved/EUC_2D"
TSPLIB_UNRESOLVE_EUC_2D = [
    'rat99', 'kroE100', 'pr107', 'pr124', 'bier127', 'pr136', 'pr144', 
    'kroB150', 'pr152', 'u159', 'rat195', 'd198', 'kroB200', 'ts225', 
    'pr226', 'gil262', 'pr264', 'pr299', 'lin318', 'rd400', 'fl417', 
    'pr439', 'pcb442', 'd493', 'att532', 'u574', 'rat575', 'p654', 'd657', 
    'u724', 'rat783', 'dsj1000'
]

TSPLIB_UNRESOLVE_EXPLICIT_PATH = "dataset/tsplib_origin/unresolved/EXPLICIT"
TSPLIB_UNRESOLVE_EXPLICIT = [
    'gr17', 'gr21', 'swiss42', 'hk48', 'brazil58'
]

TSPLIB_UNRESOLVE_GEO_PATH = "dataset/tsplib_origin/unresolved/GEO"
TSPLIB_UNRESOLVE_GEO = [
    'burma14', 'ali535'
]


class TSPLIBOriginDataset:
    def __init__(self):
        self.url = "https://huggingface.co/datasets/ML4TSP/TSPLIBOriginDataset/resolve/main/tsplib_origin.tar.gz?download=true"
        self.md5 = "f096628e060cbc6b800c9dbaa8d2bd0c"
        self.dir = "dataset/tsplib_origin"
        self.raw_data_path = "dataset/tsplib_origin.tar.gz"
        if not os.path.exists('dataset'):
            os.mkdir('dataset')
        if not os.path.exists(self.dir):
            download(filename=self.raw_data_path, url=self.url, md5=self.md5)
            extract_archive(archive_path=self.raw_data_path, extract_path=self.dir)

    @property
    def support(self):
        return{
            "large": {
                "EUC_2D":{
                    "path": TSPLIB_LARGE_EUC_2D_PATH,
                    "problem": TSPLIB_LARGE_EUC_2D
                },
                "CEIL_2D":{
                    "path": TSPLIB_LARGE_CEIL_2D_PATH,
                    "problem": TSPLIB_LARGE_CEIL_2D 
                }
            },
            "resolved":{
                "EUC_2D":{
                    "path": TSPLIB_RESOLVE_EUC_2D_PATH,
                    "solution": TSPLIB_RESOLVE_EUC_2D_SOLUTION,
                    "problem": TSPLIB_RESOLVE_EUC_2D 
                },
                "EXPLICIT":{
                    "path": TSPLIB_RESOLVE_EXPLICIT_PATH,
                    "solution": TSPLIB_RESOLVE_EXPLICIT_SOLUTION,
                    "problem": TSPLIB_RESOLVE_EXPLICIT
                },
                "GEO":{
                    "path": TSPLIB_RESOLVE_GEO_PATH,
                    "solution": TSPLIB_RESOLVE_GEO_SOLUTION,
                    "problem": TSPLIB_RESOLVE_GEO  
                }
            },
            "unresolved":{
                "EUC_2D":{
                    "path": TSPLIB_UNRESOLVE_EUC_2D_PATH,
                    "problem" : TSPLIB_UNRESOLVE_EUC_2D
                },
                "EXPLICIT":{
                    "path": TSPLIB_UNRESOLVE_EXPLICIT_PATH,
                    "problem": TSPLIB_UNRESOLVE_EXPLICIT 
                },
                "GEO":{
                    "path": TSPLIB_UNRESOLVE_GEO_PATH,
                    "problem": TSPLIB_UNRESOLVE_GEO 
                },
            }
        }

