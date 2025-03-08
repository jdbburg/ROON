<script>
  import { createEventDispatcher } from 'svelte';
  import Socket from './Socket.svelte';

  export let node;
  export let screenToGraphCoords; // function from parent
  export let selectedNodeId;
  const dispatch = createEventDispatcher();

  let dragging = false;
  let startGraphX, startGraphY; // the initial pointer position in graph coords
  let origNodeX, origNodeY;     // the node's original position
  let showWidgets = true;
  
  // outline the node if selected
  $: selected = ( selectedNodeId == node.id )
  $: outline_color =  !selected ? "#000" : "#F00";
  $: outline_stroke_width = !selected ? 1 : 2;

  // Show widgets
  // export let show_widgets = false;

  function handlePointerDown(e) {
    // Left-click only for node dragging
    if (e.button !== 0) return;
    e.stopPropagation();
    dragging = true;

    node.selected = !node.selected;

    // Convert the screen coords to graph coords
    const { x, y } = screenToGraphCoords(e.clientX, e.clientY);
    startGraphX = x;
    startGraphY = y;
    origNodeX = node.position.x;
    origNodeY = node.position.y;

    console.log("outline_color: ", outline_color)

    dispatch('select');
    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);
  }

  function handlePointerMove(e) {
    if (!dragging) return;
    const { x, y } = screenToGraphCoords(e.clientX, e.clientY);
    const dx = x - startGraphX;
    const dy = y - startGraphY;
    // Update node position in graph coords
    const newX = origNodeX + dx;
    const newY = origNodeY + dy;
    dispatch('drag', { x: newX, y: newY });
  }

  function handlePointerUp(e) {
    if (e.button !== 0) return;
    dragging = false;
    window.removeEventListener('pointermove', handlePointerMove);
    window.removeEventListener('pointerup', handlePointerUp);
  }

  // Dynamically compute the node's height for neat layout
  function calcNodeHeight() {
    const baseHeight = 40; // space for title
    const maxIO = Math.max(node.inputs.length, node.outputs.length);
    return baseHeight + maxIO * 25;
  }

  // Called when the user pointer-downs on an output socket
  function handleSocketPointerDown(type, socketName, index, event) {
    if ( type === 'input' ) return; // for now, until we handle correctly
    event.stopPropagation();  // don’t trigger node-drag
    dispatch('socketPointerDown', {
      socketType: type,           // 'output' (or 'input' if you add that)
      socketName,     // e.g. "result"
      index,
      nodeId: node.id,
      clientX: event.clientX,
      clientY: event.clientY
    });
  }

</script>


  <!-- We do NOT apply camera transform here. It's applied in App.svelte. 
       This <g> is placed in 'graph' coordinates, then the parent container 
       is scaled/panned. -->
  <g
    transform="translate({node.position.x}, {node.position.y})"
    style="cursor: move;"
    on:pointerdown={handlePointerDown}
  >
    <foreignObject>
      <select>

      </select>
    </foreignObject>
    <rect
      x="0" y="0"
      rx="5" ry="5"
      width="160"
      height="{calcNodeHeight()}"
      fill="#fff"
      stroke={outline_color}
      stroke-width={outline_stroke_width}
    />
    <text x="10" y="15" font-size="12" fill="#333">[{node.id}]: {node.name}</text>

    <!-- Inputs -->
    {#each node.inputs as input, i}
    <Socket
        nodeId={node.id}
        socket={input}
        socketFlow="input"
        index={i}
        showWidgets={showWidgets}
        on:socketPointerDown
      />
    {/each}

    <!-- Outputs -->
    {#each node.outputs as output, j}
      <Socket
        nodeId={node.id}
        socket={output}
        socketFlow="output"
        index={j}
        showWidgets={showWidgets}
        on:socketPointerDown
      />
    {/each}
</g>

<style>
</style>