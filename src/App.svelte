<script>
	import { onMount } from 'svelte';
	import Node from './Node.svelte';
	import CommandPalette from './CommandPalette.svelte';
	import Link from './Link.svelte';
	// import BuiltInNodes from './BuiltInNodes.svelte';
	import { checkCollision } from 'svg-path-intersections';
    // import PyodideTerm from './PyodideTerm.svelte';
    import PyodideRepl from './PyodideREPL.svelte';

	let pyodide; // Pyodide instance

	// some debug stuff
	let highlightPointer = false;
	let highlightPosition = { x: 0, y: 0 };

/* ---------------------------------------------------------------------------
 * Command undo/redo logic
 * ------------------------------------------------------------------------- */
	let commandHistory = [];
	let commandIndex = -1;

	function pushCommand(cmd) {
		// If we're in the middle of the history, overwrite the current command
		if (commandIndex < commandHistory.length - 1) {
			commandHistory = commandHistory.slice(0, commandIndex + 1);
		}
		commandHistory.push(cmd);
		commandIndex = commandHistory.length - 1;
	}

	function undo() {
		console.log("Undo { commandIndex: ", commandIndex, "}");
		if (commandIndex < 0) return;
		const cmd = commandHistory[commandIndex];
		if (cmd.undo) cmd.undo();
		commandIndex--;
	}

	function redo() {
		if (commandIndex >= commandHistory.length - 1) return;
		commandIndex++;
		const cmd = commandHistory[commandIndex];
		if (cmd.redo) cmd.redo();
	}


