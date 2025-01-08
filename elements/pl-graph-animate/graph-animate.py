import networkx as nx
import pygraphviz as pgv
import numpy as np
import prairielearn as pl
import moviepy
import moviepy.editor as mpy
import warnings
import os
import tempfile
import lxml
import base64
from typing import List

# Default parameters
ENGINE_DEFAULT = "dot"
PARAMS_TYPE_DEFAULT = "adjacency-matrix"
DIRECTED_DEFAULT = False
DURATION_FRAME_DEFAULT = 2
ALGORITHM_DEFAULT = "dfs"
SHOW_STEPS_DEFAULT=True
SHOW_WEIGHTS_DEFAULT=False



def generate_frames_bfs_from_matrix(matrix, start_node, show_steps, show_weights,directed, size="5,5")-> List:
    """
    **Parameters:**
    
    - `matrix`: Input adjacency matrix (numpy array or NetworkX graph) representing the graph.
    - `start_node`: Node from which the BFS traversal starts.
    - `show_steps`: Boolean-like string indicating whether to display step-by-step information in the graph (e.g., current node).
    - `show_weights`: Boolean-like string indicating whether to display edge weights in the visualization.
    - `directed`: Boolean-like string indicating whether the graph is directed or undirected.
    - `size`: String specifying the size of the graph visualization in "width,height" format. Default is "5,5".      
    
    The function generates a sequence of graph visualizations (frames) showing the progression of a Breadth-First Search (BFS) traversal. It highlights visited nodes and traversed edges step-by-step,
    optionally including step annotations and edge weights. 
    Each frame is saved as a temporary `.png` file and added to a list, which is returned as the function's output.
    """
    if isinstance(matrix, np.ndarray):  
        if directed==True:
            G = nx.from_numpy_array(matrix, create_using=nx.DiGraph())  
        else:
            G = nx.from_numpy_array(matrix)
    else:
        G = matrix 
    A = nx.nx_agraph.to_agraph(G)

    bfs_edges = list(nx.bfs_edges(G, source=start_node)) 
    bfs_nodes = list(nx.bfs_tree(G, source=start_node).nodes) 

    frames = []

    for i in range(1, len(bfs_nodes) + 1):
        A_temp = A.copy()

        nodes_to_highlight = bfs_nodes[:i]
        for node in nodes_to_highlight:
            A_temp.get_node(node).attr['color'] = 'red'
            A_temp.get_node(node).attr['style'] = 'filled'
            A_temp.get_node(node).attr['fillcolor'] = 'red'

        edges_to_highlight = bfs_edges[:i-1]  
        for edge in edges_to_highlight:
            A_temp.get_edge(edge[0], edge[1]).attr['color'] = 'blue'
            A_temp.get_edge(edge[0], edge[1]).attr['penwidth'] = 2.5

        if show_steps==True:
            A_temp.graph_attr['label'] = f"Step {i}: Current Node {bfs_nodes[i-1]} (BFS)"
            A_temp.graph_attr['labelloc'] = 'top'
        else:
            pass

        if show_weights==True:
            for u, v, data in G.edges(data=True):
                weight = data.get('weight', 1.0)  
                A_temp.get_edge(u, v).attr['label'] = str(weight)
        else:
            pass
        A_temp.graph_attr['size'] = size
        A_temp.graph_attr['dpi'] = "300"

        # Save the graph to a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        A_temp.draw(temp_file.name, format="png", prog="dot")

        frames.append(temp_file.name)

    return frames


