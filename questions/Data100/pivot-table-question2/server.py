import prairielearn as pl
import pandas as pd

def generate(data):
    df = pd.DataFrame({"A": ["foo", "foo", "foo", "foo", "foo",
                         "bar", "bar", "bar", "bar"],
                   "B": ["one", "one", "one", "two", "two",
                         "one", "one", "two", "two"],
                   "C": ["small", "large", "large", "small",
                         "small", "large", "small", "small",
                         "large"],
                   "D":["a","a","a","a","a","a","b","c","a"],
                   "E": [1, 2, 2, 3, 3, 4, 5, 6, 7],
                   "F": [2, 4, 5, 5, 6, 6, 8, 9, 9],
                   "G": [2, 1, 5, 3, 6, 6, 7, 7, 9]})
    data["params"]["df"] = pl.to_json(df.head(10))