/* ---------------------------------------------------------------------------
* Drag n Drop Connection Logic
* ------------------------------------------------------------------------- */
	let startGraphCoords = { x: 0, y: 0 };
	let mouseGraphCoords = { x: 0, y: 0 };
	let activeCutConnection = null;
	let activeConnection = null; // e.g. { from: {...}, to: { x, y } }
  	let hoveredSocket = null;    // optional, if you want snapping
	let mouseX = 0;
	let mouseY = 0;

	// Called when user clicks on a socket in Node.svelte
	function handleSocketPointerDown(e) {
		console.debug( "SocketPointerDown" );
		const { nodeId, socketName, socketType, clientX, clientY } = e.detail;
		// Start a new connection
		let gc = screenToGraphCoords(e.clientX, e.clientY);
		activeConnection = {
			from: { nodeId, socketName, socketType },
			to:   { x: gc.x, y: gc.y }
		};
		// Listen for pointermove/pointerup globally
		window.addEventListener('pointermove', handleConnectionPointerMove);
		window.addEventListener('pointerup', handleConnectionPointerUp);
	}

	function handleConnectionPointerMove(e) {
		
		if (!activeConnection) return;
		
		let gc = screenToGraphCoords(e.clientX, e.clientY);
		// Update the 'to' position (graph coords)
		activeConnection.to.x = gc.x;
		activeConnection.to.y = gc.y;

		// If you want to highlight a potential drop target, find a nearby socket
		hoveredSocket = findNearestSocket(e.clientX, e.clientY);
	}

	function handleConnectionPointerUp(e) {
		// return;
		window.removeEventListener('pointermove', handleConnectionPointerMove);
		window.removeEventListener('pointerup', handleConnectionPointerUp);

		if (!activeConnection) return;


		// Check if pointer-up is on a valid socket
		const dropSocket = findNearestSocket(e.clientX, e.clientY);
		if (dropSocket) {
		// Create the connection in your graph data
		graphData.connections = [
			...graphData.connections,
			{
			from: {
				node: activeConnection.from.nodeId,
				output: (activeConnection.from.socketType === 'output')
				? activeConnection.from.socketName
				: dropSocket.socketName
			},
			to: {
				node: dropSocket.nodeId,
				input: (activeConnection.from.socketType === 'output')
				? dropSocket.socketName
				: activeConnection.from.socketName
			}
			}
		];
		}
		// Clear the active connection
		activeConnection = null;
		hoveredSocket = null;
	}

	// Draw the ghost path from the source socket to the mouse
	function computeActiveConnectionPath( conn ) {
		// console.log("activeConnection", activeConnection);
		if (!conn) return "";
		const source = getSocketScreenCoords(conn.from);
		if (!source || isNaN(source.cx) || isNaN(source.cy) ) return "";
		// If hoveredSocket is found, snap to that; else use the current mouse
		const targetX = hoveredSocket
		? hoveredSocket.cx
		: conn.to.x;
		const targetY = hoveredSocket
		? hoveredSocket.cy
		: conn.to.y;

		if (isNaN(targetX) || isNaN(targetY)) return "";

		const dx = Math.abs(targetX - source.cx) / 2;

		console.debug( `M ${source.cx} ${source.cy}
				C ${source.cx + dx} ${source.cy}
				${targetX - dx} ${targetY}
				${targetX} ${targetY}` );

		
		return `M ${source.cx} ${source.cy}
				C ${source.cx + dx} ${source.cy}
				${targetX - dx} ${targetY}
				${targetX} ${targetY}`;
	}

	function computeActiveCutConnectionPath( active, start, to ) {
		if (!active) return "";
		return `M ${start.x} ${start.y} L ${to.x} ${to.y}`;
	}

	// Reactive statement: recalc whenever activeConnection changes
	$: ghostPath = computeActiveConnectionPath(activeConnection);
	$: ghostCutPath = computeActiveCutConnectionPath( activeCutConnection, startGraphCoords, mouseGraphCoords );

	function getSocketScreenCoords({ nodeId, socketName, socketType }) {
		// 1) Find the node by ID
		const node = graphData.nodes.find(n => n.id === nodeId);
		if (!node) {
			console.log(`Node ${nodeId} not found`);
			return { cx: 0, cy: 0 };
		}

		// 2) Determine if we’re looking among inputs or outputs
		const sockets = (socketType === 'input') ? node.inputs : node.outputs;
		const index = sockets.findIndex(s => s.name === socketName);
		if (index < 0) {
			console.log(`Socket ${socketName} not found in node ${nodeId}`);
			return { cx: 0, cy: 0 };
		}

		// 3) Calculate the socket’s position in graph coords
		//    (Adjust these offsets for your node geometry)
		const nodeWidth = 160;
		const topOffset = 30;
		const spacing = 25;

		let gx, gy;
		if (socketType === 'input') {
			gx = node.position.x;
			gy = node.position.y + topOffset + index * spacing;
		} else {
			// 'output'
			gx = node.position.x + (nodeWidth);
			gy = node.position.y + topOffset + index * spacing;
		}

		return { cx: gx, cy: gy };
	}

	// Find the nearest socket to the mouse within a certain radius
	function findNearestSocket(mouseX, mouseY) {
		const snapRadius = 15; // pixel distance
		let closest = null;
		let minDist = Infinity;

		let graphPosition = screenToGraphCoords(mouseX, mouseY);

		for (const node of graphData.nodes) {
			let index = 0;
			for (const input of node.inputs) {
				// Convert that input’s graph coords -> screen coords
				const cx = node.position.x;
				const cy = node.position.y + 30 + index * 25;
				console.log( "cx: ", cx, "cy: ", cy );

				// Distance from mouse in pixel space
				const dx = graphPosition.x - cx;
				const dy = graphPosition.y - cy;
				const dist = Math.sqrt(dx*dx + dy*dy);
				console.log( "dist: ", dist );

				if (dist < snapRadius && dist < minDist) {
					minDist = dist;
					closest = {
						nodeId: node.id,
						socketName: input.name,
						cx,
						cy
					};
				}
				index++;
			}
		}

		return closest; // or null if none within snapRadius
	}

	// Intersection checking
	function checkCutIntersections() {
		if (!activeCutConnection) return;
		let currentPath = computeActiveCutConnectionPath(activeCutConnection, startGraphCoords, mouseGraphCoords);
		
		// compute length of the cut path from startGraphCoords and mouseGraphCoords
		// if the length is less than a certain threshold, then we don't want to cut
		// if the length is greater than a certain threshold, then we want to cut
		let cutPathLength = Math.sqrt( Math.pow( mouseGraphCoords.x - startGraphCoords.x, 2 ) + Math.pow( mouseGraphCoords.y - startGraphCoords.y, 2 ) );
		if ( cutPathLength < 20 ) return;
		const graphDataCopy = structuredClone(graphData);
		let cmd = {
			undo: () => {
				console.log("Undo cut: ", graphDataCopy.connections);
				// 1. Find the connection that was cut
				// 2. Add it back to the connections array
				graphData.connections = graphDataCopy.connections;
			},
			redo: () => {}
		}

		// 1. Find all connections that intersect with the current path
		// Filter out connections that intersect with the current path
		graphData.connections = graphData.connections.filter(conn => {
			return checkCollision(computePathData(conn), currentPath) === 0;
		});

		// only push command if something actually changed
		if ( graphData.connections.length !== graphDataCopy.connections.length )
			pushCommand(cmd);
	}

