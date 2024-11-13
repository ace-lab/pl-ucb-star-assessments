import re

def parse_dot(dot_string):
    # Normalize line endings and whitespace
    dot_string = dot_string.replace("\r", "").replace("\n", "")
    
    # Parse nodes and create a mapping from N identifiers to actual labels
    node_labels = set()
    
    # Node pattern to account for any whitespace around square brackets
    node_pattern = re.compile(r'(\w+)\s*\[label="([^"]+)",\s*shape=circle\]')
    for match in node_pattern.finditer(dot_string):
        node_id, label = match.groups()
        node_labels.add(label)  # We just need the label to count nodes

    edges = set()
    # Edge pattern to account for optional whitespace and positive/negative labels
    edge_pattern = re.compile(r'(\w+)\s*->\s*(\w+)\s*\[label="(-?\d+)"\]')
    for match in edge_pattern.finditer(dot_string):
        source_id, target_id, label = match.groups()
        edges.add((source_id, target_id))  # Track only the connections to count edges
    
    return node_labels, edges

def grade(data):
    # Define required number of nodes and edges
    required_node_count = 10
    required_edge_count = 12
    
    # Parse the student's answer
    student_dot = data['submitted_answers'].get('graphData', '')
    student_nodes, student_edges = parse_dot(student_dot)

    # Count nodes and edges
    node_count = len(student_nodes)
    edge_count = len(student_edges)

    # Check if the student's graph meets the requirements
    if node_count == required_node_count and edge_count == required_edge_count:
        data['score'] = 1  # Full credit if both criteria are met
    else:
        # Partial credit based on the proportion of correct nodes and edges
        node_score = min(node_count / required_node_count, 1)
        edge_score = min(edge_count / required_edge_count, 1)
        data['score'] = 0.5 * node_score + 0.5 * edge_score  # Weighted equally