<script>
  import { createEventDispatcher } from 'svelte';
  export let node;
  const dispatch = createEventDispatcher();

  let dragging = false;
  let startX, startY;
  let origX, origY;

  // Calculate a node height based on how many inputs/outputs you have
  // so everything fits nicely.
  function calcNodeHeight() {
    const baseHeight = 40;        // space for the title bar
    const perInput = 25;         // space per input row
    const maxIO = Math.max(node.inputs.length, node.outputs.length);
    return baseHeight + maxIO * perInput;
  }

  function handlePointerDown(e) {
    dragging = true;
    startX = e.clientX;
    startY = e.clientY;
    origX = node.position.x;
    origY = node.position.y;
    dispatch('select');
    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);
  }

  function handlePointerMove(e) {
    if (!dragging) return;
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    const newX = origX + dx;
    const newY = origY + dy;
    dispatch('drag', { x: newX, y: newY });
  }

  function handlePointerUp() {
    dragging = false;
    window.removeEventListener('pointermove', handlePointerMove);
    window.removeEventListener('pointerup', handlePointerUp);
  }
</script>

<svg>
  <!-- Position the entire group based on node.position -->
  <g
    transform="translate({node.position.x}, {node.position.y})"
    style="cursor: move;"
    on:pointerdown={handlePointerDown}
  >
    <!-- Draw a rectangle big enough for the title and all inputs -->
    <rect
      x="0" y="0"
      rx="5" ry="5"
      width="160"
      height="{calcNodeHeight()}"
      fill="#fff"
      stroke="#333"
      stroke-width="1"
    />

    <!-- Function name (title) -->
    <text x="10" y="15" font-size="12" fill="#333">{node.name}</text>

    <!-- Render input sockets & default value fields -->
    {#each node.inputs as input, i}
      <!-- Circle offset from left edge by 5px; 30px from top bar + i * 25px row spacing -->
      <circle cx="5" cy={30 + i * 25} r="5" fill="#0a0" />

      <!-- Use a foreignObject for the input widget -->
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
            style="width: 100%; height: 20px; font-size: 12px; box-sizing: border-box;"
            on:change={(e) => input.default = parseFloat(e.target.value)}
          />
        {:else if input.type === 'string'}
          <input
            type="text"
            value={input.default}
            style="width: 100%; height: 20px; font-size: 12px; box-sizing: border-box;"
            on:change={(e) => input.default = e.target.value}
          />
        {:else}
          <input
            type="text"
            value={input.default}
            style="width: 100%; height: 20px; font-size: 12px; box-sizing: border-box;"
            on:change={(e) => input.default = e.target.value}
          />
        {/if}
      </foreignObject>
    {/each}

    <!-- Render output sockets -->
    {#each node.outputs as output, j}
      <!-- Circle offset from the right edge by 5px; same vertical spacing as inputs -->
      <circle cx="155" cy={30 + j * 25} r="5" fill="#00a" />
    {/each}
  </g>
</svg>
  
  <style>
    input {
      border: 1px solid #ccc;
      border-radius: 2px;
    }
  </style>