def generate_frames_dfs_from_matrix(matrix, start_node, show_steps, show_weights, directed,size="5,5")-> List:
    """
    **Parameters:**
    
    - `matrix`: Input adjacency matrix (numpy array or NetworkX graph) representing the graph.
    - `start_node`: Node from which the BFS traversal starts.
    - `show_steps`: Boolean-like string indicating whether to display step-by-step information in the graph (e.g., current node).
    - `show_weights`: Boolean-like string indicating whether to display edge weights in the visualization.
    - `directed`: Boolean-like string indicating whether the graph is directed or undirected.
    - `size`: String specifying the size of the graph visualization in "width,height" format. Default is "5,5".      
    
    The function generates a sequence of graph visualizations (frames) showing the progression of a Depth-First Search (DFS) traversal. It highlights visited nodes and traversed edges step-by-step,
    optionally including step annotations and edge weights. 
    Each frame is saved as a temporary `.png` file and added to a list, which is returned as the function's output.
    """
    if isinstance(matrix, np.ndarray):  
        if directed==True:
            G = nx.from_numpy_array(matrix, create_using=nx.DiGraph())  
        else:
            G = nx.from_numpy_array(matrix)
    else:
        G = matrix 


    A = nx.nx_agraph.to_agraph(G)

    dfs_edges = list(nx.dfs_edges(G, source=start_node)) 
    dfs_nodes = list(nx.dfs_preorder_nodes(G, source=start_node)) 

    frames = []
    for i in range(1, len(dfs_nodes) + 1):
        A_temp = A.copy()
        nodes_to_highlight = dfs_nodes[:i]
        for node in nodes_to_highlight:
            A_temp.get_node(node).attr['color'] = 'red'
            A_temp.get_node(node).attr['style'] = 'filled'
            A_temp.get_node(node).attr['fillcolor'] = 'red'

        edges_to_highlight = dfs_edges[:i-1] 
        for edge in edges_to_highlight:
            A_temp.get_edge(edge[0], edge[1]).attr['color'] = 'blue'
            A_temp.get_edge(edge[0], edge[1]).attr['penwidth'] = 2.5
        if show_steps==True:
            A_temp.graph_attr['label'] = f"Step {i}: Current Node {dfs_nodes[i-1]} (DFS)"
            A_temp.graph_attr['labelloc'] = 'top'
        else: 
            pass
        if show_weights==True:
            for u, v, data in G.edges(data=True):
                weight = data.get('weight', 1.0)  
                A_temp.get_edge(u, v).attr['label'] = str(weight)
        else:
            pass
        A_temp.graph_attr['size'] = size
        A_temp.graph_attr['dpi'] = "300"
        # Save the graph to a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        A_temp.draw(temp_file.name, format="png", prog="dot")

        frames.append(temp_file.name)

    return frames

def generate_frames_dijkstra_from_matrix(matrix, start_node, show_steps, show_weights,directed, size="5,5")-> List:
    """
    **Parameters:**
    
    - `matrix`: Input adjacency matrix (numpy array or NetworkX graph) representing the graph.
    - `start_node`: Node from which the BFS traversal starts.
    - `show_steps`: Boolean-like string indicating whether to display step-by-step information in the graph (e.g., current node).
    - `show_weights`: Boolean-like string indicating whether to display edge weights in the visualization.
    - `directed`: Boolean-like string indicating whether the graph is directed or undirected.
    - `size`: String specifying the size of the graph visualization in "width,height" format. Default is "5,5".      
    
    The function generates a sequence of graph visualizations (frames) showing the progression of a Dijkstras traversal. It highlights visited nodes and traversed edges step-by-step,
    optionally including step annotations and edge weights. 
    Each frame is saved as a temporary `.png` file and added to a list, which is returned as the function's output.
    """
    if isinstance(matrix, np.ndarray):
        if directed==True:
            G = nx.from_numpy_array(matrix, create_using=nx.DiGraph())
        else:
            G = nx.from_numpy_array(matrix)
    else:
        G = matrix

    A = nx.nx_agraph.to_agraph(G)

    shortest_paths = nx.single_source_dijkstra_path_length(G, start_node)
    predecessors = nx.single_source_dijkstra_path(G, start_node)

    frames = []
    visited_nodes = set()
    visited_edges = set()

    step_count = 0  
    for target_node in shortest_paths.keys():
        step_count += 1
        if step_count % 2 != 0:  
            continue  
        A_temp = A.copy()
        path = predecessors[target_node]
        visited_nodes.update(path)
        for node in visited_nodes:
            A_temp.get_node(node).attr['color'] = 'red'
            A_temp.get_node(node).attr['style'] = 'filled'
            A_temp.get_node(node).attr['fillcolor'] = 'red'

        for i in range(len(path) - 1):
            edge = (path[i], path[i + 1])
            visited_edges.add(edge)
            A_temp.get_edge(edge[0], edge[1]).attr['color'] = 'blue'
            A_temp.get_edge(edge[0], edge[1]).attr['penwidth'] = 2.5

        if show_steps==True:
            A_temp.graph_attr['label'] = f"Target Node {target_node}: Shortest Path (Dijkstra)"
            A_temp.graph_attr['labelloc'] = 'top'
        else:
            pass

        if show_weights==True:
            for u, v, data in G.edges(data=True):
                weight = data.get('weight', 1.0)
                A_temp.get_edge(u, v).attr['label'] = str(weight)
        else:
            pass

        A_temp.graph_attr['size'] = size
        A_temp.graph_attr['dpi'] = "300"

        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        A_temp.draw(temp_file.name, format="png", prog="dot")
        frames.append(temp_file.name)

    return frames

