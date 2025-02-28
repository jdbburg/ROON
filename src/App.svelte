<script>
	import { onMount } from 'svelte';
	import Node from './Node.svelte';
	import CommandPalette from './CommandPalette.svelte';
  
	/* ---------------------------------------------------------------------------
	 * GRAPH DATA (Nodes, Connections)
	 * ------------------------------------------------------------------------- */
	let graphData = {
	  nodes: [
		{
		  id: "1",
		  name: "add_numbers",
		  inputs: [
		  { name: "a", type: "number", default: 5 },
		  { name: "b", type: "number", default: 3 }
		  ],
		  outputs: [{ name: "result", type: "number" }],
		  position: { x: 100, y: 150 } // in 'graph' coordinates
		},
		{
		  id: "2",
		  name: "print_result",
		  inputs: [{ name: "value", type: "number", default: null }],
		  outputs: [],
		  position: { x: 400, y: 150 }
		}
	  ],
	  connections: [
		{
		  from: { node: "1", output: "result" },
		  to:   { node: "2", input: "value" }
		}
	  ]
	};
  
	/* ---------------------------------------------------------------------------
	 * COMMAND PALETTE
	 * ------------------------------------------------------------------------- */
	let showCommandPalette = false;
	let commands = [
	  { name: 'Add Node', action: 'addNode' },
	  { name: 'Delete Selected Node', action: 'deleteNode' }
	];
	let selectedNodeId = null;
  
	function handleCommand(cmd) {
	  if (cmd.action === 'addNode') addNode();
	  else if (cmd.action === 'deleteNode') deleteSelectedNode();
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
	  graphData.nodes = [...graphData.nodes, newNode];
	}
  
	function deleteSelectedNode() {
	  if (!selectedNodeId) return;
	  graphData.nodes = graphData.nodes.filter(n => n.id !== selectedNodeId);
	  graphData.connections = graphData.connections.filter(conn =>
		conn.from.node !== selectedNodeId && conn.to.node !== selectedNodeId
	  );
	  selectedNodeId = null;
	}
  
	/* ---------------------------------------------------------------------------
	 * CAMERA STATE: Panning & Zooming
	 * ------------------------------------------------------------------------- */
	let panX = 0;
	let panY = 0;
	let scale = 1.0;
  
	// For middle-mouse dragging
	let isPanning = false;
	let startPanX, startPanY;
	let startMouseX, startMouseY;
  
	// For controlling zoom speed, panning speed
	const ZOOM_FACTOR = 0.1;
	const PAN_SPEED = 20; // WASD panning speed
  
	// Convert screen coordinates -> graph coordinates
	function screenToGraphCoords(screenX, screenY) {
	  return {
		x: (screenX - panX) / scale,
		y: (screenY - panY) / scale
	  };
	}
  
	// Middle mouse down => start panning
	function handleMouseDown(e) {
	  // Only handle middle mouse button (button === 1)
	  if (e.button === 1) {
		e.preventDefault();
		isPanning = true;
		startMouseX = e.clientX;
		startMouseY = e.clientY;
		startPanX = panX;
		startPanY = panY;
		window.addEventListener('mousemove', handleMouseMove);
		window.addEventListener('mouseup', handleMouseUp);
	  }
	}
  
	function handleMouseMove(e) {
	  if (!isPanning) return;
	  const dx = e.clientX - startMouseX;
	  const dy = e.clientY - startMouseY;
	  panX = startPanX + dx;
	  panY = startPanY + dy;
	}
  
	function handleMouseUp(e) {
	  if (e.button === 1) {
		isPanning = false;
		window.removeEventListener('mousemove', handleMouseMove);
		window.removeEventListener('mouseup', handleMouseUp);
	  }
	}
  
	// Mouse wheel => zoom in/out
	function handleWheel(e) {
	  e.preventDefault();
	  const delta = e.deltaY < 0 ? 1 : -1; // up => zoom in, down => zoom out
	  scale += delta * ZOOM_FACTOR * scale; // scale up or down proportionally
	  scale = Math.max(0.1, Math.min(scale, 10)); // clamp
	}
  
	// Keyboard panning (WASD) & zooming (+/-)
	function handleKeyDown(e) {
	  if (e.key === 'w' || e.key === 'W') {
		panY += PAN_SPEED;
	  } else if (e.key === 's' || e.key === 'S') {
		panY -= PAN_SPEED;
	  } else if (e.key === 'a' || e.key === 'A') {
		panX += PAN_SPEED;
	  } else if (e.key === 'd' || e.key === 'D') {
		panX -= PAN_SPEED;
	  } else if (e.key === '+') {
		scale = Math.min(scale + ZOOM_FACTOR * scale, 10);
	  } else if (e.key === '-') {
		scale = Math.max(scale - ZOOM_FACTOR * scale, 0.1);
	  }
  
	  // Command palette toggle: Cmd+Shift+P or Ctrl+Shift+P
	  if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.code === 'KeyP') {
		showCommandPalette = !showCommandPalette;
	  }
	}
  
	onMount(() => {
	  window.addEventListener('keydown', handleKeyDown);
	  return () => window.removeEventListener('keydown', handleKeyDown);
	});
  
	/* ---------------------------------------------------------------------------
	 * CONNECTIONS
	 * ------------------------------------------------------------------------- */
	function getNodeById(id) {
	  return graphData.nodes.find(n => n.id === id);
	}
  
	function computePathData(conn) {
	  const sourceNode = getNodeById(conn.from.node);
	  const targetNode = getNodeById(conn.to.node);
	  if (!sourceNode || !targetNode) return "";
	  const sourceIndex = sourceNode.outputs.findIndex(o => o.name === conn.from.output);
	  const targetIndex = targetNode.inputs.findIndex(i => i.name === conn.to.input);
  
	  const sourcePos = getSocketPosition(sourceNode, 'output', sourceIndex);
	  const targetPos = getSocketPosition(targetNode, 'input', targetIndex);
  
	  const delta = Math.abs(targetPos.cx - sourcePos.cx) / 2;
	  return `M ${sourcePos.cx} ${sourcePos.cy}
			  C ${sourcePos.cx + delta} ${sourcePos.cy}
				${targetPos.cx - delta} ${targetPos.cy}
				${targetPos.cx} ${targetPos.cy}`;
	}
  
	// Get socket coordinates in screen space
	function getSocketPosition(node, type, index) {
	  // node.position is in 'graph' coords
	  // We'll transform to screen coords by applying the camera transform
	  const nodeWidth = 160;
	  const topOffset = 30;
	  const spacing = 25;
  
	  let localX = 0, localY = 0;
	  if (type === 'input') {
		localX = node.position.x + 5;
		localY = node.position.y + topOffset + index * spacing;
	  } else {
		localX = node.position.x + (nodeWidth - 5);
		localY = node.position.y + topOffset + index * spacing;
	  }
  
	  // Convert graph coords to screen coords:
	  return {
		cx: localX * scale + panX,
		cy: localY * scale + panY
	  };
	}
  
	// Called when a node is clicked => select it
	function selectNode(id) {
	  selectedNodeId = id;
	}
  
	// Update node position after dragging (the node receives 'graph' coords)
	function updateNodePosition(id, x, y) {
	  graphData.nodes = graphData.nodes.map(n =>
		n.id === id ? { ...n, position: { x, y } } : n
	  );
	}
  </script>
  
  <style>
	.canvas {
	  width: 100%;
	  height: 100vh;
	  background-color: #f5f5f5;
	  position: relative;
	  overflow: hidden;
	}
	/* Graph container is where we apply transform for pan & zoom (CSS approach) */
	.graph-container {
	  width: 100%;
	  height: 100%;
	  transform-origin: center center; /* zoom around middle of container */
	  /* We'll apply translate/scale inline with style binding. */
	  position: relative;
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
  
  <div
	class="canvas"
	on:mousedown|preventDefault={handleMouseDown}
	on:wheel|preventDefault={handleWheel}
  >
	<!--
	  We'll do a nested DIV for the 'graph-container' that is translated/scaled by panX, panY, scale.
	  Inside it, we place an <svg> for connections & nodes. Another approach is using an <svg> alone
	  and setting <g transform>, but CSS transforms are simpler for center-based zoom in many browsers.
	-->
	<div
	  class="graph-container"
	  style="transform: translate({panX}px, {panY}px) scale({scale});"
	>
	  <svg width="100%" height="100%">
		<!-- Render connections -->
		{#each graphData.connections as conn (conn.from.node + '-' + conn.to.node)}
		  <path d={computePathData(conn)} stroke="#555" stroke-width="2" fill="none" />
		{/each}
  
		<!-- Render nodes -->
		{#each graphData.nodes as node (node.id)}
		  <Node
			{node}
			on:drag={(e) => updateNodePosition(node.id, e.detail.x, e.detail.y)}
			on:select={() => selectNode(node.id)}
			{screenToGraphCoords}
			{scale}
			{panX}
			{panY}
		  />
		{/each}
	  </svg>
	</div>
  
	{#if showCommandPalette}
	  <div class="command-palette-overlay">
		<CommandPalette {commands} on:selectCommand={(e) => handleCommand(e.detail)} />
	  </div>
	{/if}
  </div>