/* ---------------------------------------------------------------------------
* GRAPH DATA (Nodes, Connections)
* ------------------------------------------------------------------------- */
	let graphData = {
    "nodes": [
        {
            "id": "1",
            "name": "add_numbers",
            "inputs": [
                {
                    "name": "a",
                    "type": "number",
                    "default": 5
                },
                {
                    "name": "b",
                    "type": "number",
                    "default": 3
                }
            ],
            "outputs": [
                {
                    "name": "result",
                    "type": "number"
                }
            ],
            "position": {
                "x": 100,
                "y": 150
            }
        },
        {
            "id": "2",
            "name": "print_result",
            "inputs": [
                {
                    "name": "value",
                    "type": "number",
                    "default": null
                }
            ],
            "outputs": [],
            "position": {
                "x": 487.7523990599577,
                "y": 204.72011966538503
            }
        },
        {
            "name": "open_root_file",
            "inputs": [
                {
                    "name": "path",
                    "type": "str",
                    "default": "example.root",
                    "kind": "POSITIONAL_OR_KEYWORD"
                }
            ],
            "outputs": [
                {
                    "name": "file",
                    "type": "uproot.reading.ReadOnlyDirectory"
                },
                {
                    "name": "keys",
                    "type": "list[str]"
                },
                {
                    "name": "view",
                    "type": "str"
                }
            ],
            "docstring": "Facility for text visualization.",
            "source": "def open_root_file(path: str = \"example.root\") -> RootFileResult:\n    \"\"\"Facility for text visualization.\"\"\"\n    f = uproot.open(path)\n    view = json.dumps(f.classnames(), indent=4)\n    return {\n        'file': f,\n        'keys': f.keys(),\n        'view': view,\n    }",
            "id": "3",
            "position": {
                "x": 657.1297880062386,
                "y": 4.21793756957652
            }
        },
        {
            "name": "calculate_total",
            "inputs": [
                {
                    "name": "price",
                    "type": "float",
                    "default": null,
                    "kind": "POSITIONAL_OR_KEYWORD"
                },
                {
                    "name": "quantity",
                    "type": "int",
                    "default": "1",
                    "kind": "POSITIONAL_OR_KEYWORD"
                },
                {
                    "name": "tax_rate",
                    "type": "float",
                    "default": "0.1",
                    "kind": "POSITIONAL_OR_KEYWORD"
                }
            ],
            "outputs": [
                {
                    "name": "return_value",
                    "type": "float"
                }
            ],
            "docstring": "Calculate the total cost including tax.\n\nArgs:\n    price: Base price of the item\n    quantity: Number of items\n    tax_rate: Tax rate as a decimal",
            "source": "def calculate_total(price: float, quantity: int = 1, tax_rate: float = 0.1) -> float:\n    \"\"\"\n    Calculate the total cost including tax.\n    \n    Args:\n        price: Base price of the item\n        quantity: Number of items\n        tax_rate: Tax rate as a decimal\n    \"\"\"\n    subtotal = price * quantity\n    tax = subtotal * tax_rate\n    return subtotal + tax",
            "id": "4",
            "position": {
                "x": 607.3928812326479,
                "y": 448.7565066724061
            }
        }
    ],
    "connections": [
        {
            "from": {
                "node": "1",
                "output": "result"
            },
            "to": {
                "node": "2",
                "input": "value"
            }
        },
        {
            "from": {
                "node": "1",
                "output": "result"
            },
            "to": {
                "node": "3",
                "input": "path"
            }
        },
        {
            "from": {
                "node": "1",
                "output": "result"
            },
            "to": {
                "node": "4",
                "input": "quantity"
            }
        }
    ]
	};


	// Whenever graphData changes, assign it to window.graphData so the console sees the latest state.
	// ONLY for DEBUGGING, remove this line in production!
	$: window.graphData = graphData;
  
