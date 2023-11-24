import random, string, copy
import prairielearn as pl
import networkx as nx
import string
import random

def generate_tree(n):
    """Generate a directed tree with n nodes and root 'A'"""
    # Create a random undirected tree
    tree = nx.random_tree(n)

    # Convert the tree to a directed one making 'A' the root
    edges = nx.bfs_edges(tree, source=0)  # BFS ensures hierarchical top-down structure
    directed_tree = nx.DiGraph(edges)

    return directed_tree

def generate_graph(n, m):
	directed = random.randint(0,1)
	if (directed == 1):
		graph = nx.gnm_random_graph(n, m, directed=True)
	else:
		graph = nx.gnm_random_graph(n,m,directed=False)
	return graph
def generate(data):
	#if inline == true: data["params"]["random-graph"] = inline data, else random

	#else: random.randint min-number-nodes, max-number-nodes
    n = random.randint(5, 10)  # Number of nodes; random between 5 and 10
    # Generate a random number of edges, ensuring it's less than the maximum possible to avoid duplicates
    m = random.randint(n-1, n*2)  # The number of edges; adjust as required, avoiding too sparse or too dense

    labels = list(string.ascii_uppercase)[:n]  # Generate n labels alphabetically

    # Generate a random directed graph
	
	#pass in directed = true or false based on argument
    random_graph = generate_graph(n, m)

    # Label the nodes with alphabetical labels
    label_mapping = {i: labels[i] for i in range(n)}
    random_graph = nx.relabel_nodes(random_graph, label_mapping)

    # Convert the graph to the format expected by Prairie Learn and store in params
    data["params"]["random-graph"] = pl.to_json(random_graph)  # use node_link_data for serialization


def parse(data):
	pass
	
def grade(data):
    user_selected_nodes = eval(pl.from_json(data["submitted_answers"]["selectedNodes"]))
    score = 0
    dfs_final_graph =  ["A", "B", "D", "F", "H", "I", "G", "", ""]
  # Your list of correct nodes
    #if preserve-order == true: check ordering of nodes by checking user_selected_nodes.index
    for i in range(len(user_selected_nodes)):
        if dfs_final_graph[i] == user_selected_nodes[i]:
            score += 1
    
    data["score"] = score/len(dfs_final_graph)


"""
data = {}
data["params"] = {}
generate(data)
print(data)
print(sma())
"""
