<script>
    import { createEventDispatcher } from 'svelte';
    import { socketColorForType, socketPosition } from './node_utilities.ts';
    import { config } from './CONF.js';
    export let socket;
    export let index;
    export let nodeId; // id of our Node if needed
    export let socketFlow;
    export let showWidgets;
    const socketRadius = 4
    const dispatch = createEventDispatcher();

    let offsetX = (socketFlow == "input" ? 8 : -50 );

  function handleInputClick(e) {
    e.stopPropagation();
    e.preventDefault();
    // Explicitly focus the input element
    e.target.focus();
  }

    // Called when the user pointer-downs on an output socket
  function handleSocketPointerDown(type, socketName, index, event) {
    if ( type === 'input' ) return; // for now, until we handle correctly
    event.stopPropagation();  // don’t trigger node-drag
    event.preventDefault();
    dispatch('socketPointerDown', {
      socketType: type,           // 'output' (or 'input' if you add that)
      socketName,     // e.g. "result"
      index,
      nodeId: nodeId,
      clientX: event.clientX,
      clientY: event.clientY
    });
  }
</script>

<style>
    /* Smooth scale animation on hover */
.socket-group {
    transition: transform 0.1s ease;
    transform-origin: center;
    transform-box: fill-box; /* Ensures transform origin is the circle's center */
    cursor: pointer;
  }
.socket-group:hover {
    transform: scale(2.5);
  }

</style>
<g>
    <text
      x={socketPosition(socketFlow, index).x + (socketFlow === "input" ? 8 : -8)}
      y={config.node.header.height + index * config.node.socket.separation}
      font-size="10"
      fill="#333"
      dominant-baseline="middle"
      text-anchor={socketFlow === "input" ? "start" : "end"}
  >
      {socket.name}
  </text>
  <text></text>

    {#if (socketFlow == "input" && showWidgets && socket.default !== undefined)}
    <foreignObject
        x="17"
        y={config.node.header.height + index * config.node.socket.separation}
        width="130"
        height="24"
        style="overflow: visible; pointer-events: none;"
      >
      <div style="pointer-events: auto;">
      {#if socket.type === 'number'}
          <input
            type="number"
            value={socket.default}
            style="width:75%; height:20px; font-size:12px; box-sizing:border-box;"
            on:change={(e) => socket.default = parseFloat(e.target.value)}
            on:pointerdown|stopPropagation
            on:click|stopPropagation={handleInputClick}
            on:focus|stopPropagation
          />
        {:else if socket.type === 'string'}
          <input
            type="text"
            value={socket.default}
            style="width:100%; height:20px; font-size:12px; box-sizing:border-box; pointer-events: auto;"
            on:change={(e) => socket.default = e.target.value}
            on:pointerdown|stopPropagation
            on:click|stopPropagation={handleInputClick}
            on:focus|stopPropagation
          />
        {:else}
          <input
            type="text"
            value={socket.default}
            style="width:100%; height:20px; font-size:12px; box-sizing:border-box;"
            on:change={(e) => socket.default = e.target.value}
            on:pointerdown|stopPropagation
            on:click|stopPropagation={handleInputClick}
            on:focus|stopPropagation
          />
        {/if}
      </div>
    </foreignObject>
    {/if}


    <g class="socket-group"
        on:pointerdown = {(e) => handleSocketPointerDown(socketFlow, socket.name, index, e)}
        >
        <!-- circle outline -->
        <circle
            class="socket ${socket.type}-socket"
            cx={socketPosition(socketFlow, index).x}
            cy={socketPosition(socketFlow, index).y}
            r={socketRadius + 2}
            fill={socketColorForType(socket.type, 90, 20)}
        /> 
        <!-- inner -->
        <circle
            class="socket output-socket"
            cx={socketPosition(socketFlow, index).x}
            cy={socketPosition(socketFlow, index).y}
            r={socketRadius}
            fill={socketColorForType(socket.type)}
        />
    </g>
</g>