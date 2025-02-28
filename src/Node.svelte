<script>
  import { createEventDispatcher } from 'svelte';

  export let node;
  export let screenToGraphCoords; // function from parent
  export let scale;
  export let panX;
  export let panY;

  const dispatch = createEventDispatcher();

  let dragging = false;
  let startGraphX, startGraphY; // the initial pointer position in graph coords
  let origNodeX, origNodeY;     // the node's original position

  function handlePointerDown(e) {
    // Left-click only for node dragging
    if (e.button !== 0) return;
    e.stopPropagation();
    dragging = true;

    // Convert the screen coords to graph coords
    const { x, y } = screenToGraphCoords(e.clientX, e.clientY);
    startGraphX = x;
    startGraphY = y;
    origNodeX = node.position.x;
    origNodeY = node.position.y;

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
</script>

<svg>
  <!-- We do NOT apply camera transform here. It's applied in App.svelte. 
       This <g> is placed in 'graph' coordinates, then the parent container 
       is scaled/panned in screen space. -->
  <g
    transform="translate({node.position.x}, {node.position.y})"
    style="cursor: move;"
    on:pointerdown={handlePointerDown}
  >
    <rect
      x="0" y="0"
      rx="5" ry="5"
      width="160"
      height="{calcNodeHeight()}"
      fill="#fff"
      stroke="#333"
      stroke-width="1"
    />
    <text x="10" y="15" font-size="12" fill="#333">{node.name}</text>

    <!-- Inputs -->
    {#each node.inputs as input, i}
      <circle
        cx="5"
        cy={30 + i * 25}
        r="5"
        fill="#0a0"
      />
      <foreignObject
        x="15"
        y={20 + i * 25}
        width="130"
        height="24"
        style="overflow: visible;"
      >
        {#if input.type === 'number'}
          <input
            type="number"
            value={input.default}
            style="width:100%; height:20px; font-size:12px; box-sizing:border-box;"
            on:change={(e) => input.default = parseFloat(e.target.value)}
          />
        {:else if input.type === 'string'}
          <input
            type="text"
            value={input.default}
            style="width:100%; height:20px; font-size:12px; box-sizing:border-box;"
            on:change={(e) => input.default = e.target.value}
          />
        {:else}
          <input
            type="text"
            value={input.default}
            style="width:100%; height:20px; font-size:12px; box-sizing:border-box;"
            on:change={(e) => input.default = e.target.value}
          />
        {/if}
      </foreignObject>
    {/each}

    <!-- Outputs -->
    {#each node.outputs as output, j}
      <circle
        cx="155"
        cy={30 + j * 25}
        r="5"
        fill="#00a"
      />
    {/each}
  </g>
</svg>