
# pl-interactive-graph for PrairieLearn

## Overview
`pl-interactive-graph` is a custom interactive element for PrairieLearn, designed for creating and interacting with graph-based questions. It supports various functionalities like graph traversal, visualization, and interactive node/edge selection. The element is built on top of the existing `pl-graph` element.

## Usage
To use the `pl-interactive-graph` element in your PrairieLearn course:

1. **Include the Element in Your Question**: Embed the custom element tag `<pl-interactive-graph>`in your question HTML file.
2. **Define the Graph**: Specify the graph structure within the tag using your desired graph generation method. Use DOT language to specify your graph, to learn how to use DOT language, navigate to https://graphviz.org/. *Note:* If you would like randomized graphs, you do not need need to use the DOT language.
3. **Set Attributes**: Customize the behavior and appearance of the graph using XML attributes. Attributes numbered 8-15 are used for random graphs. If you are not using a random graph, these attributes add nothing. Further, attributes 15 and on are part of the existing `pl-graph` element. The element supports a variety of attributes to cater to different question types and requirements: 
    1. `preserve-ordering`: String. If set to `"True"`, it requires the answer sequence to match exactly.
    2. `answers`: String. String of an array of node labels representing the correct answer. (Example: '["A","B","C"]')
    3. `partial-credit`: String. If set to `"True"`, it allows partial credit for partially correct sequences.
    4. `node-fill-color`: String. If set, changes the fill color of selected nodes to that color (default is "red").
    5. `edge-fill-color`: String. If set, changes the fill color of selected edges to that color (default is "green").
    6. `select-nodes`: Boolean. If set to `True`, it allows the user to click on nodes for selection for interaction.
    7. `select-edges`: Boolean. If set to `True`, it allows the user to click on edges for selection for interaction. 
    8. `random-graph`: Boolean. If set to `True`, random graphs will be generated.
    9. `directed-random`: Boolean. If set to `True`, random graphs will be generated with directed edges.
    10. `min-nodes`: Integer. Defines the minimum number of nodes in a random graph.
    11. `max-nodes`: Integer. Defines the maximum number of nodes in a random graph.
    12. `min-edges`: Integer. Defines the minimum number of edges in a random graph.
    13. `max-edges`: Integer. Defines the maximum number of edges in a random graph.
    14. `weighted`: Boolean. Specifies if a random graph should have random edge weights.
    15. `tree`: Boolean. Specifies if the random graph should be a tree. 
    16. `directed`: Boolean. Specify whether the graph is directed. 
    17. `engine`: String. Defines the layout engine for graph rendering (default is `"dot"`).
    18. `params-name-matrix`, `params-name`: String. Parameter names for matrix or other input types.
    19. `weights`: Boolean. Determines if weights are displayed on the graph.
    20.  `weights-digits`: Integer. Number of digits to round the weights to.
    21. `weights-presentation-type`: String. Format for presenting weights.
    22. `params-name-labels`: String. Parameter name for node labels.
    23. `params-type`: String. Type of graph representation, e.g., `"adjacency-matrix"` or `"networkx"`.
    24. `negative-weights`: Boolean. Indicates if negative weights are to be shown.
    25. `log-warnings`: Boolean. Toggles logging of warnings.
Some of the attributes have been inherited from pl-graph, here is more information on those specific inherited attributes: https://prairielearn.readthedocs.io/en/latest/elements/#pl-graph-element

4. **Modify server.py if Needed**: Determine how would you want to grade the question. To access the order given by the student as the nodes were clicked, you can do student_answer = data["submitted_answers"]["selectedNodes"]. Note: If you have used custom attributes, like preserve-ordering or answers, this part might be different. There is existing autograding if answers are provided in the `<pl-interactive-graph>` as `<pl-interactive-graph answers='["A","B","C"]'>`


## Description
The students will be presented with a graph of your specified structure and each node will be clickable. Students can click the node and depending on the element attribute values, the order might matter (they can also unclick nodes). A list of clicked nodes in the corresponding order will be shown on the left bottom of the question panel, to avoid clashes with the graph (still might happen for very large left leaning graphs). When the students click "submit" the element will record the clicked nodes and provide them to the backend.

## Suggested Use
This element is not only limited to purely graph traversal questions. Some of the possible problems that could be modelled by this element are (but not limited to): Network Flow, Finite State Machines, Pathfinding Algorithms, etc.

## Example
Different examples have been included in the questions folder. They are titled `pl-interactive-graph-examples/Clickable_Nodes_BFS_In_Order`, `pl-interactive-graph-examples/Clickable_Nodes_Basic_Interaction`, and `pl-interactive-graph-examples/Clickable_Nodes_Finite_State_Machine` Here's an example of how you might use `pl-interactive-graph` in a question about graph traversal:

```html
<p>
  What is the Breadth-First Search traversal order of this algorithm? Click the nodes in the order they are selected and click submit.
</p>
<pl-question-panel>
  <pl-interactive-graph 
    preserve-ordering="True" 
    partial-credit="True" 
    answers='["A","B","C","D","E","F","G","H","I"]'>
      graph G {
        A -- B;
        A -- C;
        B -- D;
        B -- E;
        C -- F;
        C -- G;
        E -- H;
        E -- I;
      }
  </pl-interactive-graph>
</pl-question-panel>


