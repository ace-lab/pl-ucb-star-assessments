import prairielearn as pl
import numpy as np

def generate(data):
    

    bfs_dot_commands = {
    "step_1": """
    digraph G {
        label="Step 1: Visit Node 0 from Node 0";
        labelloc="top";
        0 [style=filled, fillcolor=red];
        0 -> 1 [color=black];
        0 -> 2 [color=black];
        0 -> 3 [color=black];
        1 -> 4 [color=black];
        2 -> 5 [color=black];
        2 -> 6 [color=black];
        3 -> 7 [color=black];
        6 -> 8 [color=black];
    }
    """,
    "step_2": """
    digraph G {
        label="Step 2: Visit Node 1 from Node 0";
        labelloc="top";
        0 [style=filled, fillcolor=red];
        1 [style=filled, fillcolor=red];
        0 -> 1 [color=blue];
        0 -> 2 [color=black];
        0 -> 3 [color=black];
        1 -> 4 [color=black];
        2 -> 5 [color=black];
        2 -> 6 [color=black];
        3 -> 7 [color=black];
        6 -> 8 [color=black];
    }
    """,
    "step_3": """
    digraph G {
        label="Step 3: Visit Node 2 from Node 0";
        labelloc="top";
        0 [style=filled, fillcolor=red];
        1 [style=filled, fillcolor=red];
        2 [style=filled, fillcolor=red];
        0 -> 1 [color=blue];
        0 -> 2 [color=blue];
        0 -> 3 [color=black];
        1 -> 4 [color=black];
        2 -> 5 [color=black];
        2 -> 6 [color=black];
        3 -> 7 [color=black];
        6 -> 8 [color=black];
    }
    """,
    "step_4": """
    digraph G {
        label="Step 4: Visit Node 3 from Node 0";
        labelloc="top";
        0 [style=filled, fillcolor=red];
        1 [style=filled, fillcolor=red];
        2 [style=filled, fillcolor=red];
        3 [style=filled, fillcolor=red];
        0 -> 1 [color=blue];
        0 -> 2 [color=blue];
        0 -> 3 [color=blue];
        1 -> 4 [color=black];
        2 -> 5 [color=black];
        2 -> 6 [color=black];
        3 -> 7 [color=black];
        6 -> 8 [color=black];
    }
    """
}




    data["params"]["dotty-commands-dictionary"] = pl.to_json(bfs_dot_commands)
    