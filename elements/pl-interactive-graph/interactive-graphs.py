import warnings
import random
import lxml.html
import networkx as nx
import numpy as np
import string
import prairielearn as pl
import pygraphviz


#Default pl-interactive-graph
PRESERVE_ORDERING=True
ANSWERS = []
PARTIAL_CREDIT = False
ENGINE_DEFAULT = "dot"
# Legacy default
PARAMS_NAME_MATRIX_DEFAULT = None
PARAMS_NAME_DEFAULT = None
PARAMS_NAME_LABELS_DEFAULT = None
PARAMS_TYPE_DEFAULT = "adjacency-matrix"
WEIGHTS_DEFAULT = None
WEIGHTS_DIGITS_DEFAULT = 2
WEIGHTS_PRESENTATION_TYPE_DEFAULT = "f"
NEGATIVE_WEIGHTS_DEFAULT = False
DIRECTED_DEFAULT = True
LOG_WARNINGS_DEFAULT = True


def graphviz_from_networkx(
    element: lxml.html.HtmlElement, data: pl.QuestionData
) -> str:
    input_param_name = pl.get_string_attrib(element, "params-name")

    networkx_graph = pl.from_json(data["params"][input_param_name])

    G = nx.nx_agraph.to_agraph(networkx_graph)

    return G.string()

def graphviz_from_adj_matrix(
    element: lxml.html.HtmlElement, data: pl.QuestionData
) -> str:
    # Legacy input with passthrough
    input_param_matrix = pl.get_string_attrib(
        element, "params-name-matrix", PARAMS_NAME_DEFAULT
    )
    input_param_name = pl.get_string_attrib(element, "params-name", input_param_matrix)

    # Exception to make typechecker happy.
    if input_param_name is None:
        raise ValueError('"params-name" is a required attribute.')

    input_label = pl.get_string_attrib(
        element, "params-name-labels", PARAMS_NAME_LABELS_DEFAULT
    )
    negative_weights = pl.get_boolean_attrib(
        element, "negative-weights", NEGATIVE_WEIGHTS_DEFAULT
    )

    mat = np.array(pl.from_json(data["params"][input_param_name]))
    show_weights = pl.get_boolean_attrib(
        element, "weights", WEIGHTS_DEFAULT
    )  # by default display weights for stochastic matrices
    digits = pl.get_integer_attrib(
        element, "weights-digits", WEIGHTS_DIGITS_DEFAULT
    )  # if displaying weights how many digits to round to
    presentation_type = pl.get_string_attrib(
        element, "weights-presentation-type", WEIGHTS_PRESENTATION_TYPE_DEFAULT
    ).lower()
    directed = pl.get_boolean_attrib(element, "directed", DIRECTED_DEFAULT)

    label = None
    if input_label is not None:
        label = np.array(pl.from_json(data["params"][input_label]))

    # Sanity checking

    if mat.shape[0] != mat.shape[1]:
        raise ValueError(
            f'Non-square adjacency matrix "{input_param_name}" of size ({mat.shape[0]}, {mat.shape[1]}) given as input.'
        )

    if label is not None:
        mat_label = label
        if mat_label.shape[0] != mat.shape[0]:
            raise ValueError(
                f'Dimension {mat_label.shape[0]} of the label "{input_label}"'
                f'is not consistent with the dimension {mat.shape[0]} of the matrix "{input_param_name}".'
            )
    else:
        mat_label = range(mat.shape[1])

    if not directed and not np.allclose(mat, mat.T):
        raise ValueError(
            f'Input matrix "{input_param_name}" must be symmetric if rendering is set to be undirected.'
        )

    # Auto detect showing weights if any of the weights are not 1 or 0

    if show_weights is None:
        show_weights = any(x not in {0, 1} for x in mat.flatten())

    # Create pygraphviz graph representation

    G = pygraphviz.AGraph(directed=directed)
    G.add_nodes_from(mat_label)

    for in_node, row in zip(mat_label, mat):
        for out_node, x in zip(mat_label, row):
            # If showing negative weights, show every entry that is not None
            # Otherwise, only show positive weights
            if x is None or (not negative_weights and x <= 0.0):
                continue

            if show_weights:
                G.add_edge(
                    out_node,
                    in_node,
                    label=pl.string_from_2darray(
                        x, presentation_type=presentation_type, digits=digits
                    ),
                )
            else:
                G.add_edge(out_node, in_node)

    return G.string()

