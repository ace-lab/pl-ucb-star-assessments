class Visualizer {
  constructor(executionVisualizer) {
    this.executionVisualizer = executionVisualizer;
    this.vizLayoutTd = executionVisualizer.querySelector("#vizLayoutTdSecond")
  }

  getLastIndex(slug) {
    let index;
    let prevFrames = this.executionVisualizer.querySelectorAll('[id^="'+slug+'"]')
    let lastFrame = prevFrames[prevFrames.length - 1]
    if (!lastFrame) {
      index = 0 // This should never happen.
    } else {
      let str = lastFrame.id.substring(slug.length)
      let indexOfDash = str.indexOf("-");
      if (indexOfDash >= 0) {
        str = str.substring(0, indexOfDash)
      }
      index = parseInt(str) + 1
    }
    return index
  }

  add_variable_listener(e) {
    console.log(e)
    let button = e.target
    let frame = button.closest(".stackFrame")
    let variables = frame.querySelector(".stackFrameVarTable").children[0]
    let index = this.getLastIndex(frame.id + "-var-")
    //var newvar = document.createElement("div");
    if (frame.id == "frame-0") {
      variables.appendChild(this.make_variable(frame.id + "-var-" + index))
    } else {
      console.log(button)
      console.log(frame)
      let returnVal = frame.querySelector(".returnValueTr");
      console.log(variables)
      console.log(returnVal)
      variables.insertBefore(this.make_variable(frame.id + "-var-" + index), returnVal)
      this.updatePointerFrom(frame.id + "-return-val", false)
      this.updateAllPointers()
    }
  }

  make_variable(plKey, returnValue=false) {
    const tr = document.createElement("tr");
    tr.classList.add("variableTr", "removable", "removableSecondary")
    tr.id = plKey
    var varname; 
    if (returnValue) {
      tr.classList.add("returnValueTr")
      varname = document.createElement("span")
      varname.innerText = "Return Value"
    } else {
      varname = this.make_variable_length_input("stackFrameVarInput", plKey + "-name")
    }
    var stackframeval = this.make_value_box("stackFrameValueInput", plKey + "-val")
  
    var td = tr.insertCell();
    td.classList.add()
    if (!returnValue) {
      td.appendChild(this.make_remove_button(true));
    }
    var td = tr.insertCell();
    td.classList.add("stackFrameVar")
    td.appendChild(varname);
    var td = tr.insertCell();
    td.classList.add("stackFrameValue")
    td.appendChild(stackframeval);
    return tr;
  }
  
  make_remove_button(isSecondary) {
    let specialClass = isSecondary ? "removeButtonSecondary" : "removeButtonPrimary";
    var removeframe = document.createElement("button");
    removeframe.classList.add("btn", "removeButton", specialClass)
    removeframe.type = "button";
    removeframe.addEventListener("click", (e) => this.removeListener(e))
    return removeframe
  }
  
  removeListener(e) {
    let button = e.target
    let target = button.closest(".removable")
  
    // if (target.classList.contains("topLevelHeapObject")) {
    //   this.updatePointersTo(target.id, true)
    // } else if (target.classList.contains("stackFrame")) {
    //   for (let input of Array.from(executionVisualizer.getElementsByClassName("stackFrameValueInput"))) {
    //     this.updatePointerFrom(input.id, true)
    //   } 
    // } else if (target.classList.contains("variableTr")) {
    //   this.updatePointerFrom(target.getElementsByClassName("stackFrameValueInput")[0].id, true)
    // }

    // update the parent pointer dropdowns when a frame is deleted
    if (target.classList.contains("stackFrame")) {
      let frameHeader = target.querySelector(".frameHeader").textContent
      let frameIndex = frameHeader.substring(0, frameHeader.indexOf(":"))
      this.removeFrameFromDataList(frameIndex)

      target.parentElement.removeChild(target);
    } else if (target.classList.contains("sequenceElt")) {
      let heapObject = target.closest(".heapObject")
      let sequence = target.closest(".sequence")
      let sequenceContent = target.closest(".sequenceContent")
      let previousElement = target.previousElementSibling;
      let appendButton = target.querySelector(".sequenceAppendButtonContainer")
      sequenceContent.removeChild(target);
      if (appendButton) { // Only runs if we remove the last element
        if (sequenceContent.children.length > 0) {
          sequenceContent.children[sequenceContent.children.length - 1].appendChild(appendButton)
        } else {
          sequence.appendChild(appendButton)
        }
      }
      this.renumber_sequence_objects(sequenceContent, previousElement)
      this.fix_empty_sequence_type(heapObject, sequenceContent)
    } else {
      target.parentElement.removeChild(target);
    }

    this.updateAllPointers();
  }
  
  updateAllPointers(thorough) {
    for (let pointer of Array.from(this.executionVisualizer.querySelectorAll(".pointerArrow"))) {
      console.log(pointer)
      this.updatePointer(pointer, thorough)
    }
  }
  
  updatePointersTo(destinationId, remove) {
    for (let pointer of Array.from(this.executionVisualizer.querySelectorAll(".pointerTo-" + destinationId))) {
      console.log(pointer)
      if (remove) {
        this.removePointer(pointer)
      } else {
        this.updatePointer(pointer)
      }
    }
  }
  
  updatePointerFrom(originId, remove) {
    let pointer = this.executionVisualizer.querySelector("#pointer-" + originId);
    if (pointer == null) {
      return
    }
    if (remove) {
      this.removePointer(pointer)
    } else {
      this.updatePointer(pointer)
    }
  }
  
  make_parent_marker(elemType, plKey) {
    let marker = document.createElement(elemType);
    const dropdown = this.makeSelectInput("frameParentHeader", plKey + "-parent", "frame-indices")

    // construct "[Parent = <dropdown>]"
    marker.appendChild(document.createTextNode(" [Parent = "));
    marker.appendChild(dropdown);
    marker.appendChild(document.createTextNode("]"));
    return marker;
  }

  addFrameToDataList(frameIndex) {
    let dataList = this.executionVisualizer.querySelector("#frame-indices")
    let option = document.createElement("option")
    option.value = frameIndex;
    dataList.appendChild(option)
  }

  removeFrameFromDataList(frameIndex) {
    let dataList = this.executionVisualizer.querySelector("#frame-indices")
    for (let option of dataList.children) {
      if (option.value == frameIndex) {
        dataList.removeChild(option)
        return
      }
    }
  }
  
  make_value_box(className, plKey) {
    let container = document.createElement("div")
    container.className = "valueContainer"
    container.appendChild(this.make_variable_length_input(className, plKey))
    let pointerButton = document.createElement("button");
    pointerButton.className = "btn pointerButton pointerValueButton"
    pointerButton.type = "button"
    pointerButton.addEventListener("click", (e) => this.pointerValueToggleListener(e))
    container.appendChild(pointerButton)
    return container
  }
  
  make_variable_length_input(className, plKey) {
    let input = this.makeInput(className, plKey)
    let viz = this
    input.classList.add("varLengthInput")
    input.addEventListener("keyup", (e) => this.varLengthInputListener(e));
    input.addEventListener("keydown", (e) => this.varLengthInputListener(e));
    return input
  }

  varLengthInputListener(e) {
    let input = e.target
    this.updateInputLengthToContent(input)
  }
  
  makeInput(className, plKey) {
    let input = document.createElement("input")
    input.id = plKey
    input.name = plKey
    input.classList.add(className)
    input.value = ""
    return input
  }

  makeSelectInput(className, plKey, dataListId) {
    const dropdown = this.makeInput(className, plKey)
    dropdown.setAttribute("list", dataListId);
    dropdown.classList.add("selectInput")
    return dropdown
  }
  
  updateInputLengthToContent(input, ignorePointers) {
    let oldWidth = window.getComputedStyle(input).width
    input.style.minWidth = (input.value.length + 1) + "ch"
    if (!ignorePointers) {
      if (window.getComputedStyle(input).width != oldWidth) {
        this.updateAllPointers()
      } 
    }
  }
  
  updateAllInputLengthsToContent() {
    for (let input of this.executionVisualizer.querySelectorAll(".varLengthInput")) {
      this.updateInputLengthToContent(input, true)
    }
  }

  updateDropdowns() {
    // query for the dropdowns and frame names
    const frameNames = document.querySelectorAll(".frameHeader");
    const dropdowns = document.querySelectorAll(".frameParentHeader");

    // save selected elements (to later re-populate)
    const selectedOptions = [];
    dropdowns.forEach(dropdown => {
        selectedOptions.push(dropdown.value);
    });

    // clear the dropdown to re-render properly
    dropdowns.forEach(dropdown => {
        dropdown.innerHTML = "";

        // maintain an empty option for un-selected options
        const emptyOption = document.createElement("option");
        emptyOption.text = "";
        dropdown.add(emptyOption);
    });

    // pre-populate with global
    dropdowns.forEach(dropdown => {
        const globalOption = document.createElement("option");
        globalOption.value = "Global";
        globalOption.textContent = "Global";
        dropdown.add(globalOption);
    });

    // make new dropdowns
    frameNames.forEach(frameName => {
        const frameIndex = frameName.id.split('-')[1];

        // there were undefined frame indices popping up
        if (frameIndex !== undefined && frameIndex !== null) {
            const frameOption = document.createElement("option");
            frameOption.value = "f" + frameIndex;
            frameOption.textContent = "f" + frameIndex;

            // add in new option
            dropdowns.forEach(dropdown => {
                const clonedOption = frameOption.cloneNode(true);
                dropdown.add(clonedOption);
            });
        }
    });

    // restore selected value
    dropdowns.forEach((dropdown, index) => {
        dropdown.value = selectedOptions[index];
    });
  }

  
  add_frame() {
    let index = this.getLastIndex("frame-")
    var frame = document.createElement("div");
    var frame_name_label = document.createElement("label");
    var frame_name = this.make_variable_length_input("frameHeader", "frame-" + index + "-name")
    var table = document.createElement("table")
    table.className = "stackFrameVarTable"
    var variables = document.createElement("tbody");
    table.appendChild(variables)
    var variable_button = document.createElement("button");
    
    frame.classList.add("stackFrame", "removable", "removablePrimary");
    frame_name_label.className = "frameHeader";
      
    let removeframe = this.make_remove_button(false);
    
    variable_button.className = "btn"
    variable_button.type = "button"
    variable_button.innerHTML = "Add variable";
    variable_button.onclick = ((e) => this.add_variable_listener(e))
  
  
    frame_name_label.innerHTML = "f" + index + ": ";
    frame_name_label.inner
    variables.appendChild(this.make_variable("frame-" + index + "-return", true))
  
    frame.id = "frame-" + index
    
    frame.appendChild(removeframe);
    frame.appendChild(frame_name_label);
    frame.appendChild(frame_name);
    frame.appendChild(this.make_parent_marker("label", "frame-" + index));
    frame.appendChild(table);
    frame.appendChild(variable_button);
  
    this.executionVisualizer.querySelector("#globals_area").appendChild(frame);
    this.addFrameToDataList("f" + index)
    this.updateAllPointers();
    return frame
  }
  
  add_heap_object(id, content, typeName) {
    let topLevelHeapObject = document.createElement("div")
    topLevelHeapObject.classList.add("topLevelHeapObject", "removable", "removablePrimary")
    topLevelHeapObject.id = id;
    let heapObject = document.createElement("div")
    heapObject.className = "heapObject";
    topLevelHeapObject.appendChild(heapObject)

    let header = document.createElement("div")
    
    if (typeName instanceof HTMLElement) {
      header.appendChild(typeName)
    } else {
      let typeMarker = document.createElement("div")
      header.appendChild(typeMarker)
      typeMarker.className = "typeLabel"
      typeMarker.innerText = typeName
    }

    header.appendChild(this.make_remove_button(false))

    heapObject.append(header)
    heapObject.appendChild(content)
    this.executionVisualizer.querySelector("#heap").appendChild(topLevelHeapObject);
    this.updateAllPointers();
  }
  
  add_function_object() {
    let index = this.getLastIndex("heap-func-")
    let funcObj = document.createElement("div")
    funcObj.classList.add("funcObj")
    funcObj.innerText = "func "
    let funcNameInput = this.make_variable_length_input("funcNameInput", "heap-func-" + index + "-name")
    funcObj.appendChild(funcNameInput)
    funcObj.appendChild(this.make_parent_marker("span", "heap-func-" + index))
  
    this.add_heap_object("heap-func-" + index, funcObj, "function")
  }
  
  pointerValueToggleListener(e) {
    let button = e.target
    if (button.classList.contains("pointerButton")) {
      this.handlePointerClick(button);
    } else {
      this.handleValueClick(button);
    }
  }
  
  handlePointerClick(button) {
    let valueContainer = button.closest(".valueContainer")
    let valueInput = valueContainer.children[0]
    let pointer = this.makePointer("pointer-" + valueInput.id)
    let svg = pointer.children[0]
    let viz = this
    this.update_arrow_svg(this.relative_coordinates_obj_to_obj(valueInput, button), pointer)
  
    function mouseListener(mouseEvent) {
      let coords = viz.relative_coordinates_obj_to_pointer(valueInput, mouseEvent)
      viz.update_arrow_svg(coords, pointer)
    }
    this.executionVisualizer.addEventListener("mousemove", mouseListener)
    this.vizLayoutTd.appendChild(pointer)
  
    function clickListener(clickEvent) {
      clickEvent.stopPropagation()
      viz.executionVisualizer.removeEventListener("mousemove", mouseListener)
      let targetObj = clickEvent.target.closest(".topLevelHeapObject")
      if (targetObj == null) {
        viz.vizLayoutTd.removeChild(pointer)
        return 
      } 
      pointer.classList.add( "pointerTo-" + targetObj.id)
      
      viz.updatePointer(pointer, true)
    }
    this.executionVisualizer.addEventListener("click", clickListener, {
      capture: true,
      once: true
    })
  }
  
  handleValueClick(button) {
    let valueContainer = button.closest(".valueContainer")
    let valueInput = valueContainer.children[0]
    let pointerObj = this.executionVisualizer.querySelector("#pointer-" + valueInput.id)
    this.removePointer(pointerObj)
  }
  
  relative_coordinates_obj_to_pointer(obj1, mouseEvent) {
    let origin = this.vizLayoutTd.getBoundingClientRect()
    let pos1 = obj1.getBoundingClientRect()
    let x1 = pos1.x - origin.x + pos1.width/2
    let y1 = pos1.y - origin.y + pos1.height/2
    let x2 = mouseEvent.clientX - origin.x
    let y2 = mouseEvent.clientY - origin.y
    return [x1, y1, x2, y2]
  }
  
  relative_coordinates_obj_to_obj(obj1, obj2) {
    let origin = this.vizLayoutTd.getBoundingClientRect()
    let pos1 = obj1.getBoundingClientRect()
    let pos2 = obj2.getBoundingClientRect()
    let x1 = pos1.x - origin.x + pos1.width/2
    let y1 = pos1.y - origin.y + pos1.height/2
    let x2 = pos2.x - origin.x
    let y2 = pos2.y - origin.y + pos2.height/2
    return [x1, y1, x2, y2]
  }
  
  update_arrow_svg(coords, pointer) {
    let x1 = coords[0]
    let y1 = coords[1]
    let x2 = coords[2]
    let y2 = coords[3]
    let svg = pointer.children[0]
    let path = svg.children[0]
    let width = Math.abs(x2 - x1)
    let height = Math.abs(y2 - y1)
    let outerContainerX = Math.min(x1, x2)
    let outerContainerY = Math.min(y1, y2)
    svg.setAttribute("style", "top: " + outerContainerY + "px; left: " + outerContainerX + "px;")
    svg.setAttribute("width", width)
    svg.setAttribute("height", height)
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`)
    let pointerPathString = `M ${x1 - outerContainerX}, ${y1 - outerContainerY} L ${x2 - outerContainerX} ${y2 - outerContainerY}`;
    path.setAttribute("d", pointerPathString)
  }
  
  updatePointerDataInput(pointer) {
    let svg = pointer.children[0]
    let path = svg.children[0]
    let pointerDataInput = pointer.children[1]
    pointerDataInput.value = JSON.stringify({
      'd': path.getAttribute("d"),
      'width': svg.getAttribute("width"),
      'height': svg.getAttribute('height'),
      'top': svg.style.top,
      'left': svg.style.left
    })
  }
  
  // TODO: fix bug where changing widths mess things up. 
  updatePointer(pointer, thorough) {
    if (pointer == null) {
      return
    }
    let originId = pointer.id.substring("pointer-".length)
    let originElement = this.executionVisualizer.querySelector("#" + originId)
    let destinationId;
    for (let className of pointer.classList) {
      if (className.indexOf("pointerTo-") >= 0) {
        destinationId = className.substring("pointerTo-".length)
      }
    }
    let destinationElement = this.executionVisualizer.querySelector("#" + destinationId)
    if (originElement == null || destinationElement == null) {
      this.removePointer(pointer)
      return;
    }

    if (thorough) {
      originElement.value = "#" + destinationElement.id
      originElement.style.minWidth = ""
      originElement.classList.add("varLengthInputPointer")
      let button = originElement.nextElementSibling
      button.classList.add("valueButton")
      button.classList.remove("pointerButton")
    }

    this.update_arrow_svg(this.relative_coordinates_obj_to_obj(originElement, destinationElement), pointer)

    this.updatePointerDataInput(pointer)
  }
  
  removePointer(pointer) {
    pointer.parentElement.removeChild(pointer)
    let originId = pointer.id.substring("pointer-".length)
    let valueInput = this.executionVisualizer.querySelector("#" + originId)
    if (valueInput != null) {
      valueInput.value = ""
      valueInput.classList.remove("varLengthInputPointer")
      let button = valueInput.nextElementSibling
      button.classList.add("pointerButton")
      button.classList.remove("valueButton")
    }
  }
  
  makePointer(id) {
    let container = document.createElement("div")
    container.className = "pointerArrow"
    container.id = id;
    let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
    svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
    let newPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
    svg.appendChild(newPath)
    newPath.setAttribute("marker-end", "url(#pointerArrowHead)")
    container.appendChild(svg)
    let input = this.makeInput("pointerInput", id + "-input")
    container.appendChild(input)
    return container
  }
  
  add_sequence_object(typeName) {
    let index = this.getLastIndex("heap-" + typeName + "-")
    let sequenceObj = document.createElement("div")
    let plKey = "heap-" + typeName + "-" + index;
    sequenceObj.className = "sequence"
    let sequenceContent = document.createElement("div")
    sequenceContent.className = "sequenceContent"
    sequenceObj.appendChild(sequenceContent)
    let viz = this;
    let appendButton = this.make_sequence_add_button(function (e) {
      viz.sequenceAddButtonListener(e)
    }, false)
    sequenceObj.appendChild(appendButton)
    this.add_heap_object(plKey, sequenceObj, "empty " + typeName)
  }

  sequenceAddButtonListener(e) {
    let button = e.target
    let buttonContainer = button.parentElement
    let topLevelHeapObject = button.closest(".topLevelHeapObject")
    if (buttonContainer.classList.contains("sequenceAppendButtonContainer")) {
      this.add_list_element(null, topLevelHeapObject)
    } else {
      let sequenceElt = button.closest(".sequenceElt")
      this.add_list_element(sequenceElt, topLevelHeapObject)
    }
  }

  add_list_element(before, topLevelHeapObject) {
      let sequencePlKey = topLevelHeapObject.id;
      let sequence = topLevelHeapObject.querySelector(".sequence")
      let sequenceContent = topLevelHeapObject.querySelector(".sequenceContent")
      
      let index;
      if (before) {
        let input = before.querySelector("input")
        index = parseInt(input.id.split("-")[4])
      } else {
        index = sequenceContent.children.length
      }

      let elementId = sequencePlKey + "-item-" + index
      let viz = this
      let newElement = document.createElement("div")
      newElement.id = elementId
      newElement.classList.add("sequenceElt", "removable", "removableSecondary")
      newElement.appendChild(this.make_sequence_add_button(function(e) {
        viz.sequenceAddButtonListener(e)
      }, true))
      let elementHeader = document.createElement('div')
      elementHeader.classList.add("sequenceHeader")
      let sequenceEltIndex = document.createElement('span')
      sequenceEltIndex.classList.add("sequenceEltIndex")
      sequenceEltIndex.textContent = index;
      elementHeader.appendChild(sequenceEltIndex)
      elementHeader.appendChild(this.make_remove_button(true))
      newElement.appendChild(elementHeader)
      let valueContainer = this.make_value_box("sequenceElementValueContainer", elementId + "-val")
      newElement.appendChild(valueContainer)

      if (before) {
        sequenceContent.insertBefore(newElement, before)
        this.renumber_sequence_objects(sequenceContent, newElement)
      } else { // In this case we are appending. 
        sequenceContent.appendChild(newElement)
        let appendButton = sequence.querySelector(".sequenceAppendButtonContainer")
        newElement.appendChild(appendButton)
      }

      this.fix_empty_sequence_type(sequence.closest(".heapObject"), sequenceContent)
      this.updateAllPointers();
  }

  make_sequence_add_button(listener, isPrepend) {
      let buttonContainer = document.createElement("div")
      buttonContainer.classList.add("sequenceAddButtonContainer")
      if (isPrepend) {
        buttonContainer.classList.add("sequencePrependButtonContainer")
      } else {
        buttonContainer.classList.add("sequenceAppendButtonContainer")
      }
      let button = this.make_add_button(listener)
      buttonContainer.appendChild(button)
      return buttonContainer;
  }

  fix_empty_sequence_type(heapObj, sequenceContent) {
    let typeLabel = heapObj.querySelector(".typeLabel")
    if (sequenceContent.children.length <= 0) {
      if (typeLabel.textContent.substring(0, 5) != "empty") {
        typeLabel.textContent = "empty " + typeLabel.textContent
      }
    } else {
      if (typeLabel.textContent.substring(0, 5) == "empty") {
        typeLabel.textContent = typeLabel.textContent.substring(6)
      }
    }
  }
  
  renumber_sequence_objects(sequenceContent, item) {
    // Renumber the sequence after the specified item
    let comps;
    let index;
    if (sequenceContent.children.length <= 0) {
      return
    }
    if (!item) {
      item = sequenceContent.children[0]
      index = -1
      comps = item.id.split("-")
    } else {
      comps = item.id.split("-")
      index = parseInt(comps[4]);
      item = item.nextElementSibling;
    }
    while (item) {
      index += 1
      comps[4] = index
      let elementId = comps.join("-")

      let input = item.querySelector("input")
      if (input.value && input.value[0] == "#") { // Need to renumber the pointer object as well. 
        let pointerId = "pointer-" + input.id
        let pointerElement = this.executionVisualizer.querySelector("#" + pointerId)
        pointerElement.id = "pointer-" + elementId + "-val"
        let pointerInput = pointerElement.children[1]
        pointerInput.id = "pointer-" + elementId + "-val-input"
        pointerInput.name = "pointer-" + elementId + "-val-input"
      }
      input.id = elementId + "-val"
      input.name = elementId + "-val"
      item.id = elementId
      let indexContainer = item.querySelector(".sequenceEltIndex")
      indexContainer.textContent = index
      item = item.nextElementSibling;
    }
  }
  
  make_add_button(onclick) {
    var addButton = document.createElement("button");
    addButton.classList.add("btn", "addButton")
    addButton.type = "button";
    addButton.onclick = onclick
    return addButton
  }

  initializeStuff() {
    this.executionVisualizer.querySelectorAll('.addVarButton').forEach(x => x.addEventListener("click", (e) => this.add_variable_listener(e)))
    this.executionVisualizer.querySelectorAll('.removeButton').forEach(x => x.addEventListener("click", (e) => this.removeListener(e)))
    this.executionVisualizer.querySelectorAll('.varLengthInput').forEach(x => x.addEventListener("keydown", (e) => this.varLengthInputListener(e)))
    this.executionVisualizer.querySelectorAll('.pointerValueButton').forEach(x => x.addEventListener("click", (e) => this.pointerValueToggleListener(e)))
    this.executionVisualizer.querySelectorAll('.sequenceAddButtonContainer > button').forEach(x => x.addEventListener("click", (e) => this.sequenceAddButtonListener(e)))
    this.executionVisualizer.querySelectorAll('.varLengthInput').forEach(x => x.addEventListener("keyup", (e) => this.varLengthInputListener(e)))
    this.executionVisualizer.querySelector("#addFrameButton").addEventListener("click", (e) => this.add_frame(e))
    this.executionVisualizer.querySelector("#addFuncButton").addEventListener("click", (e) => this.add_function_object(e))
    this.executionVisualizer.querySelector("#addListButton").addEventListener("click", (e) => this.add_sequence_object("list"))
    this.executionVisualizer.querySelector("#addTupleButton").addEventListener("click", (e) => this.add_sequence_object("tuple"))
    this.updateAllInputLengthsToContent()
    this.updateAllPointers(true)
  }

  inactiveInitializeStuff() {
    this.updateAllInputLengthsToContent()
    //this.updateAllPointers(true)
  }
}

let activeExecutionVisualizer;
window.addEventListener('load', function() {
  activeExecutionVisualizer = document.querySelector('.ExecutionVisualizerActive')
  let viz = new Visualizer(activeExecutionVisualizer)
  viz.initializeStuff()

  for (let visualizerDOM of document.querySelectorAll('.ExecutionVisualizerInactive')) {
    let inactiveViz = new Visualizer(visualizerDOM)
    inactiveViz.inactiveInitializeStuff()
  }
});