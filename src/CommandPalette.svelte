<script>
    import { createEventDispatcher } from 'svelte';

    export let commands = [];
    const dispatch = createEventDispatcher();
    let searchTerm = "";
    let filteredCommands = commands;
    let selectedIndex = 0;  // NEW: tracks which command is highlighted
    let listElement;  // NEW: reference to the <ul> element

     // Reactively scroll to the selected item
    $: if (listElement && filteredCommands.length > 0) {
      const selectedItem = listElement.children[selectedIndex];
      if (selectedItem) {
        selectedItem.scrollIntoView({ behavior: 'auto', block: 'nearest' });
      }
    }
  
    $: filteredCommands = commands.filter(cmd =>
      cmd.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    $: selectedIndex = 0;  // reset selection each time search changes

  
    function handleKeyDown(e) {
      if (e.key === "Enter" && filteredCommands.length > 0) {
        dispatch('selectCommand', filteredCommands[selectedIndex]);
      }
      // ARROW DOWN moves selection forward
      else if (e.key === 'ArrowDown') {
        if (filteredCommands.length > 0) {
            selectedIndex = (selectedIndex + 1) % filteredCommands.length;
            e.preventDefault();
        }
      }
      // ARROW UP moves selection backward
      else if (e.key === 'ArrowUp') {
        if (filteredCommands.length > 0) {
            selectedIndex = (selectedIndex - 1 + filteredCommands.length) % filteredCommands.length;
            e.preventDefault();
        }
      }
    }
  </script>
  
  <div class="palette">
    <input
      type="text"
      placeholder="Type a command..."
      bind:value={searchTerm}
      on:keydown={handleKeyDown}
      autofocus
    />
    <ul bind:this={listElement}>
      {#each filteredCommands as cmd, i}
        <!-- Highlight the currently selected item -->
        <li
        class:selected={i === selectedIndex}
        on:click={() => dispatch('selectCommand', cmd)}
        >
        {cmd.name}
        </li>
      {/each}
    </ul>
  </div>
  
  <style>
    .palette {
      background: white;
      border-radius: 5px;
      padding: 10px;
      width: 50%;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    input {
      width: 100%;
      padding: 5px;
      font-size: 14px;
      margin-bottom: 5px;
    }
    ul {
      list-style: none;
      margin: 0;
      padding: 0;
      max-height: 150px;
      overflow-y: auto;
    }
    li {
      padding: 5px;
      cursor: pointer;
    }
    li:hover {
      background: #eee;
    }
    li.selected {
      background: #eee;  /* highlight color */
    }
  </style>