/* ---------------------------------------------------------------------------
* COMMAND PALETTE
* ------------------------------------------------------------------------- */
	let showCommandPalette = false;
	let commands = [
		{ name: 'Run Engine', callable: () => {runEngine(graphData);} },
		{ name: 'Save Graph', callable: saveGraphAsJSON },	
		{ name: 'Add Node', action: 'addNode', callable: addNode },
		{ name: 'Delete Selected Node', action: 'deleteNode', deleteSelectedNode },
		{ name: 'Load Graph', action: 'loadGraph', callable: loadGraphFromFile },
		{ name: 'Insert Node from JSON', callable: insertNodeFromFile },
		{ name: 'New Graph', callable: () => { graphData.nodes = []; graphData.connections = []; }},
		{ name: 'Undo', callable: undo },
		{ name: 'Redo', callable: redo },
	];

	async function runEngine( graphDataCopy ) {
        // 1) Load engine.py from your server (or embed it directly)
        // const enginePy = await (await fetch('/engine.py')).text();
        // This executes the code in engine.py so that its functions become available in Pyodide
        let pyodide = window.pyodide;
		// await pyodide.runPythonAsync(enginePy);

		
        // 2) Convert graphData to a JSON string for Python
        const graphJson = JSON.stringify(graphDataCopy);

		// 2a) Escape backslashes and double quotes in that JSON string
		const escapedGraphJson = graphJson
			.replace(/\\/g, '\\\\')  // escape all backslashes
			.replace(/"/g, '\\"');   // escape all double quotes

        // 3) Build a Python snippet that:
        //    - Imports json and engine
        //    - Parses graphJson
        //    - Calls the evaluate function
        //    - Returns the result as a JSON string
        const pythonCode = `
import json


# Convert the string into a Python dict
graph_dict = json.loads("""${escapedGraphJson}""")

# Evaluate using your DAG logic in engine.py
result = generate_python_script(graph_dict)

# Return the result as JSON so Pyodide can hand it back
json.dumps(result)
`;

        // 4) Run the Python code
		console.log('Running engine...');
		console.log('Python code:', pythonCode);
        const output = await pyodide.runPythonAsync(pythonCode);

        // output is whatever the last expression returns, so we have a JSON string
        console.log('Engine raw output:\n', output);

		// assuming that worked...
		
		// pyodide.setStdout({ batched: 
        //   (output) => {
        //       console.log("STDOUT GEN: ", output);
        //     //   outputLines = [...outputLines, output];
        //     }
        //   }
        //   );
		try {
			await pyodide.runPythonAsync( output );
			console.log("Run generated script complete");
		}  catch (err) {
			console.error("Error running generated script:", err);

		}
		console.log("Running Engine Complete");
		
		// console.log('Generated Script Output:', generated_script_output );

		// console.log("PRINTED: ", printed);
        // 5) Parse the returned JSON in JavaScript
        // const parsed = JSON.parse(output);
        // console.log('Parsed DAG evaluation result:', parsed);

        // Now `parsed` is a JS object with your DAG outputs.
    }

	function saveGraphAsJSON() {
		const data = {
			nodes: graphData.nodes,
			connections: graphData.connections
		};
	try {
        const jsonString = JSON.stringify(data, null, 2); // Pretty print with 2 spaces
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        // Create a temporary link element to trigger download
        const link = document.createElement('a');
        link.href = url;
        link.download = `data-${new Date().toISOString()}.json`; // Filename with timestamp
        document.body.appendChild(link);
        link.click();
        
        // Cleanup
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error saving JSON:', error);
        // You might want to add error handling UI here
      }
	}

	let selectedNodeId = null;
  
	function handleCommand(cmd) {
		if (cmd.callable && typeof cmd.callable === 'function') {
			cmd.callable();
		}
		showCommandPalette = false;
	}
  
	function addNode() {
	  const newId = (graphData.nodes.length + 1).toString();
	  const newNode = {
		id: newId,
		name: "new_function",
		inputs: [
		  { name: "param", type: "string", default: "default" }
		],
		outputs: [
		  { name: "result", type: "string" }
		],
		position: { x: 200, y: 200 }
	  };
	  console.log(newNode);
	  graphData.nodes = [...graphData.nodes, newNode];
	}
  
	function deleteSelectedNode() {
		console.debug( "DeleteSelectedNode: ", selectedNodeId );
	  if (!selectedNodeId) return;

	  const graphDataCopy = structuredClone(graphData);
	  let cmd = {
			undo: () => {

				console.log("Delete Node: ");
				// 1. Find the connection that was cut
				// 2. Add it back to the connections array
				graphData.nodes = graphDataCopy.nodes;
				graphData.connections = graphDataCopy.connections;
			},
			redo: () => {}
		}
		pushCommand(cmd);

	  graphData.nodes = graphData.nodes.filter(n => n.id !== selectedNodeId);
	  graphData.connections = graphData.connections.filter(conn =>
		conn.from.node !== selectedNodeId && conn.to.node !== selectedNodeId
	  );
	  selectedNodeId = null;
	}


/* ---------------------------------------------------------------------------
* INSERT NODE FROM JSON (new feature)
* ------------------------------------------------------------------------- */
	let nodeFileInputRef; // hidden file input for inserting node(s)

	function insertNodeFromFile() {
		nodeFileInputRef.click();
	}

	function handleNodeFileChange(e) {
		const file = e.target.files[0];
		if (!file) return;

		const reader = new FileReader();
		reader.onload = (event) => {
			try {
				// Expecting either a single node object or an array of nodes
				const data = JSON.parse(event.target.result);
				
				// If the file has a single node object
				if (!Array.isArray(data)) {
					// Insert one node
					addNodeToGraph(data);
				} else {
					// Insert multiple nodes
					for (const nodeDef of data) {
						addNodeToGraph(nodeDef);
					}
				}
			} catch (err) {
				console.error("Invalid node JSON:", err);
			}
		};
		reader.readAsText(file);

		e.target.value = "";
	}

	// Helper: add a node definition to the graph, auto-assign ID if missing
	function addNodeToGraph(nodeDef) {
		console.log(nodeDef);
		// If the nodeDef doesn't have an id, generate one
		if (!nodeDef.id) {
			nodeDef.id = (graphData.nodes.length + 1).toString();
		}
		// If there's no position, default it somewhere
		if (!nodeDef.position) {
			nodeDef.position = { x: 100, y: 100 };
		}
		// Merge it into the array
		graphData.nodes = [...graphData.nodes, nodeDef];
	}


	// -- FILE LOADING LOGIC --
	let fileInputRef; // reference to the hidden <input type="file" />

	function loadGraphFromFile() {
		// Programmatically click the hidden file input
		fileInputRef.click();
	}

	function handleFileChange(e) {
	const file = e.target.files[0];
	if (!file) return;

	const reader = new FileReader();
	reader.onload = (event) => {
		try {
		const data = JSON.parse(event.target.result);
		// Replace current graphData with the loaded data
		graphData = data;
		} catch (err) {
		console.error("Invalid JSON file:", err);
		}
	};
	reader.readAsText(file);

	// Reset the value so the user can load the same file again if needed
	e.target.value = "";
	}
  
/* ---------------------------------------------------------------------------
* VIEWBOX-BASED CAMERA: Panning & Zooming
* -------------------------------------------------------------------------
* We treat the SVG coordinate system as 0..baseWidth by 0..baseHeight.
* The 'camera' is defined by (cameraX, cameraY, scale), meaning:
*   - top-left corner of the visible area is (cameraX, cameraY)
*   - width of visible area is (baseWidth / scale), likewise for height
* Adjusting cameraX/cameraY pans; adjusting scale zooms.
* The final viewBox is updated accordingly.
* ------------------------------------------------------------------------- */
	// instead of using a fixed value I did this - but it is not reactive...
	// let canvasWidth = 0;
	// let canvasHeight = 0;
	let baseWidth = window.innerWidth;  // The nominal coordinate space width
	let baseHeight = window.innerHeight; // The nominal coordinate space height
  
	let cameraX = 0;   // top-left in graph coords
	let cameraY = 0;
	let scale = 1.0;
  
	// We'll measure the actual rendered SVG size so we can convert
	// screen (mouse) coords to graph coords. This is optional, but recommended.
	let svgRef;
	let svgWidth = 0;
	let svgHeight = 0;

	// these wont update on their own, so respond to the change in baseWidth and baseHeight
	$: if ( svgRef && baseWidth !== undefined ) svgWidth = svgRef.clientWidth;
	$: if ( svgRef && baseHeight !== undefined ) svgHeight = svgRef.clientHeight;
	  
	const ZOOM_FACTOR = 0.1; // 10% zoom per wheel event

	async function setup(){
        let pyodide = await loadPyodide();
        console.log(pyodide.runPython("1 + 2"));
      }
	onMount(() => {
	  window.addEventListener('keydown', handleKeyDown);
	//   setup();

	  return () => window.removeEventListener('keydown', handleKeyDown);
	});
  
	// Convert from screenX/screenY => graph coords
	// For top-left anchored zoom, we do:
	function screenToGraphCoords(sx, sy) {
	  // fraction across the svg in each dimension
	  let fx = sx / svgWidth;
	  let fy = sy / svgHeight;
  
	  // width & height in graph coords that currently fill the entire svg
	  let w = baseWidth / scale;
	  let h = baseHeight / scale;
  
	  // cameraX, cameraY define the top-left corner in graph coords
	  let gx = cameraX + fx * w;
	  let gy = cameraY + fy * h;
	  return { x: gx, y: gy };
	}
  
	// Update camera after user drags the middle mouse
	function handleMouseDown(e) {
		console.log( "tagname: ", e.target.tagName );
		if (e.target.tagName === 'INPUT' || 
			e.target.closest('foreignObject') || 
			e.target.tagName === 'foreignObject') {
			
				console.log("skipping mouse down event");
				return;
		}
		// save starting mouse position and camera position
		if (e.button === 0 && e.target.tagName === 'svg') {
			selectedNodeId = null;
			mouseGraphCoords = startGraphCoords = screenToGraphCoords(e.clientX, e.clientY);
			activeCutConnection = true;
		}
	}
  
	function handleMouseMove(e) {
		// console.debug( "MouseMove" );
		const { x, y } = screenToGraphCoords(e.clientX, e.clientY);
		mouseX = x;
		mouseY = y;
		mouseGraphCoords = { x, y };
		// console.log( "CutPAth: ", computeActiveCutConnectionPath() );

	}
  
	function handleMouseUp(e) {
		console.debug( "MouseUp" );
		// handle link disconnect
		checkCutIntersections();
		activeCutConnection = null;
		
	}
  
	function handleCameraZoom( direction ){
		// 1. Get the current center of the view in graph coordinates
		const viewWidth = baseWidth / scale;
		const viewHeight = baseHeight / scale;
		const centerX = cameraX + viewWidth / 2;
		const centerY = cameraY + viewHeight / 2;

		// 2. Determine zoom direction and update scale
		scale += direction * ZOOM_FACTOR * scale;
		scale = Math.max(0.1, Math.min(scale, 10));

		// 3. Adjust cameraX and cameraY to keep the center fixed
		const newViewWidth = baseWidth / scale;
		const newViewHeight = baseHeight / scale;
		cameraX = centerX - newViewWidth / 2;
		cameraY = centerY - newViewHeight / 2;
	}

	function handleCameraPan( dx, dy ){
		cameraX += dx / scale;
		cameraY += dy / scale;
	}

	// Zoom in/out with mouse wheel
	function handleWheel(e) {
		if (e.ctrlKey != 1){
			// two finger pan
			e.preventDefault();
			const panFactor = 1.1; // just to make my mouse pan a little faster
			handleCameraPan( e.deltaX * panFactor, e.deltaY * panFactor );
	  	} else {
			// handles ctrl + zoom wheel AND pinch to zoom (magic?)
			e.preventDefault();
			handleCameraZoom( 0.5 * (e.deltaY < 0 ? 1 : -1) );
	  	}
	}
  
	// WASD panning + +/- zoom
	function handleKeyDown(e) {
	  // For panning, we move camera in graph coords
	  // e.g. pressing W => cameraY -= some offset
	  	if (!showCommandPalette) {
			if (e.key === 'w' || e.key === 'W') {
				handleCameraPan( 0, -50 );
			} else if (e.key === 's' || e.key === 'S') {
				handleCameraPan( 0, 50 );
			} else if (e.key === 'a' || e.key === 'A') {
				handleCameraPan( -50, 0 );
			} else if (e.key === 'd' || e.key === 'D') {
				handleCameraPan( 50, 0 );
			} else if (e.key === '=') {
				handleCameraZoom(1);
			} else if (e.key === '-') {
				handleCameraZoom(-1);
			} else if (e.key === 'h' || e.key === 'H') {
				// highlightPointer = !highlightPointer;
				
				cameraX = 0;
				cameraY = 0;
				scale = 0.5;
			} else if (e.key === 'Delete' || e.key === 'Backspace') {
				console.log("Delete key pressed");
				deleteSelectedNode();
			} else if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
				undo();
			} else if ((e.metaKey || e.ctrlKey) && e.key === 'y') {
				redo();
			} else if ( e.key === 'Escape' ) {
				selectedNodeId = null;
			}

		}
  
	  // Toggle command palette
	  if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.code === 'KeyP') {
		showCommandPalette = !showCommandPalette;
	  }
	  // Add this condition to close the command palette when Esc is pressed
	  if (e.key === 'Escape' && showCommandPalette) {
		showCommandPalette = false;
	  } 
	}
  
	// The final derived viewBox, updated whenever cameraX, cameraY, or scale changes
	$: viewBoxString = `${cameraX} ${cameraY} ${baseWidth / scale} ${baseHeight / scale}`;
  
	/* ---------------------------------------------------------------------------
	 * CONNECTIONS
	 * ------------------------------------------------------------------------- */
	function getNodeById(id) {
	  return graphData.nodes.find(n => n.id === id);
	}
  
	// For each connection, compute an SVG path from the source socket to the target socket
	function computePathData(conn) {
	  const sourceNode = getNodeById(conn.from.node);
	  const targetNode = getNodeById(conn.to.node);
	  if (!sourceNode || !targetNode) return "";
	  const sourceIndex = sourceNode.outputs.findIndex(o => o.name === conn.from.output);
	  const targetIndex = targetNode.inputs.findIndex(i => i.name === conn.to.input);
  
	  // Convert node coords to the same coordinate system as the viewBox (graph coords)
	  const sourcePos = getSocketPosition(sourceNode, 'output', sourceIndex);
	  const targetPos = getSocketPosition(targetNode, 'input', targetIndex);
  
	  // We'll just do a simple cubic curve
	  const delta = Math.abs(targetPos.x - sourcePos.x) / 2;
	  return `M ${sourcePos.x} ${sourcePos.y}
			  C ${sourcePos.x + delta} ${sourcePos.y}
				${targetPos.x - delta} ${targetPos.y}
				${targetPos.x} ${targetPos.y}`;
	}
  
	// Return the (x,y) in graph coords for a socket
	// Because we're directly using viewBox, these are just node.position plus offsets
	function getSocketPosition(node, type, index) {
	  const nodeWidth = 160;
	  const topOffset = 30;
	  const spacing = 25;
  
	  let x = (type === 'input')
		? node.position.x + 5
		: node.position.x + (nodeWidth - 5);
  
	  let y = node.position.y + topOffset + index * spacing;
  
	  return { x, y };
	}
  
	function selectNode(id) {
	  selectedNodeId = id;
	}
  
	// Called by Node.svelte when a node is dragged
	function updateNodePosition(id, x, y) {
	  graphData.nodes = graphData.nodes.map(n =>
		n.id === id ? { ...n, position: { x, y } } : n
	  );
	}
