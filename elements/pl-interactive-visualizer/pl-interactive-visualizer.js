// pl-interactive-visualizer.js

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

    let currentPoint = null;
    let selectedColormap = "Colour Palette 2";

    const colormapMap = {
        "Colour Palette 1": 'Viridis',
        "Colour Palette 2": 'Cividis',
        "Colour Palette 3": 'Inferno',
        "Colour Palette 4": 'Jet'
    };

    const layout = {
        scene: {
            aspectmode: "manual",
            aspectratio: { x: 1, y: 1, z: 0.7 },
            camera: { eye: { x: 1.5, y: 1.5, z: 1.5 } }
        },
        height: 600,
        width: 800,
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

        const pointTrace = currentPoint
            ? {
                type: 'scatter3d',
                mode: 'markers',
                x: [currentPoint.x],
                y: [currentPoint.y],
                z: [currentPoint.z],
                marker: { size: 5, color: 'red' },
                name: 'Selected Point'
            }
            : {
                type: 'scatter3d',
                mode: 'markers',
                x: [],
                y: [],
                z: [],
                marker: { size: 5, color: 'red' },
                name: 'Selected Point'
            };

        Plotly.newPlot('surfacePlot', [surface, pointTrace], layout).then(() => {
            const plotDiv = document.getElementById('surfacePlot');
            plotDiv.on('plotly_click', function (data) {
                if (currentPoint !== null) return;
                const pt = data.points[0];
                if (!pt || pt.x === undefined || pt.y === undefined || pt.z === undefined) return;
                currentPoint = { x: pt.x, y: pt.y, z: pt.z };
                document.getElementById('point-coordinates').innerText =
                    `Selected Point: x = ${pt.x.toFixed(2)}, y = ${pt.y.toFixed(2)}, z = ${pt.z.toFixed(2)}`;
                renderPlot();
            });
        });
    }

    document.querySelectorAll('.colormap-link').forEach((el) => {
        el.addEventListener('click', function (event) {
            event.preventDefault();
            const label = el.getAttribute('data-map');
            if (label in colormapMap) {
                selectedColormap = label;
                renderPlot();
            }
        });
    });
    

    document.getElementById('clearPointLink').addEventListener('click', function (event) {
        event.preventDefault();
        currentPoint = null;
        document.getElementById('point-coordinates').innerText = '';
        renderPlot();
    });

    renderPlot();
});
