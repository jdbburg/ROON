<script>
    export let cameraX = 0; // X position of the camera (panning)
    export let cameraY = 0; // Y position of the camera (panning)
    export let scale = 1;   // Zoom level (scale factor)
    export let width = 800; // Viewport width
    export let height = 600;// Viewport height
  
    const gridSpacing = 50; // Base spacing between grid lines (unscaled)
    const majorInterval = 5; // Every 5th line is major
  
    // Calculate scaled spacing for rendering
    $: scaledSpacing = gridSpacing * scale;
  
    // Calculate the visible range in unscaled coordinates
    $: startX = cameraX;
    $: endX = Math.ceil((cameraX + (width / 2) * scale) / gridSpacing) * gridSpacing;
    $: startY = cameraY;
    $: endY = Math.ceil((cameraY + (height / 2) * scale) / gridSpacing) * gridSpacing;
  
    // Generate lines in unscaled space, then scale them
    $: verticalLines = Array.from(
      { length: Math.ceil((endX - startX) / gridSpacing) + 1 },
      (_, i) => startX + i * gridSpacing
    );
    $: horizontalLines = Array.from(
      { length: Math.ceil((endY - startY) / gridSpacing) + 1 },
      (_, i) => startY + i * gridSpacing
    );
  </script>
  
  <!-- Group with scale first, then translate -->
  <g transform="scale({scale}) translate({-cameraX / scale} {-cameraY / scale})">
    <!-- Vertical lines -->
    {#each verticalLines as x}
      <line
        x1={x}
        y1={startY}
        x2={x}
        y2={endY}
        class={Math.abs(x) % (gridSpacing * majorInterval) === 0 ? 'major' : 'minor'}
      />
    {/each}
  
    <!-- Horizontal lines -->
    {#each horizontalLines as y}
      <line
        x1={startX}
        y1={y}
        x2={endX}
        y2={y}
        class={Math.abs(y) % (gridSpacing * majorInterval) === 0 ? 'major' : 'minor'}
      />
    {/each}
  </g>
  
  <style>
    line.minor {
      stroke: #ddd; /* Light gray for minor lines */
      stroke-width: 1;
    }
    line.major {
      stroke: #888; /* Darker gray for major lines */
      stroke-width: 2;
    }
  </style>