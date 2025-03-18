<script>
  // Grid.svelte
    import { config } from './config.js';
    export let cameraX = 0; // X position of the camera (panning)
    export let cameraY = 0; // Y position of the camera (panning)
    export let scale = 1;   // Zoom level (scale factor)
    export let width = 800; // Viewport width
    export let height = 600;// Viewport height
  
    const gridSpacing = config.grid.spacing; // Base spacing between grid lines (unscaled)
    const majorInterval = config.grid.major.interval; // Every 5th line is major
  
    // Calculate scaled spacing for rendering
    $: scaledSpacing = gridSpacing * scale;
  
    // Calculate the visible range in unscaled coordinates
    $: startX = Math.ceil(cameraX / (gridSpacing * majorInterval) ) * ( gridSpacing * majorInterval) - gridSpacing * majorInterval;
    $: endX =  startX + width + gridSpacing * majorInterval;
    $: startY = Math.ceil(cameraY / (gridSpacing * majorInterval) ) * ( gridSpacing * majorInterval) - gridSpacing * majorInterval;
    $: endY = startY + height + gridSpacing * majorInterval;
  
    $: numberOfVerticalLines = Math.ceil((endX - startX) / gridSpacing);
    $: numberOfHorizontalLines = Math.ceil((endY - startY) / gridSpacing);
    // Generate lines in unscaled space, then scale them
    $: verticalLines = Array.from(
      { length: numberOfVerticalLines },
      (_, i) => startX + i * gridSpacing
    );
    $: horizontalLines = Array.from(
      { length: numberOfHorizontalLines },
      (_, i) => startY + i * gridSpacing
    );
  </script>
  
  <!-- Group with scale first, then translate -->
  <!-- <g transform="translate({-cameraX/scale} {-cameraY/scale})"> -->
    <g>
    <!-- Vertical lines -->
    {#each verticalLines as x, i}
      {#if i % majorInterval !== 0}
        <line
          x1={x}
          y1={startY}
          x2={x}
          y2={endY}
          class={i % majorInterval === 0 ? 'major' : 'minor'}
        />
      {/if}
    {/each}
  
    <!-- Horizontal lines -->
    {#each horizontalLines as y, i}
      <line
        x1={startX}
        y1={y}
        x2={endX}
        y2={y}
        class={i % majorInterval === 0 ? 'major' : 'minor'}
      />
    {/each}

    <!-- Vertical lines -->
    {#each verticalLines as x, i}
      {#if i % majorInterval === 0}
        <line
          x1={x}
          y1={startY}
          x2={x}
          y2={endY}
          class={i % majorInterval === 0 ? 'major' : 'minor'}
        />
      {/if}
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