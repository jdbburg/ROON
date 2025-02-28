<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let commands = [];
    let searchTerm = "";
    let filteredCommands = commands;
  
    $: filteredCommands = commands.filter(cmd => 
      cmd.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  
    function handleKeyDown(e) {
      if (e.key === "Enter" && filteredCommands.length > 0) {
        dispatch('selectCommand', filteredCommands[0]);
      }
    }
  </script>
  
  <div class="palette">
    <input type="text" placeholder="Type a command..." bind:value={searchTerm} on:keydown={handleKeyDown} autofocus />
    <ul>
      {#each filteredCommands as cmd}
        <li on:click={() => dispatch('selectCommand', cmd)}>{cmd.name}</li>
      {/each}
    </ul>
  </div>
  
  <style>
    .palette {
      background: white;
      border-radius: 5px;
      padding: 10px;
      width: 300px;
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
  </style>