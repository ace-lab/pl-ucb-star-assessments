$(function () {
    // Get the function from the hidden div
    const functionString = $('#function-data').text().trim();
    const placeEnabled = $('#place-data').text().trim().toLowerCase() === 'true';
    
    // Create a function with access to Math functions
    const userFunction = new Function('x', 'y', `
        const { sin, cos, tan, exp, log, sqrt, pow, abs, min, max } = Math;
        return ${functionString};
    `);

    let size = 30;
    let x = [], y = [], z = [];

    for (let i = -size; i <= size; i++) {
        let xVal = i / 10;
        let xRow = [], yRow = [], zRow = [];
        for (let j = -size; j <= size; j++) {
            let yVal = j / 10;
            let zVal = userFunction(xVal, yVal);
            xRow.push(xVal);
            yRow.push(yVal);
            zRow.push(zVal);
        }
        x.push(xRow);
        y.push(yRow);
        z.push(zRow);
    }

    // allow up to 4 points
    let points = []; // array of {x,y,z}
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
            camera: { eye: { x: 1.5, y: 1.5, z: 1.5 } },
            xaxis: { title: {
                text: 'θ<sub>0</sub>',
                font: { size: 14 }
            } },
            yaxis: { title: {
                text: 'θ<sub>1</sub>',
                font: { size: 14 }
            } },
            zaxis: { title: {
                text: 'L(θ)',
                font: { size: 14 }
            } }
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

        // points trace
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
            if (placeEnabled) {
                const plotDiv = document.getElementById('surfacePlot');
                plotDiv.on('plotly_click', data => {
                    if (points.length >= maxPoints) return;  // already 4
                    const pt = data.points[0];
                    if (!pt || pt.x===undefined) return;
                    points.push({ x:pt.x, y:pt.y, z:pt.z });
                    updateCoordsDisplay();
                    renderPlot();
                });
            }
        });
    }

    // clear point button
    if (placeEnabled) {
        document.getElementById('clearPointLink').addEventListener('click', function (event) {
            event.preventDefault();
            points = [];
            updateCoordsDisplay();
            renderPlot();
        });
    }

    // show all coords below
    function updateCoordsDisplay() {
        if (!placeEnabled) return;
        const display = document.getElementById('point-coordinates');
        if (points.length === 0) {
            display.innerText = '';
        } else {
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
