$(function () {
    const container = $('.interactive-visualizer');

    const coeffX = 1.0;
    const expX = 2.0;
    const coeffY = 1.0;

    let size = 30;
    let x = [], y = [], z = [];

    for (let i = -size; i <= size; i++) {
        let xVal = i / 10;
        let xRow = [], yRow = [], zRow = [];
        for (let j = -size; j <= size; j++) {
            let yVal = j / 10;
            let zVal = coeffX * xVal + Math.pow(xVal, expX) * yVal + coeffY * yVal;
            xRow.push(xVal);
            yRow.push(yVal);
            zRow.push(zVal);
        }
        x.push(xRow);
        y.push(yRow);
        z.push(zRow);
    }

    // now allow up to 4 points
    let points = [];        // array of {x,y,z}
    const maxPoints = 4;

    let selectedColormap = "Color Palette 1";
    const colormapMap = {
        "Color Palette 1": 'Blackbody',
        "Color Palette 2": 'Electric',
        "Color Palette 3": 'Jet',
        "Color Palette 4": 'Hot',
        "Color Palette 5": 'Greys'
    };
    
    // dropdown handler
    document.getElementById('colormap-select')
    .addEventListener('change', e => {
        selectedColormap = e.target.value;
        renderPlot();
    });

    const layout = {
        scene: {
            aspectmode: "manual",
            aspectratio: { x: 1, y: 1, z: 0.7 },
            camera: { eye: { x: 1.5, y: 1.5, z: 1.5 } }
        },
        height: 600,
        width: 600,
        margin: { l: 0, r: 0, b: 0, t: 50 }
    };

    function renderPlot() {
        const surface = {
            type: 'surface',
            x: x,
            y: y,
            z: z,
            colorscale: colormapMap[selectedColormap],
            opacity: 0.9
        };

        // points trace (could be empty)
        const pointTrace = {
            type: 'scatter3d',
            mode: 'markers',
            x: points.map(p=>p.x),
            y: points.map(p=>p.y),
            z: points.map(p=>p.z),
            marker: { size:6, color:'red' },
            name: 'Selected Points'
        };

        // render
        Plotly.newPlot('surfacePlot', [surface, pointTrace], layout).then(() => {
            const plotDiv = document.getElementById('surfacePlot');
            plotDiv.on('plotly_click', data => {
                if (points.length >= maxPoints) return;  // already 4
                const pt = data.points[0];
                if (!pt || pt.x===undefined) return;
                points.push({ x:pt.x, y:pt.y, z:pt.z });
                updateCoordsDisplay();
                renderPlot();
            });

            // double‐click to clear all
            plotDiv.on('plotly_doubleclick', () => {
                points = [];
                updateCoordsDisplay();
                renderPlot();
            });
        });
    }

    // clear point button
    document.getElementById('clearPointLink').addEventListener('click', function (event) {
        event.preventDefault();
        points = [];
        updateCoordsDisplay();
        renderPlot();
    });

    // show all coords below
    function updateCoordsDisplay() {
        const display = document.getElementById('point-coordinates');
        if (points.length === 0) {
            display.innerText = '';
        } else {
            // list them "1: x=…, y=…, z=…; 2: …"
            display.innerText = points
              .map((p,i) =>
                  `Point ${i+1}: x=${p.x.toFixed(2)}, y=${p.y.toFixed(2)}, z=${p.z.toFixed(2)}`
              )
              .join('\n');
        }
    }

    renderPlot();
    updateCoordsDisplay();
});
