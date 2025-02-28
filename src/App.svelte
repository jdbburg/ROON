<script>
	import { onMount } from 'svelte';
	import Node from './Node.svelte';
	import CommandPalette from './CommandPalette.svelte';
  
	// Sample graph data representing Python functions.
	let graphData = {
	  nodes: [
		{
		  id: "1",
		  name: "add_numbers",
		  inputs: [
			{ name: "a", type: "number", default: 5 },
			{ name: "b", type: "number", default: 3 }
		  ],
		  outputs: [
			{ name: "result", type: "number" }
		  ],
		  position: { x: 100, y: 150 }
		},
		{
		  id: "2",
		  name: "print_result",
		  inputs: [
			{ name: "value", type: "number", default: null }
		  ],
		  outputs: [],
		  position: { x: 400, y: 150 }
		}
	  ],
	  connections: [
		{
		  from: { node: "1", output: "result" },
		  to: { node: "2", input: "value" }
		}
	  ]
	};
  
	// State for command palette visibility.
	let showCommandPalette = false;
  
	// List of available commands.
	let commands = [
	  { name: 'Add Node', action: 'addNode' },
	  { name: 'Delete Selected Node', action: 'deleteNode' }
	];
  
	// Currently selected node id.
	let selectedNodeId = null;
  
	// Update node position after dragging.
	function updateNodePosition(id, x, y) {
	  graphData.nodes = graphData.nodes.map(n =>
		n.id === id ? { ...n, position: { x, y } } : n
	  );
	}
  
	// Helper to get a node by its id.
	function getNodeById(id) {
	  return graphData.nodes.find(n => n.id === id);
	}
  
	// Helper function to compute SVG path data for a connection.
	function computePathData(conn) {
	  const sourceNode = getNodeById(conn.from.node);
	  const targetNode = getNodeById(conn.to.node);
	  if (!sourceNode || !targetNode) return "";
	  const sourceIndex = sourceNode.outputs.findIndex(o => o.name === conn.from.output);
	  const targetIndex = targetNode.inputs.findIndex(i => i.name === conn.to.input);
	  const sourcePos = getSocketPosition(sourceNode, 'output', sourceIndex);
	  const targetPos = getSocketPosition(targetNode, 'input', targetIndex);
	  const delta = Math.abs(targetPos.cx - sourcePos.cx) / 2;
	  return `M ${sourcePos.cx} ${sourcePos.cy} C ${sourcePos.cx + delta} ${sourcePos.cy} ${targetPos.cx - delta} ${targetPos.cy} ${targetPos.cx} ${targetPos.cy}`;
	}
  
	// Calculate socket positions based on node data.
	function getSocketPosition(node, type, index) {
		const x = node.position.x;
		const y = node.position.y;
		const nodeWidth = 160;  // match the <rect> width
		const topOffset = 30;   // match the circle’s vertical offset
		const spacing = 25;

		if (type === 'input') {
			return {
			cx: x + 5,                  // left circle offset
			cy: y + topOffset + index * spacing
			};
		} else {
			return {
			cx: x + (nodeWidth - 5),    // right circle offset
			cy: y + topOffset + index * spacing
			};
		}
	}
  
	// Handle commands selected from the command palette.
	function handleCommand(command) {
	  if (command.action === 'addNode') {
		addNode();
	  } else if (command.action === 'deleteNode') {
		deleteSelectedNode();
	  }
	  showCommandPalette = false;
	}
  
	// Add a new dummy node.
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
	  graphData.nodes = [...graphData.nodes, newNode];
	}
  
	// Delete the currently selected node.
	function deleteSelectedNode() {
	  if (!selectedNodeId) return;
	  graphData.nodes = graphData.nodes.filter(n => n.id !== selectedNodeId);
	  // Also remove connections that involve the node.
	  graphData.connections = graphData.connections.filter(
		c => c.from.node !== selectedNodeId && c.to.node !== selectedNodeId
	  );
	  selectedNodeId = null;
	}
  
	// Global keydown handler for toggling the command palette.
	function handleKeyDown(e) {
	  if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.code === 'KeyP') {
		showCommandPalette = !showCommandPalette;
	  }
	}
  
	onMount(() => {
	  window.addEventListener('keydown', handleKeyDown);
	  return () => window.removeEventListener('keydown', handleKeyDown);
	});
  
	// Called when a node is clicked.
	function selectNode(id) {
	  selectedNodeId = id;
	}
  </script>
  
  <style>
	.canvas {
	  width: 100%;
	  height: 100vh;
	  background-color: #f5f5f5;
	  position: relative;
	}
	.command-palette-overlay {
	  position: absolute;
	  top: 0;
	  left: 0;
	  right:0;
	  bottom: 0;
	  background: rgba(0,0,0,0.5);
	  display: flex;
	  justify-content: center;
	  align-items: center;
	  z-index: 10;
	}
	
  </style>
  
  <div class="canvas">
	<svg width="100%" height="100%">
	  <!-- Render connections -->
	  {#each graphData.connections as conn (conn.from.node + '-' + conn.to.node)}
		{#if getNodeById(conn.from.node) && getNodeById(conn.to.node)}
		  <path d={computePathData(conn)} stroke="#555" stroke-width="2" fill="none" />
		{/if}
	  {/each}
  
	  <!-- Render nodes -->
	  {#each graphData.nodes as node (node.id)}
		<Node {node} on:drag={e => updateNodePosition(node.id, e.detail.x, e.detail.y)}
			  on:select={() => selectNode(node.id)} />
	  {/each}
	</svg>
  
	{#if showCommandPalette}
	  <div class="command-palette-overlay">
		<CommandPalette {commands} on:selectCommand={e => handleCommand(e.detail)} />
	  </div>
	{/if}
  </div>