def generate_graph(min_nodes, max_nodes, min_edges, max_edges, directed=False, weighted=False, tree=False ):
    n = random.randint(min_nodes, max_nodes)  
    if min_edges == 0:
        min_edges = n-1
    if max_edges == 0:
        max_edges = round(n*1.5)
    if tree:
        G = nx.random_tree(n, create_using=nx.DiGraph() if directed else nx.Graph())
        if directed:
            G = nx.DiGraph([(u, v) for u, v in G.edges()])
    else:
        # Generate a non-tree graph
        m = random.randint(min_edges, max_edges if not directed else n*(n-1) // 2 ) 
        G = nx.gnm_random_graph(n, m, directed=directed)
    if weighted==True:
        for (u, v) in G.edges():
            G.edges[u, v]['weight'] = random.randint(1, 10) 

    ascii_labels = list(string.ascii_letters[:n])  # Get the first 'n' ASCII letters
    mapping = {i: ascii_labels[i] for i in range(n)}  # Create a mapping from numeric to ASCII labels
    G = nx.relabel_nodes(G, mapping)

    return G

def prepare(element_html: str, data: pl.QuestionData) -> None:
    optional_attribs = [
        "preserve-ordering",
        "answers",
        "partial-credit",
        "node_fill_color",
        "edge_fill_color",
        "select_nodes",
        "select_edges",
        "random_graph",
        "directed_random",
        "min_nodes",
        "max_nodes",
        "min_edges",
        "max_edges",
        "weighted",
        "tree",
        "engine",
        "directed",
        "params-name-matrix",
        "params-name",
        "weights",
        "weights-digits",
        "weights-presentation-type",
        "params-name-labels",
        "params-type",
        "negative-weights",
        "log-warnings",
    ]

    # Load attributes from extensions if they have any
    extensions = pl.load_all_extensions(data)
    for extension in extensions.values():
        if hasattr(extension, "optional_attribs"):
            optional_attribs.extend(extension.optional_attribs)

    element = lxml.html.fragment_fromstring(element_html)
    pl.check_attribs(element, required_attribs=[], optional_attribs=optional_attribs)

def render(element_html: str, data: pl.QuestionData) -> str:

    # Get attribs
    element = lxml.html.fragment_fromstring(element_html)
    engine = pl.get_string_attrib(element, "engine", ENGINE_DEFAULT)
    log_warnings = pl.get_boolean_attrib(element, "log-warnings", LOG_WARNINGS_DEFAULT)
    node_fill_color = pl.get_string_attrib(element, "node_fill_color", "red")
    edge_fill_color = pl.get_string_attrib(element, "edge_fill_color", "red")

    select_nodes = pl.get_string_attrib(element, "select_nodes", "True")
    select_edges = pl.get_string_attrib(element, "select_edges", True)
    random_graph = pl.get_string_attrib(element, "random_graph", False)

    #if random_graph is true, generate a random graph instead of using existing functions
    if random_graph=="True":
        min_nodes = pl.get_integer_attrib(element, "min_nodes", 5)
        max_nodes = pl.get_integer_attrib(element, "max_nodes", 10)
        min_edges = pl.get_integer_attrib(element, "min_edges", 0)
        max_edges = pl.get_integer_attrib(element, "max_nodes", 0)
        directed_random = pl.get_boolean_attrib(element, "directed_random", False)
        weighted = pl.get_boolean_attrib(element, "weighted", False)
        tree = pl.get_boolean_attrib(element, "tree", False)

        networkx_graph = generate_graph(min_nodes, max_nodes, min_edges, max_edges, directed_random, weighted, tree)
        agraph = nx.nx_agraph.to_agraph(networkx_graph)

        if weighted:
            for edge in agraph.edges():
                u, v = edge
                edge.attr['label'] = networkx_graph[u][v]['weight']

        graphviz_data = agraph.string()
    else:
        # Original logic to choose between networkx and adjacency matrix based on input_type
        matrix_backends = {
            "adjacency-matrix": graphviz_from_adj_matrix,
            "networkx": graphviz_from_networkx,
        }
        #load color
        # Load all extensions
        extensions = pl.load_all_extensions(data)
        for extension in extensions.values():
            matrix_backends.update(extension.backends)
        # Legacy input with passthrough
        input_param_matrix = pl.get_string_attrib(
            element, "params-name-matrix", PARAMS_NAME_DEFAULT
        )
        input_param_name = pl.get_string_attrib(element, "params-name", input_param_matrix)

        input_type = pl.get_string_attrib(element, "params-type", PARAMS_TYPE_DEFAULT)

        if len(str(element.text)) == 0 and input_param_name is None:
            raise ValueError(
                "No graph source given! Must either define graph in HTML or provide source in params."
            )

        if input_param_name is not None:
            if input_type in matrix_backends:
                graphviz_data = matrix_backends[input_type](element, data)
            else:
                raise ValueError(f'Unknown graph type "{input_type}".')
        else:
            # Read the contents of this element as the data to render
            # we dump the string to json to ensure that newlines are
            # properly encoded
            graphviz_data = element.text

    translated_dotcode = pygraphviz.AGraph(string=graphviz_data)

    with warnings.catch_warnings():
        # Only apply ignore filter if we enable hiding warnings
        if not log_warnings:
            warnings.simplefilter("ignore")
        svg = translated_dotcode.draw(format="svg", prog=engine).decode(
            "utf-8", "strict"
        )
    javascript_function = f"""
    <input type="hidden" id="selectedNodes" name="selectedNodes" value="">
    <input type="hidden" id="selectedEdges" name="selectedEdges" value="">
    <div id="selectedNodeList"></div>
    <div id="selectedEdgeList"></div>
    <script>
    function clickable() {{
    window.addEventListener('DOMContentLoaded', (event) => {{
        let nodes = document.querySelectorAll('.node > ellipse');
        let edges = document.querySelectorAll('.edge > path');
        let selectedNodes = []; // Array to store selected node labels
        let selectedEdges = [];
        let nodeFillColor = "{node_fill_color}";
        let edgeFillColor = "{edge_fill_color}";

        let selectNodes = "{select_nodes}"
        let selectEdges = "{select_edges}"
        // Ensure text elements do not intercept mouse events
        let nodeTexts = document.querySelectorAll('.node > text');
        nodeTexts.forEach(text => {{
            text.style.pointerEvents = 'none';
        }});
        
        // Move edge labels to the right by 5 units
        document.querySelectorAll('.edge text[text-anchor="middle"]').forEach(function(text) {{
            var currentX = parseFloat(text.getAttribute('x'));
            var newX = currentX + 5;
            text.setAttribute('x', newX.toString());
         }});



        if (selectNodes == "True") {{
            document.getElementById("selectedNodeList").style.visibility= "visible";
            nodes.forEach(node => {{
                // Set a transparent fill for each ellipse
                node.setAttribute('fill', 'rgba(0,0,0,0)');

                node.addEventListener('click', function(event) {{
                    event.stopPropagation();

                    // Get the ID of the node, which should ideally be its label/name
                    // and get the text content of the sibling <text> node
                    let nodeId = node.parentNode.getAttribute("id"); // Get the ID of the node
                    let nodeLabel = node.parentNode.querySelector("text").textContent; // Get the text content of the node

                    // Toggle node stroke color

                    //instead of red, do select-color
                    if (node.getAttribute('fill') !== nodeFillColor) {{
                        node.setAttribute('fill', nodeFillColor);
                        selectedNodes.push(nodeLabel); // Add to selected nodes, using the text label
                    }} else {{
                        node.setAttribute('fill', 'rgba(0,0,0,0)'); // changed to transparent instead of white
                        const index = selectedNodes.indexOf(nodeLabel); // Use nodeLabel instead of nodeId
                        if (index > -1) {{
                            selectedNodes.splice(index, 1)// Remove from selected nodes
                        }}
                    }}

                    // Update the hidden input with the current list of selected nodes
                    document.getElementById("selectedNodes").value = JSON.stringify(selectedNodes);
                    updateNodeListDisplay(selectedNodes);

                }});
            }})
            }};
            if (selectEdges == "True") {{
                    document.getElementById("selectedEdgeList").style.visibility= "visible";

                    edges.forEach(edge => {{
                        edge.setAttribute('stroke-width', '5'); 
                        }});
                edges.forEach(edge => {{
                    edge.addEventListener('click', function(event) {{
                        event.stopPropagation();
                        let edgeTitle = edge.parentNode.querySelector('title').textContent;

                        if (!selectedEdges.includes(edgeTitle)) {{
                            edge.setAttribute('stroke', edgeFillColor); // Use stroke for edge selection visual
                            edge.setAttribute('stroke-width', "5");
                            selectedEdges.push(edgeTitle);
                        }} else {{
                            edge.setAttribute('stroke', 'black'); // Reset to default or specify non-selected stroke color
                            const index = selectedEdges.indexOf(edgeTitle);
                            if (index > -1) {{
                                selectedEdges.splice(index, 1);
                            }}
                        }}

                        document.getElementById("selectedEdges").value = JSON.stringify(selectedEdges);
                        updateEdgeListDisplay(selectedEdges); // Format for display
                    }});
                }})
            }};

    }});

    function updateNodeListDisplay(selectedNodes) {{
    let listHTML = selectedNodes.map((nodeLabel) => 
        `<li>${{nodeLabel}}</li>`
    ).join('');
    document.getElementById("selectedNodeList").innerHTML = `<ol>${{listHTML}}</ol>`;
    }}

    function updateEdgeListDisplay(selectedEdges) {{
    let listHTML = selectedEdges.map(edgeTitle => 
        `<li>${{edgeTitle}}</li>`
    ).join('');

    document.getElementById("selectedEdgeList").innerHTML = `<ol>${{listHTML}}</ol>`; // Ensure you have a corresponding div for edges
}}
    }}
    clickable();
    </script>
    """
    return f'<div class="pl-graph">{svg}</div>{javascript_function}'

def grade(element_html, data):
    if len(data["submitted_answers"]["selectedNodes"]) == 0:
        data["partial_scores"]["score"] = {
        "score": 0,
        "weight": 1,
        "feedback": "no nodes selected",
        }
        return data
    user_selected_nodes = eval(data["submitted_answers"]["selectedNodes"])
    # Use 'submitted_answers' instead of data["submitted_answers"]
    score = 0
    element = lxml.html.fragment_fromstring(element_html)

    correct_answer = eval(pl.from_json(element.get("answers", "[]")))
    preserve_ordering = pl.from_json(element.get("preserve-ordering"))
    partial_credit = pl.from_json(element.get("partial-credit"))
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
