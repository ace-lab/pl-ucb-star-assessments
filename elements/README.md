# pl-interactive-graph for PrairieLearn

## Overview
`pl-interactive-graph` is a custom interactive element for PrairieLearn, designed for creating and interacting with graph-based questions. It supports various functionalities like graph traversal, visualization, and interactive node selection.

## Usage
To use the `pl-interactive-graph` element in your PrairieLearn course:

1. **Include the Element in Your Question**: Embed the custom element tag in your question HTML file.
2. **Define the Graph**: Specify the graph structure within the tag using your desired graph generation method. Use DOT language to specify your graph, to learn how to use DOT language, navigate to https://graphviz.org/
3. **Set Attributes**: Customize the behavior and appearance of the graph using XML attributes. The element supports a variety of attributes to cater to different question types and requirements:
    - `preserve-ordering`: Boolean. If set to `True`, it requires the answer sequence to match exactly.
    - `answers`: String. String of an array of node labels representing the correct answer. (Example: "[A,B,C]")
    - `partial-credit`: Boolean. If set to `True`, it allows partial credit for partially correct sequences.
    - `directed`: Boolean. Specify whether the graph is directed.
    - `engine`: String. Defines the layout engine for graph rendering (default is `"dot"`).
    - `params-name-matrix`, `params-name`: String. Parameter names for matrix or other input types.
    - `weights`: Boolean. Determines if weights are displayed on the graph.
    - `weights-digits`: Integer. Number of digits to round the weights to.
    - `weights-presentation-type`: String. Format for presenting weights.
    - `params-name-labels`: String. Parameter name for node labels.
    - `params-type`: String. Type of graph representation, e.g., `"adjacency-matrix"` or `"networkx"`.
    - `negative-weights`: Boolean. Indicates if negative weights are to be shown.
    - `log-warnings`: Boolean. Toggles logging of warnings.

4. **Modify server.py if Needed**: Determine how would you want to grade the question, to access the order given by the student as the nodes were clicked, you can do student_answer = data["submitted_answers"]["user_answer"]. Note: If you have used custom attributes, like preserve-ordering or answer, this part might be different


## Description
The students will be presented with a graph of your specified structure and each node will be clickable. Students can click the node and depending on the element attribute values, the order might matter (they can also unclick nodes). A list of clicked nodes in the corresponding order will be shown on the left bottom of the question panel, to avoid clashes with the graph (still might happen for very large left leaning graphs). When the students click "submit" the element will record the clicked nodes and provide them to the backend.

## Suggested Use
This element is not only limited to purely graph traversal questions. Some of the possible problems that could be modelled by this element are (but not limited to): Network Flow, Finite State Machines, Pathfinding Algorithms, etc.

## Example
Here's an example of how you might use `pl-interactive-graph` in a question about graph traversal:

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


