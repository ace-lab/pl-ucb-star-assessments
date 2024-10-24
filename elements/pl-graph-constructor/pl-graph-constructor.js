(function() {
    // Variables
    var canvas, context;
    var nodes = [];
    var links = [];
    var selectedNode = null;
    var creatingLink = false;
    var tempLink = null;

    // Constants
    var nodeRadius = 20;

    // Initialize the canvas and event handlers
    function initialize() {
        canvas = document.getElementById('fsm-canvas');
        context = canvas.getContext('2d');

        canvas.addEventListener('mousedown', canvasMouseDown);
        canvas.addEventListener('mousemove', canvasMouseMove);
        canvas.addEventListener('mouseup', canvasMouseUp);

        draw();
    }

    // Event handlers
    function canvasMouseDown(e) {
        var mouse = getMousePos(e);
        var node = getNodeAt(mouse.x, mouse.y);

        if (node != null) {
            selectedNode = node;
            selectedNode.setMouseOffset(mouse.x, mouse.y);
            creatingLink = true;
            tempLink = new Link(selectedNode, { x: mouse.x, y: mouse.y });
        } else {
            // Create a new node if none is selected
            node = new Node(mouse.x, mouse.y);
            nodes.push(node);
            selectedNode = node;
        }
    }

    function canvasMouseMove(e) {
        var mouse = getMousePos(e);
        if (creatingLink && tempLink != null) {
            tempLink.to = { x: mouse.x, y: mouse.y };
        } else if (selectedNode != null) {
            selectedNode.move(mouse.x, mouse.y);
        }
    }

    function canvasMouseUp(e) {
        var mouse = getMousePos(e);
        if (creatingLink && tempLink != null) {
            var node = getNodeAt(mouse.x, mouse.y);
            if (node != null && node !== selectedNode) {
                // Create a new link
                links.push(new Link(selectedNode, node));
            }
        }
        selectedNode = null;
        creatingLink = false;
        tempLink = null;
    }

    // Drawing function
    function draw() {
        // Clear canvas
        context.clearRect(0, 0, canvas.width, canvas.height);

        // Draw links
        links.forEach(function(link) {
            link.draw(context);
        });

        // Draw temporary link
        if (tempLink != null) {
            tempLink.draw(context);
        }

        // Draw nodes
        nodes.forEach(function(node) {
            node.draw(context);
        });

        requestAnimationFrame(draw);
    }

    // Utility functions
    function getMousePos(event) {
        var rect = canvas.getBoundingClientRect();
        return {
            x: (event.clientX - rect.left) * (canvas.width / rect.width),
            y: (event.clientY - rect.top) * (canvas.height / rect.height)
        };
    }

    function getNodeAt(x, y) {
        for (var i = nodes.length - 1; i >= 0; i--) {
            if (nodes[i].containsPoint(x, y)) {
                return nodes[i];
            }
        }
        return null;
    }

    // Node class
    function Node(x, y) {
        this.x = x;
        this.y = y;
        this.offsetX = 0;
        this.offsetY = 0;
    }

    Node.prototype.setMouseOffset = function(mouseX, mouseY) {
        this.offsetX = this.x - mouseX;
        this.offsetY = this.y - mouseY;
    };

    Node.prototype.move = function(mouseX, mouseY) {
        this.x = mouseX + this.offsetX;
        this.y = mouseY + this.offsetY;
    };

    Node.prototype.draw = function(c) {
        // Draw the circle
        c.beginPath();
        c.arc(this.x, this.y, nodeRadius, 0, 2 * Math.PI, false);
        c.fillStyle = '#FFFFFF';
        c.fill();
        c.strokeStyle = '#000000';
        c.stroke();
    };

    Node.prototype.containsPoint = function(x, y) {
        var dx = this.x - x;
        var dy = this.y - y;
        return dx * dx + dy * dy <= nodeRadius * nodeRadius;
    };

    // Link class
    function Link(fromNode, toNode) {
        this.from = fromNode;
        this.to = toNode;
    }

    Link.prototype.draw = function(c) {
        c.beginPath();
        c.moveTo(this.from.x, this.from.y);
        c.lineTo(this.to.x, this.to.y);
        c.strokeStyle = '#000000';
        c.stroke();
    };

    // Start the initialization
    if (window.addEventListener) {
        window.addEventListener('load', initialize, false);
    } else if (window.attachEvent) {
        window.attachEvent('onload', initialize);
    }
})();
