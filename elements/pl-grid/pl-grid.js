$(function() {
  /* for question panel */
  const question_data = JSON.parse($("#question-data").val()); 
  const colors = question_data.colors; // all of the color assignments specified by the instructor
  const color_column = question_data.color_column // whether or not to color blocks according to column (will color the same as the first block in the column)
  
  let source_grid = GridStack.init({
    acceptWidgets: true, // allow dropping items from other grids (for deleting)
    disableResize: true,
    float: false
  }, '.source-grid');
  source_grid.load(question_data.source);

  initGridColors(source_grid.el, colors); // source blocks are colored

  let destination_grid = GridStack.init({
    acceptWidgets: true, // allow dropping items from other grids (for deleting)
    disableResize: true,
    float: true// prevent auto-rearranging that minimizes free space
  }, '.dest-grid');
  destination_grid.load(question_data.given);
  
  initGridColors(destination_grid.el, colors); // if prepoluation was set, dest blocks are colored

  /* for submission panel */
  document.querySelectorAll('.submission-data').forEach((input_element, index) => {
    let submission_data;
    try {
      submission_data = JSON.parse(input_element.value);
    } catch (e) {
      console.warn("Bad submission JSON", e);
      return;
    }
  
    const grid_container = input_element.previousElementSibling;
    const grid = GridStack.init({
      float: true,
      acceptWidgets: false,
      disableDrag: true,
      disableResize: true
    }, grid_container);
    grid.load(submission_data);

    setColorComplete(grid, colors);  // your coloring logic
  });
  

  /* for solution panel */
  let solution_data = []; 
  const solution_data_element = $("#solution-data");

  if (solution_data_element.length > 0) {
    try {
      solution_data = JSON.parse(solution_data_element.val());
    } catch (e) {
      console.warn("Invalid or missing #load-data-sol JSON");
    }

    let solution_grid;

    if (Array.isArray(solution_data) && solution_data.length > 0) {
      solution_grid = GridStack.init({
        acceptWidgets: false, // allow dropping items from other grids (for deleting)
        disableResize: true,
        float: true
      }, '.sol-grid');
      solution_grid.load(solution_data);

      setColorComplete(solution_grid, colors);
    }
  }
  

  /* removes duplicate source_grid blocks when dragged back into source_grid */
  source_grid.on('dropped', function(event, prev_widget, new_widget) { 
    let existing_widgets_html = source_grid.getGridItems();

    let duplicate_found = existing_widgets_html.some(widget_element_html => { 
      let node = widget_element_html.gridstackNode; 
      return node.id == new_widget.id; 
    });

    if (duplicate_found) {
      source_grid.removeWidget(new_widget.el); 
    }

    setAnswer(); // update student answer
  });

  /* duplicate blocks when dragged out of source_grid into destination_grid */
  destination_grid.on('dropped', function(event, prev_widget, new_widget) {
    source_grid.addWidget(
      { w: prev_widget.w, h: prev_widget.h, content: prev_widget.content, id: prev_widget.id }
    );

    if (color_column) {
      setColumnColor(destination_grid, new_widget.el);
    };

    setAnswer(); // update student answer
  });

  /* updates the student's answer in the hidden input field */
  function setAnswer() {
    let grid_cells = $(".dest-grid").children(); 
    let student_answers = [];

    for (const grid_cell of grid_cells) {
      let cell = $(grid_cell) // convert DOM to JQuery Object
      let answer_html = cell.find(".grid-stack-item-content").html().trim();
      let answer_x = cell.attr("gs-x");
      let answer_y = cell.attr("gs-y");
      let answer_w = cell.attr("gs-w");
      let answer_h = cell.attr("gs-h") || 1;

      student_answers.push({
        x: answer_x,
        y: answer_y,
        w: answer_w,
        h: answer_h,
        content: answer_html
      });
    }

    $("#answer-input").val(JSON.stringify(student_answers));
  }

  /* applies same color to the new block as the ones in the same column */
  function setColumnColor(grid, new_widget_el) {
    let column = new_widget_el.getAttribute('gs-x');
    let existing_widgets = grid.getGridItems();
    let color = null;
    
    for (const widget_element_html of existing_widgets) {
      let widget_column = widget_element_html.getAttribute('gs-x');

      if (column === widget_column) {
        let text = $(widget_element_html).text().trim();
        let current_color = colors[text];
        if (current_color && current_color.toLowerCase() !== "#ffffff") { // non-white
          color = current_color;
          break;
        }
      }
    }
  
    if (color) {
      $(new_widget_el).find('.grid-stack-item-content').css('background-color', color);
    } else {
      console.log('No color found for column:', column); 
    }
  }

  /* colors block based on color assignments set by the instructor */
  function initGridColors(grid_element, colors) {
    $(grid_element).find('.grid-stack-item-content').each(function () {
      let text = $(this).text().trim();

      if (text in colors) {
        $(this).css('background-color', colors[text]);
      }
    });
  }
  
  /* colors all of the blocks in corresponding submission grid */
  function setColorComplete(grid, colors) {
    initGridColors(grid.el, colors); // submission blocks are colored (only ones that were in original mappings)

    if (color_column) {
      let existing_widgets = grid.getGridItems();
      let color_mapping = {};
      
      // first pass: determine a color for each column
      for (const widget_element_html of existing_widgets) {
        const widget_column = widget_element_html.getAttribute('gs-x');
        const content = $(widget_element_html).find('.grid-stack-item-content').text().trim();

        // assign the first found color in this column (non-white)
        if (!(widget_column in color_mapping)) {
          const color = colors[content];
          if (color && color.toLowerCase() !== "#ffffff") {
            color_mapping[widget_column] = color;
          }
        }
      }

      // second pass: apply that color to all widgets in the same column
      for (const widget_element_html of existing_widgets) {
        const widget_column = widget_element_html.getAttribute('gs-x');
        const color = color_mapping[widget_column];
        if (color) {
          $(widget_element_html).find('.grid-stack-item-content').css('background-color', color);
        }
      }
    }
  }
});
