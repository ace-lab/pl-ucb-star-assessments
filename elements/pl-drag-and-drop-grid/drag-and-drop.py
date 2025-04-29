import lxml.html
import prairielearn as pl
import ast

# Constants for default values
DEFAULT_NUM_COLS = 4
DEFAULT_NUM_ROWS = 4
DEFAULT_BLOCKED_CELLS = ''
DEFAULT_ITEMS = '' 
DEFAULT_POOL_TYPE = "finite"
DEFAULT_ANSWER = ''
PARTIAL_CREDIT = False

def prepare(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)
    data['params']['num_rows'] = pl.get_integer_attrib(element, "num_rows", DEFAULT_NUM_ROWS)
    data['params']['num_cols'] = pl.get_integer_attrib(element, "num_cols", DEFAULT_NUM_COLS)
    data['params']['items'] = pl.get_string_attrib(element, "items", DEFAULT_ITEMS)
    data['params']['pool_type'] = pl.get_string_attrib(element, "pool_type", DEFAULT_POOL_TYPE)
    data['params']['blocked_cells'] = pl.get_string_attrib(element, "blocked_cells", DEFAULT_BLOCKED_CELLS)

def render(element_html: str, data: pl.QuestionData) -> str:
    num_rows = data['params']['num_rows']
    num_cols = data['params']['num_cols']
    pool_type = data['params']['pool_type']
    blocked_cells_input = data['params']['blocked_cells']
    if pool_type == "infinite":
        data_infinite = "true"
        
    else:
        data_infinite = "false"
    
    if blocked_cells_input.strip():  # Checks if the string is not empty and not just whitespace
        try:
            blocked_cells = ast.literal_eval(blocked_cells_input)
        except SyntaxError as e:
            print(f"Error parsing blocked_cells: {e}")
            blocked_cells = []
    else:
        blocked_cells = []
    items = [item.strip() for item in data['params']['items'].split(',')]

    # Building the grid HTML
    grid_html = '<div id="grid-container">\n'
    for row in range(num_rows):
        grid_html += f'<div class="grid-row" style="grid-template-columns: repeat({num_cols}, 50px);">\n'
        for col in range(num_cols):
            cell_class = "grid-cell"
            if (row, col) in blocked_cells:
                cell_class = "blocked"
            grid_html += f'<div class="{cell_class}" data-row="{row}" data-col="{col}"></div>\n'
        grid_html += '</div>\n'
    grid_html += '</div>\n'

    # Building the items HTML
    items_html = '<div class="draggable-items">\n'
    for item in items:
        items_html += f'<div class="draggable" draggable="true" data-infinite="{data_infinite}" id="{item}">{item}</div>\n'
    items_html += '</div>\n'

    javascript_function = """
    <script>
        document.addEventListener('DOMContentLoaded', (event) => {{
        
            // Initialize the grid state as a 2D array filled with empty strings
            let grid_state = Array.from({{ length: {num_rows} }}, () => Array.from({{ length: {num_cols} }}, () => ''));

            function updateGridState() {{
                document.getElementById("grid_state").value = JSON.stringify(grid_state);
                console.log(grid_state);
            }}

            function dragStart(event) {{
                // Set the id of the draggable element as the data to be transferred
                event.dataTransfer.setData('text/plain', event.target.id);
                const isInfiniteSource = event.target.hasAttribute('data-infinite');
                event.dataTransfer.setData('isInfiniteSource', isInfiniteSource);
            }}

            function dragOver(event) {{
                event.preventDefault();
            }}

            


            function drop(event) {{
                event.preventDefault();
                const id = event.dataTransfer.getData('text/plain');
                let draggable = document.getElementById(id);
                let targetCell = event.target.closest('.grid-cell');

                if (targetCell.classList.contains('blocked')) {{
                    console.log('This cell is blocked.');
                    return;
                }}



                let newRow = parseInt(targetCell.dataset.row);
                let newCol = parseInt(targetCell.dataset.col);

                if (draggable.getAttribute('data-infinite') === 'true') {{
                    console.log("should clone");
                    draggable = draggable.cloneNode(true);
                    draggable.removeAttribute('data-infinite');
                    draggable.id = `clone-${{id}}-${{Date.now()}}`;
                    draggable.addEventListener('dragstart', dragStart);
                    draggable.addEventListener('click', removeItemFromCell);
                }}

                if (!targetCell.hasChildNodes()) {{
                    // Clear previous location in grid state if applicable
                    if (draggable.dataset.row && draggable.dataset.col) {{
                        grid_state[draggable.dataset.row][draggable.dataset.col] = '';
                    }}

                    // Update new location in grid state
                    draggable.dataset.row = newRow;
                    draggable.dataset.col = newCol;
                    targetCell.appendChild(draggable);
                    draggable.classList.add('in-grid');
                    grid_state[newRow][newCol] = draggable.textContent;

                    // Ensure the grid state is updated properly
                    updateGridState();
                }}
            }}


            function mouseEnter(event) {{
                // This function adds a red X to the draggable item
                const draggable = event.target;
                const overlay = document.createElement('span');  // Create a new span element for the overlay
                overlay.textContent = 'X';  // Set the text content of the span to 'X'
                overlay.style.color = 'red';  // Set the color of the text to red
                overlay.style.position = 'absolute';  // Position absolutely to overlay on the draggable
                overlay.style.right = '5px';  // Position towards the right of the container
                overlay.style.top = '0';  // Position at the top of the container
                overlay.style.fontSize = '24px';  // Set a larger font size for visibility
                overlay.style.fontWeight = 'bold';  // Make the font bold
                overlay.setAttribute('class', 'overlay-x');  // Add a class for potential additional styling
                draggable.appendChild(overlay);  // Append the overlay to the draggable
                console.log('jerenter');
            }}

            function mouseOut(event) {{
                // This function removes the red X from the draggable item
                const draggable = event.target;
                const overlay = draggable.querySelector('.overlay-x');  // Select the overlay span by its class
                if (overlay) {{
                    draggable.removeChild(overlay);  // Remove the overlay from the draggable
                }}
                console.log('jerout');
            }}

            function removeItemFromCell(event) {{
                const draggableItem = event.target.closest('.draggable'); // Ensure the target is always the draggable item
                if (draggableItem && draggableItem.classList.contains('draggable')) {{
                    const row = draggableItem.dataset.row;
                    const col = draggableItem.dataset.col;
                    
                    // Clear the grid state at the original location
                    if (row !== undefined && col !== undefined) {{
                        grid_state[row][col] = '';
                    }}

                    // Move the item back to the draggable area
                    if ({data_infinite} === "finite") {{
                        document.querySelector('.draggable-items').appendChild(draggableItem);
                    }} else {{
                        draggableItem.remove();
                    }}

                    draggableItem.classList.remove('in-grid');

                    // Clear the dataset attributes
                    delete draggableItem.dataset.row;
                    delete draggableItem.dataset.col;

                    // Update the grid state to reflect the changes
                    updateGridState();
                }}
            }}


            const draggables = document.querySelectorAll('.draggable');
            draggables.forEach(draggable => {{
                draggable.addEventListener('dragstart', dragStart);
                //draggable.addEventListener('mouseenter', mouseEnter);
                //draggable.addEventListener('mouseout', mouseOut)
                draggable.addEventListener('click', removeItemFromCell);
            }});

            const gridCells = document.querySelectorAll('.grid-cell');
            gridCells.forEach(cell => {{
                cell.addEventListener('dragover', dragOver);
                cell.addEventListener('drop', drop);
            }});

            updateGridState();
        }});
    </script>
    """.format(num_rows=num_rows, num_cols=num_cols, pool_type=pool_type, data_infinite=data_infinite)

    full_html = f'{items_html}{grid_html}{javascript_function}'
    full_html += '<input type="hidden" id="grid_state" name="grid_state" value="">'

    return full_html

def grade(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)
    grid_state = eval(data["submitted_answers"]["grid_state"])
    partial_credit = pl.from_json(element.get("partial_credit"))
    correct_answer = eval(pl.get_string_attrib(element, "answer", DEFAULT_ANSWER))
    num_rows = data['params']['num_rows']
    num_cols = data['params']['num_cols']
    num_items = 0
    num_correct = 0
    feedback = ""

    for i in range(num_rows):
        for j in range(num_cols):
            if correct_answer[i][j] != '':
                num_items += 1
                if grid_state[i][j] == correct_answer[i][j]:
                    num_correct += 1
                else:
                    feedback += f"{correct_answer[i][j]} is in the wrong place. "
            elif grid_state[i][j] != '':
                pass 

    if partial_credit == "False":
        score = 0
        if num_correct == num_items:
            score = 1
    else:
        score = max(num_correct / num_items, 0)

    if score == 1:
        feedback += "All correct!"

    data["partial_scores"]["score"] = {
        "score": score,
        "weight": 1,
        "feedback": feedback 
    }

    return data
