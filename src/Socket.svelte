<script>
    import { createEventDispatcher } from 'svelte';
    export let socket;
    export let index;
    export let nodeId; // id of our Node if needed
    export let socketFlow;
    export let showWidgets;
    const socketRadius = 4
    const dispatch = createEventDispatcher();

    let offsetX = (socketFlow == "input" ? 10 : -50 );

    const hueOverrides = {
        "str": 72,
        "string" : 72,
        "number" : 330
    }

    function socketPosition( ){
        if (socketFlow == "input"){
            return { x: 0, y: 30 + index * 25 }
        }  

        return { x: 160, y:30 + index * 25 }
    }


    function colorForType(type, saturation = 60, lightness = 50) {
        console.debug("Coloring socket of type: ", socket.type)
        
    // Simple hash
    let hash = 0;
    for (let i = 0; i < type.length; i++) {
      hash = type.charCodeAt(i) + ((hash << 5) - hash);
      // no need for bitwise & here in JS, but you can do hash |= 0 to keep 32-bit
    }

    // Convert the hash to a hue from 0..359
    let hue = Math.abs(hash) % 360;
    if (type in hueOverrides)
        hue = hueOverrides[type]

    // Return an HSL color with a fixed saturation & lightness
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  }

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
        x={socketPosition().x + offsetX}
        y={30 + index * 25}
        font-size="10"
        fill="#333"
        dominant-baseline="middle"
        >
        {socket.name}
    </text>

    {#if (socketFlow == "input" && showWidgets)}
    <foreignObject
        x="17"
        y={20 + index * 25}
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
        <!-- outer -->
        <circle
            class="socket ${socket.type}-socket"
            cx={socketPosition().x}
            cy={socketPosition().y}
            r={socketRadius + 2}
            fill={colorForType(socket.type, 90, 20)}
        /> 
        <!-- inner -->
        <circle
            class="socket output-socket"
            cx={socketPosition().x}
            cy={socketPosition().y}
            r={socketRadius}
            fill={colorForType(socket.type)}
        />
    </g>
</g>