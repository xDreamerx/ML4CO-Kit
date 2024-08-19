import numpy as np
from ml4co_kit.algorithm.tsp.decoder.cython_tsp_greedy import cython_tsp_greedy


def tsp_greedy_decoder(heatmap: np.ndarray, points: np.ndarray) -> np.ndarray:
    # prepare for decoding
    heatmap = heatmap.astype("double")
    points = points.astype("double")
    tours = list()
    
    # check the number of dimension
    if heatmap.ndim == 2:
        heatmap = np.expand_dims(heatmap, axis=0)
    if heatmap.ndim != 3:
        raise ValueError("``heatmap`` must be a 2D or 3D array.")
    if points.ndim == 2:
        points = np.expand_dims(points, axis=0)
    if points.ndim != 3:
        raise ValueError("``points`` must be a 2D or 3D array.")
    
    # tsp_greedy_decoder
    for idx in range(heatmap.shape[0]):
        adj_mat = cython_tsp_greedy(points[idx], heatmap[idx])[0]
        adj_mat = np.asarray(adj_mat)
        tour = [0]
        cur_node = 0
        cur_idx = 0
        while(len(tour) < adj_mat.shape[0] + 1):
            cur_idx += 1
            cur_node = np.nonzero(adj_mat[cur_node])[0]
            if cur_idx == 1:
                cur_node = cur_node.max()
            else:
                cur_node = cur_node[1] if cur_node[0] == tour[-2] else cur_node[0]
            tour.append(cur_node)
        tours.append(tour)
            
    # check shape
    tours = np.array(tours)
    if tours.shape[0] == 1:
        tours = tours[0]
    return tours