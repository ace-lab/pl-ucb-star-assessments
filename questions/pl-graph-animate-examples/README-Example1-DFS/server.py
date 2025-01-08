import prairielearn as pl
import numpy as np

def generate(data):
    mat=np.array([[0, 1, 0, 1, 0],
                         [1, 0, 1, 0, 0],
                         [0, 1, 0, 0, 1],
                         [1, 0, 0, 0, 0],
                         [0, 0, 1, 0, 0]])

    data["params"]["matrix"] = pl.to_json(mat)