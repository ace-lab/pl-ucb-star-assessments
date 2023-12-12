function clickable() {
    document.addEventListener('DOMContentLoaded', (event) => {
        let nodes = document.querySelectorAll('.node > ellipse');
        let selectedNodes = []; // Array to store selected node labels
        // Ensure text elements do not intercept mouse events
        let nodeTexts = document.querySelectorAll('.node > text');
        nodeTexts.forEach(text => {
            text.style.pointerEvents = 'none';
        });

        nodes.forEach(node => {
            // Set a transparent fill for each ellipse
            node.setAttribute('fill', 'rgba(0,0,0,0)');

            node.addEventListener('click', function(event) {
                event.stopPropagation();

                // Get the ID of the node, which should ideally be its label/name
                // and get the text content of the sibling <text> node
                let nodeId = node.parentNode.getAttribute("id"); // Get the ID of the node
                let nodeLabel = node.parentNode.querySelector("text").textContent; // Get the text content of the node

                // Toggle node stroke color

                //instead of red, do select-color
                if (node.getAttribute('fill') !== select-color) {
                    node.setAttribute('fill', select-color);
                    selectedNodes.push(nodeLabel); // Add to selected nodes, using the text label
                } else {
                    node.setAttribute('fill', 'rgba(0,0,0,0)'); // changed to transparent instead of white
                    const index = selectedNodes.indexOf(nodeLabel); // Use nodeLabel instead of nodeId
                    if (index > -1) {
                        selectedNodes.splice(index, 1)// Remove from selected nodes
                    }
                }

                // Update the hidden input with the current list of selected nodes
                document.getElementById("selectedNodes").value = JSON.stringify(selectedNodes);
                updateNodeListDisplay(selectedNodes);

            });
        });
    });

    function updateNodeListDisplay(selectedNodes) {
    // Sort the array if you want the list to be in order of selection
    // selectedNodes.sort();

    let listHTML = selectedNodes.map((nodeLabel) => 
        `<li>${nodeLabel}</li>`
    ).join('');
    //if not preserve ordering, consider removing numbers from the side
    document.getElementById("selectedNodeList").innerHTML = `<ol>${listHTML}</ol>`;
    }
}