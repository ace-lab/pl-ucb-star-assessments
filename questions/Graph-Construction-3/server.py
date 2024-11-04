import re

def parse_dot(dot_string):
    dot_string = ''.join(dot_string.split())
    
    node_labels = {}
    node_pattern = re.compile(r'(\w+)\[label="([^"]+)",shape=circle\]')
    for match in node_pattern.finditer(dot_string):
        node_id, label = match.groups()
        node_labels[node_id] = label

    edges = set()
    edge_pattern = re.compile(r'(\w+)->(\w+)\[label="(\d+)"\]')
    for match in edge_pattern.finditer(dot_string):
        source_id, target_id, label = match.groups()
        if source_id in node_labels and target_id in node_labels:
            edges.add((node_labels[source_id], node_labels[target_id], label))
    
    return edges

def grade(data):
    correct_edges = {
        ("S", "A", "3"),
        ("A", "S", "4"),
        ("C", "A", "4"),
        ("A", "B", "4"),
        ("S", "B", "5"),
        ("B", "T", "7"),
        ("C", "T", "2"),
        ("T", "C", "4")
    }
    
    student_dot = data['submitted_answers'].get('graphData', '')
    student_edges = parse_dot(student_dot)

    if student_edges == correct_edges:
        data['score'] = 1  
    else:
        data['score'] = 0  