</script>
  
<style>
	:global(body) { /* this will apply to <body> */ margin: 0; padding: 0; }
	.canvas {
	  width: 100%;
	  height: 100vh;
	  background-color: #f5f5f5;
	  position: relative;
	  overflow: hidden;
	}
	.command-palette-overlay {
	  position: absolute;
	  inset: 0;
	  background: rgba(0,0,0,0.5);
	  display: flex;
	  justify-content: center;
	  align-items: center;
	  z-index: 10;
	}
</style>

<svelte:window
	bind:innerWidth={baseWidth}
	bind:innerHeight={baseHeight}
	/>
  <!-- 
	The .canvas fills the browser window. 
	We attach on:mousedown and on:wheel for panning & zooming. 
  -->
<div
	class="canvas"
	on:mousedown|preventDefault={handleMouseDown}
	on:mouseup={handleMouseUp}
	on:wheel|preventDefault={handleWheel}
  >
  <!-- <script>
	async function doLoadPyodide() {
		const pyodide = await window.loadPyodide();
		window.pyodide = pyodide;
	  return pyodide;
	}
	doLoadPyodide();
  </script> -->
  	<!-- Hidden file input for loading JSON -->
	<input
	type="file"
	accept="application/json"
	bind:this={fileInputRef}
	on:change={handleFileChange}
	style="display: none;"
	/>

	 <!-- Hidden file input for inserting node from JSON -->
	 <input
	 type="file"
	 accept="application/json"
	 bind:this={nodeFileInputRef}
	 on:change={handleNodeFileChange}
	 style="display: none;"
   />

	<!-- 
	  The SVG itself uses a reactive viewBox string. 
	  We bind a ref to measure its size. 
	-->
	<svg
	  bind:this={svgRef}
	  width="100%"
	  height="100%"	
	  viewBox={viewBoxString}
	  preserveAspectRatio="none"
	  on:mousemove={handleMouseMove}
	>
		{#if highlightPointer}
			<circle
				cx={mouseX}
				cy={mouseY}
				r={5}
				fill="#F00"
			></circle>
		{/if}
	  <!-- Render connections -->
	  {#each graphData.connections as conn}
		<!-- TODO: add a circle in the center of each path to quickly add a node there -->
		<Link path={computePathData(conn)} />
	  {/each}

	  <!-- Render nodes -->
	  {#each graphData.nodes as node (node.id)}
		<Node
		  {node}
		  {selectedNodeId}
		  on:socketPointerDown={handleSocketPointerDown}
		  on:drag={(e) => updateNodePosition(node.id, e.detail.x, e.detail.y)}
		  on:select={() => selectNode(node.id)}
		  {screenToGraphCoords}
		/>
	  {/each}

		<!-- Ghost path for the in-progress connection -->
		{#if activeConnection}
			<path d={ghostPath} stroke="red" stroke-width="2" fill="none" />
		{/if}

		<!-- Ghost path for the in-progress cut connection -->
		<!-- {#if activeCutConnection} -->
		<path d={ghostCutPath} stroke="red" stroke-width="2" fill="none" />
		<!-- {/if} -->
	</svg>
  
	{#if showCommandPalette}
	  <div class="command-palette-overlay">
		<CommandPalette {commands} on:selectCommand={(e) => handleCommand(e.detail)} />
	  </div>
	{/if}
	<!-- <PyodideTerm /> -->
</div>
<PyodideRepl {pyodide} />