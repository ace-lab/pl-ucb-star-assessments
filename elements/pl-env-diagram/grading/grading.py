try:
    import autoeval
except:
    import grading.autoeval as autoeval
import networkx as nx

def process_dict(d, keys_to_keep=[], entries_to_add = {}):
    d = {key: d[key] for key in keys_to_keep if key in d}
    d.update(entries_to_add)
    if 'val' in d:
        d['val'] = clean_value(d['val'])
    if 'name' in d:
        d['name'] = d['name'].strip()
    return d

def convert_parent_index_to_pl_key(parent_index):
    parent_index = parent_index.lower().strip()
    if parent_index[0] == "g":
        return "frame-0"
    else: 
        return "frame-" + parent_index[1:]
    
def clean_value(string):
    """Cleans a given value string."""
    string = string.strip()
    # This fix is dirty and should be revisited
    if string and string[0] == "'" and string[-1] == "'":
        string = "\"" + string[1: -1] + "\""
    return string
    
def add_value_node(G, node_name, value_obj, type_name):
    """Takes in a dictionary with 'val' as a key, 
    and possibly also 'name' as a key. Adds to graph G
    a node representing the value/binding, and """
    
    if value_obj['val'] and value_obj['val'][0] == "#":
        G.add_node(node_name, **process_dict(value_obj, ['name'], {'type': type_name}))
        G.add_edge(node_name, value_obj['val'][1:], type=type_name + "_pointer") # point to heap object
    else: 
        G.add_node(node_name, **process_dict(value_obj, ['name', 'val'], {'type': type_name}))

def make_graph(env_diagram_obj):
    G = nx.DiGraph()
    for frame in env_diagram_obj['frame']:
        this_frame_key = "frame-" + frame['frameIndex']
        G.add_node(this_frame_key, **process_dict(frame, ["name"], {'type': 'frame'}))
        if "parent" in frame:
            G.add_edge(convert_parent_index_to_pl_key(frame['parent']), this_frame_key, type="frame")
        if "var" in frame:
            for binding in frame['var']:
                binding_key = this_frame_key + "-var-" + str(binding['varIndex'])
                add_value_node(G, binding_key, binding, "binding")
    if 'heap' in env_diagram_obj: 
        for sequence_type_name in ("list", "tuple"):
            if sequence_type_name in env_diagram_obj["heap"]:
                for sequence in env_diagram_obj["heap"][sequence_type_name]:
                    sequence_key = "heap-" + sequence_type_name + "-" + str(sequence[sequence_type_name + "Index"])
                    G.add_node(sequence_key, type="sequence", sequence_type=sequence_type_name)
                    prev_node_name = sequence_key
                    if "item" in sequence: 
                        for item in sequence["item"]:
                            item_key = sequence_key + "-item-" + str(item['itemIndex'])
                            add_value_node(G, item_key, item, "item")
                            G.add_edge(prev_node_name, item_key, type="sequence")
                            prev_node_name = item_key
                    G.add_node(sequence_key + "-end", type="sequence_end", sequence_type=sequence_type_name)
                    G.add_edge(prev_node_name, sequence_key + "-end", type="sequence")
        if 'func' in env_diagram_obj['heap']:
            for function in env_diagram_obj['heap']['func']:
                function_key = 'heap-func-' + str(function['funcIndex'])
                G.add_node(function_key, **process_dict(function, ['name'], {'type': 'func'}))
                if "parent" in function:
                    G.add_edge(function_key, convert_parent_index_to_pl_key(function['parent']), type="func")
    return G

def round_grade(raw, num_steps):
    # Takes in a raw score and rounds it to the specified number of gradations.
    stepped = int(raw * num_steps) / num_steps
    return min(max(0, round(stepped, 3)), 1)

def grading(generated_json, student_json, granularity = 1):
    """ returns score and feedback (if applicable) for the student.
    
    To allow for partial credit, set the granularity to an integer greater than 1. 
    For example, if the granularity is set to 20, the student will
    earn a score to the nearest increment of 5% (1/20). 
    To disable partial credit, set the granularity to 1. 
    """
    correct_graph = make_graph(generated_json)
    submitted_graph = make_graph(student_json)

    if granularity > 1:
        def node_subst_cost(node1, node2):
            """Returns a number between 0 and 1"""
            if node1['type'] != node2['type']:
                return max_dist + 1
            type_name = node1['type']
            if type_name == "binding":
                if 'val' in node1 and 'val' in node2: 
                    return (node1['name'] != node2['name']) + (node1['val'] != node2['val'])
                else: 
                    return int(node1['name'] != node2['name'])
                # Note that in the case where there is one node that has a pointer and one node
                # that does not have a pointer, the error will be handled by the edge function.
            else:
                return int(node1 != node2)
            
        def node_del_cost(node):
            type_name = node['type']
            if type_name == "binding":
                return 2
            elif type_name == "sequence" or type_name == "sequence_end":
                return 0.5
            else: 
                return 1
            
        node_ins_cost = node_del_cost
            
        def edge_subst_cost(edge1, edge2):
            if edge1['type'] != edge2['type']:
                return max_dist + 1
            
            return int(edge2 != edge1)
        
        def edge_del_cost(edge):
            type_name = edge['type']
            if type_name == 'sequence':
                return 1/6
            else: 
                return 0.5
            
        edge_ins_cost = edge_del_cost

        max_dist = 0
        for _, data in correct_graph.nodes(data=True):
            max_dist += node_ins_cost(data)
        for _, _, data in correct_graph.edges(data=True):
            max_dist += edge_ins_cost(data)

        max_dist -= 1 # Account for the fact that global frame is given
            
        dist = nx.graph_edit_distance(
            submitted_graph, 
            correct_graph,
            node_subst_cost=node_subst_cost,
            node_del_cost=node_del_cost,
            node_ins_cost=node_ins_cost,
            edge_subst_cost=edge_subst_cost,
            edge_del_cost=edge_del_cost,
            edge_ins_cost=edge_ins_cost,
            upper_bound=max_dist
        )
        if dist is None: 
            return 0, ""
        return round_grade((max_dist - dist)/max_dist, granularity), ""
    elif granularity > 0.5:
        is_isomorphic = nx.is_isomorphic(submitted_graph, correct_graph, node_match=lambda x, y: x == y)
        return int(is_isomorphic), ""


def get_correctAnswerJSON(codestring):
    return autoeval.FrameTree(codestring).generate_html_json()