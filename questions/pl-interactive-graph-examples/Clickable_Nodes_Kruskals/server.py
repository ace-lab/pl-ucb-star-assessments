
def grade(element_html, data):

    element = lxml.html.fragment_fromstring(element_html)

    if len(data["submitted_answers"]["selectedNodes"]) < 3:
        data["partial_scores"]["score"] = {
        "score": 0,
        "weight": 1,
        "feedback": "no nodes selected",
        }
        return data
    

    #select_edges = pl.get_string_attrib(element_html, "select-edges", True)
    select_edges = pl.from_json(element.get("select-edges"))
    #print(select_edges)

    if select_edges:
        if len(data["submitted_answers"]["selectedEdges"]) < 3:
            data["partial_scores"]["score"] = {
            "score": 0,
            "weight": 1,
            "feedback": "no edges selected",
        }
        return data
    
    
    user_selected_nodes = eval(data["submitted_answers"]["selectedNodes"])
    if select_edges:
        user_selected_edges = eval(data["submitted_answers"]["selectedEdges"])

    # Use 'submitted_answers' instead of data["submitted_answers"]
    score = 0
    
    random_graph = data["submitted_answers"]["random-graph"]

    correct_answer = eval(pl.from_json(element.get("answers", "[]")))
    preserve_ordering = pl.from_json(element.get("preserve-ordering"))
    partial_credit = pl.from_json(element.get("partial-credit"))

    graph = pygraphviz.AGraph(string=random_graph)

    correct_answer = kruskals_agraph(graph)


    #print("user" + str(user_selected_nodes) + "answer" + str(correct_answer))
    if preserve_ordering != "True":
        for i in range(len(user_selected_nodes)):
            if user_selected_nodes[i] in correct_answer:
                score += 1
    else:
        for i in range(len(correct_answer)):
            if i < len(user_selected_nodes) and correct_answer[i] == user_selected_nodes[i]:
                score += 1
       
    if partial_credit != "True":
        if score != len(correct_answer):
            score = 0
        else:
            score = 1
    else:
        score = score/len(correct_answer)
    data["partial_scores"]["score"] = {
    "score": score,
    "weight": 1
    }
    return data




def dfs_agraph(agraph, start):
    visited = set()  # Set of visited nodes
    stack = [start]  # Stack for DFS
    order = []  # Order of visited nodes

    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            order.append(node)
            # Get successors of the node in reverse order to maintain the correct order when popped from stack
            stack.extend(reversed([n for n in agraph.successors(node) if n not in visited]))

    return order


def bfs_agraph(agraph, start_node):
    """
    Perform Breadth-First Search (BFS) starting from start_node.

    Parameters:
    - agraph (pgv.AGraph): The graph on which to perform BFS.
    - start_node (str): The starting node for BFS.

    Returns:
    list: A list of nodes in the order they were visited.
    """
    visited = set([start_node])  # Set of visited nodes
    queue = deque([start_node])  # Queue for BFS
    order = []  # Order of visited nodes

    while queue:
        # Dequeue a node from queue
        current_node = queue.popleft()
        order.append(current_node)

        # Visit all the unvisited neighbors
        for neighbor in agraph.successors(current_node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return order


    
def dijkstra_agraph(agraph, start_node):
    """
    Perform Dijkstra's algorithm to find the shortest paths from start_node to all other nodes in the graph,
    and return the order in which nodes are visited without duplicates.
    
    Parameters:
    - agraph (pgv.AGraph): The graph on which to perform Dijkstra's algorithm.
    - start_node (str): The starting node for the algorithm.
    
    Returns:
    list: A list of nodes in the order they are uniquely visited.
    """
    # Initialize distances from start_node to infinity, except for start_node itself which is 0
    distances = {node: float('inf') for node in agraph.nodes()}
    distances[start_node] = 0

    # Priority queue to select the node with the smallest distance
    pq = [(0, start_node)]
    
    # Set and list to record the order of visited nodes
    visited_set = set()
    visited_order = []
    
    while pq:
        # Pop the node with the smallest distance
        current_distance, current_node = heapq.heappop(pq)
        
        # Skip if this node has already been visited
        if current_node in visited_set:
            continue
        
        # Mark the current node as visited
        visited_set.add(current_node)
        visited_order.append(current_node)
        
        # Explore the neighbors of the current node
        for neighbor in agraph.successors(current_node):
            edge = agraph.get_edge(current_node, neighbor)
            
            try:
                # Extract the edge's label, which contains the weight as a string
                label = edge.attr.get('label')
                # If the label exists and is not None, convert it to float. Otherwise, use default weight.
                weight = float(label) if label is not None else 1.0
            except ValueError:
                # In case the label cannot be converted to float, use a default weight.
                weight = 1.0
            
            # Calculate new distance to the neighboring node
            distance = current_distance + weight
            
            # If the new distance is shorter, update the path and distances
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                # Use a tuple of (distance, neighbor) to maintain a min heap based on distance
                heapq.heappush(pq, (distance, neighbor))
    
    return visited_order




def find(parent, i):
    if parent[i] == i:
        return i
    return find(parent, parent[i])

def union(parent, rank, x, y):
    xroot = find(parent, x)
    yroot = find(parent, y)
    if rank[xroot] < rank[yroot]:
        parent[xroot] = yroot
    elif rank[xroot] > rank[yroot]:
        parent[yroot] = xroot
    else:
        parent[yroot] = xroot
        rank[xroot] += 1

def kruskals_agraph(agraph):
    """Performs Kruskal's algorithm on an AGraph object."""
    # Initialize result
    result = []  # This will store the resultant MST

    i, e = 0, 0  # Variables to store number of edges processed and added to MST

    # Step 1: Sort all the edges in non-decreasing order of their weight
    edges = [(float(edge.attr['label']), edge) for edge in agraph.edges()]
    edges.sort(key=lambda x: x[0])

    parent = {}
    rank = {}

    # Create V sets with single elements
    for node in agraph.nodes():
        parent[node] = node
        rank[node] = 0

    # Number of edges to be taken is equal to V-1
    while e < len(agraph.nodes()) - 1:
        # Step 2: Pick the smallest edge and increment the index for next iteration
        _, edge = edges[i]
        i += 1
        x = find(parent, edge[0])
        y = find(parent, edge[1])

        # If including this edge does not cause a cycle, include it in result
        # and increment the index of the result for the next edge
        if x != y:
            e += 1
            result.append(edge)
            union(parent, rank, x, y)

    # Format the result to match the specified format
    formatted_result = [f"{edge[0]}--{edge[1]}" for edge in result]
    return formatted_result

