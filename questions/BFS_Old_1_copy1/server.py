import random
import chevron
import random, string, copy
import prairielearn as pl
import networkx as nx
import string
import random


def prepare(element_html, data):
    # Example values for each parameter
    data['params']['inline'] = True #mostly done
    data['params']['tree'] = False #done
    data['params']['preserve_ordering'] = True #done
    data['params']['select_color'] = 'blue' #Done?
    data['params']['min_number_nodes'] = 3 #done
    data['params']['max_number_nodes'] = 8 #done
    data['params']['answers'] = [1, 2, 3]  # done
    data['params']['partial_credit'] = True #done
    data['params']['partial_credit_method'] = 'COV' #done for cov/pc
    data['params']['graph'] = 'digraph G {A -> B}' #done
    return data

def render(element_html, data):
    html_params = {
        'inline': str(data['params']['inline']).lower(),
        'tree': str(data['params']['tree']).lower(),
        'preserve_ordering': str(data['params']['preserve_ordering']).lower(),
        'select_color': data['params']['select_color'],
        'min_number_nodes': data['params']['min_number_nodes'],
        'max_number_nodes': data['params']['max_number_nodes'],
        'answers': ','.join(map(str, data['params']['answers'])),
        'partial_credit': str(data['params']['partial_credit']).lower(),
        'partial_credit_method': data['params']['partial_credit_method'],
        'graph': data['params']['graph']
    }

    with open('interactive-graphs-mustache.mustache', 'r') as f:
        return chevron.render(f, html_params).strip()

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
    if data['params']['inline'] == False:

        #else: random.randint min-number-nodes, max-number-nodes
        n = random.randint(data['params']['min_number_nodes'], data['params']['max_number_nodes'])  # Number of nodes; random between 5 and 10
        # Generate a random number of edges, ensuring it's less than the maximum possible to avoid duplicates
        m = random.randint(n-1, n*2)  # The number of edges; adjust as required, avoiding too sparse or too dense

        labels = list(string.ascii_uppercase)[:n]  # Generate n labels alphabetically

        # Generate a random directed graph
        
        #pass in directed = true or false based on argument
        if data['params']['tree'] == True:
            random_graph = generate_tree(n)
        else:
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
    correct_answer = eval(data['params']['answers'])  # Your list of correct nodes
	#if preserve-order == true: check ordering of nodes by checking user_selected_nodes.index
    if data['params']['preserve_ordering'] == False:
        for i in correct_answer:
            if i in user_selected_nodes:
                score += 1
    else:
         for i in range(len(correct_answer)):
            if correct_answer[i] == user_selected_nodes[i]:
                 score += 1     
    if data['params']['partial_credit'] == False:
        if score == len(correct_answer) and len(correct_answer) == len(user_selected_nodes):
             data["score"] = 1
        else:
             data["score"] = 0

    else: 
        if data['params']['partial_credit_method'] == 'COV':
            data["score"] = score/len(correct_answer) * score/len(user_selected_nodes)
        elif data['params']['partial_credit_method'] == 'PC':
            score =  max(0, score-(len(user_selected_nodes)))

    data["score"] = score