def create_graph_frame_dotty(dot_commands_dict,size="5,5")-> List:
    """
    **Parameters:**
    
    - `dot_commands_dict`: A dictionary where keys represent steps and values are DOT command strings that define the graph at each step.
    - `size`: String specifying the size of the graph visualization in "width,height" format. Default is "5,5".
        
    The function generates a sequence of graph visualizations (frames) based on a dictionary of DOT commands. Each DOT command describes a specific state or configuration of the graph at a given step.
    The function saves each graph visualization as a temporary `.png` file and appends the file path to a list, which is returned as the output.
    """
    frames = []
    for step, dot_command in dot_commands_dict.items():
        # Create a Pygraphviz AGraph object from the DOT command string
        A = pgv.AGraph(string=dot_command)
        A.graph_attr['size'] = size  
        A.graph_attr['dpi'] = "300"          
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        image_path = temp_file.name
        A.draw(image_path, format="png", prog="dot")  
        frames.append(image_path)
    return frames 



# Function to combine frames list  into a video
def create_video_from_frames(frames, output_file, frame_duration):
    """
    This functions takes as input a list with frames as temporary png files and creates a mp4 video based on the frame duration.
    """
    clips = [mpy.ImageClip(f).set_duration(frame_duration) for f in frames]
    video = mpy.concatenate_videoclips(clips, method="compose")
    video.write_videofile(output_file, fps=24, verbose=False, logger=None)

