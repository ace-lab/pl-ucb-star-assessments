import re

def parse_dot(dot_string):
    # Normalize line endings and whitespace
    dot_string = dot_string.replace("\r", "").replace("\n", "")
    
    # Parse nodes and create a mapping from N identifiers to actual labels
    node_labels = {}
    
    # Node pattern to account for any whitespace around square brackets
    node_pattern = re.compile(r'(\w+)\s*\[label="([^"]+)",\s*shape=circle\]')
    for match in node_pattern.finditer(dot_string):
        node_id, label = match.groups()
        node_labels[node_id] = label

    edges = set()
    # Edge pattern to account for optional whitespace and positive labels
    edge_pattern = re.compile(r'(\w+)\s*->\s*(\w+)\s*\[label="(\d+)"\]')
    for match in edge_pattern.finditer(dot_string):
        source_id, target_id, label = match.groups()
        if source_id in node_labels and target_id in node_labels:
            # Use the mapped labels instead of node IDs
            edges.add((node_labels[source_id], node_labels[target_id], label))
    
    return node_labels.values(), edges

def grade(data):
    # Define the correct answer with label-based nodes and edges
    correct_nodes = {"A", "B"}
    correct_edges = {("A", "B", "1")}
    
    # Parse the student's answer
    student_dot = data['submitted_answers'].get('graphData', '')
    student_nodes, student_edges = parse_dot(student_dot)

    # Check nodes
    if set(student_nodes) != correct_nodes:
        data['score'] = 0  # No credit if nodes are incorrect
        return

    # Check if the student's edges match exactly the correct edges
    if student_edges == correct_edges:
        data['score'] = 1  # Full credit
    else:
        data['score'] = 0  # No credit