def check_parameters(element_html: str, data: pl.QuestionData) -> None:
    """
    Validates that the parameters are in the correct format
    """
    try:
        
        element = lxml.html.fragment_fromstring(element_html)

        # Validate individual parameters
        input_param_name = pl.get_string_attrib(element, "params-name")
        if not isinstance(input_param_name, str) or not input_param_name:
            raise ValueError("Invalid 'params-name': must be a non-empty string.")

        input_type = pl.get_string_attrib(element, "params-type", PARAMS_TYPE_DEFAULT)
        if input_type not in [PARAMS_TYPE_DEFAULT, "dotty"]:
            raise ValueError(f"Invalid 'params-type': {input_type}. Must be 'adjacency-matrix' or 'dotty'.")

        algorithm = pl.get_string_attrib(element, "algorithm", ALGORITHM_DEFAULT).lower()
        if algorithm not in ["dfs", "bfs", "dijkstra"]:
            raise ValueError(f"Invalid 'algorithm': {algorithm}. Supported algorithms are 'dfs', 'bfs', or 'dijkstra'.")

        frame_duration = pl.get_string_attrib(element, "frame-duration", DURATION_FRAME_DEFAULT)
        try:
            frame_duration = float(frame_duration)
            if frame_duration <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("Invalid 'frame-duration': must be a positive float.")

        show_steps = pl.get_boolean_attrib(element, "show-steps", SHOW_STEPS_DEFAULT)
        if show_steps not in [True, False]:
            raise ValueError("Invalid 'show-steps': must be True or False.")

        show_weights = pl.get_boolean_attrib(element, "show-weights", SHOW_WEIGHTS_DEFAULT)
        if show_weights not in [True, False]:
            raise ValueError("Invalid 'show-weights': must be True or False.")

        directed_graph = pl.get_boolean_attrib(element, "directed-graph", DIRECTED_DEFAULT)
        if directed_graph not in [True, False]:
            raise ValueError("Invalid 'directed-graph': must be True or False.")
         # check input for PARAMS_TYPE_DEFAULT type is a 2d array
        if input_type == PARAMS_TYPE_DEFAULT:
            try:
                matrix = np.array(pl.from_json(data["params"][input_param_name]))
                if not isinstance(matrix, np.ndarray):
                    raise ValueError("Invalid adjacency matrix: must be an np.array.")
                if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
                    raise ValueError("Invalid adjacency matrix: must be a square 2D array.")
            except Exception:
                raise ValueError("Invalid JSON format for adjacency matrix.")
        # check input for dotty type is a dictionary
        if input_type == "dotty":
            try:
                
                dot_commands_dict = pl.from_json(data["params"][input_param_name])
                
                if not isinstance(dot_commands_dict, dict):
                    raise ValueError("Invalid dotty commands: must be a Python dictionary.")
            except Exception:
                raise ValueError("Invalid JSON format for dotty commands.")

    except Exception as e:
        raise ValueError(f"Parameter validation failed: {e}")




def render(element_html: str, data: pl.QuestionData) -> str:
    #check that all parameters are in the correct format
    check_parameters(element_html, data)
    # Parse the input parameters
    element = lxml.html.fragment_fromstring(element_html)
    input_param_name = pl.get_string_attrib(element, "params-name")
    input_type = pl.get_string_attrib(element, "params-type", PARAMS_TYPE_DEFAULT)
    algorithm = pl.get_string_attrib(element, "algorithm", ALGORITHM_DEFAULT).lower() 
    frame_duration = float(pl.get_string_attrib(element, "frame-duration", DURATION_FRAME_DEFAULT))
    show_steps = pl.get_boolean_attrib(element, "show-steps", SHOW_STEPS_DEFAULT)
    show_weights = pl.get_boolean_attrib(element, "show-weights", SHOW_WEIGHTS_DEFAULT)
    directed_graph=pl.get_boolean_attrib(element, "directed-graph", DIRECTED_DEFAULT)
    # Create video for input type adjacency-matrix or PARAMS_TYPE_DEFAULT
    if input_type==PARAMS_TYPE_DEFAULT:
        matrix = np.array(pl.from_json(data["params"][input_param_name]))
        start_node = 0 
        if algorithm == "dfs":
            frames=generate_frames_dfs_from_matrix(matrix, start_node,show_steps,show_weights,directed_graph)
        elif algorithm == "bfs":
            frames=generate_frames_bfs_from_matrix(matrix, start_node,show_steps,show_weights,directed_graph)
        elif algorithm == "dijkstra":
            frames=generate_frames_dijkstra_from_matrix(matrix, start_node,show_steps,show_weights,directed_graph)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")        
    
    # Create video for input type dotty
    elif input_type=="dotty":
        dot_commands_dict = pl.from_json(data["params"][input_param_name])
        frames = create_graph_frame_dotty(dot_commands_dict)
        output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    
    # Save the video to a temporary file
    output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    create_video_from_frames(frames, output_file, frame_duration)

    # Read the video file and encode it in base64
    with open(output_file, "rb") as video_file:
        video_base64 = base64.b64encode(video_file.read()).decode('utf-8')

    
    return f'<video controls  width="100" height="100"><source src="data:video/mp4;base64,{video_base64}" type="video/mp4"></video>'
