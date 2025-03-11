<script>
    import { onMount } from "svelte";
    import { doLoadPyodide } from "./python_utils.js";

    export let pyodide; // the Pyodide instance passed from the parent
  
    // State for the REPL
    let userInput = "";
    let outputLines = [];

    // Execute the entered code on pressing Enter
    async function handleEnter() {
        console.log("handleEnter");
      if (!pyodide) {
        console.error("Pyodide not loaded yet");
        return;
      }
      const code = userInput;
      userInput = "";  // clear the input
  
      try {
        let result = await pyodide.runPythonAsync(code);
        if (result === undefined) {
            result = "";
        }
        // Append the command + result to our output
        outputLines = [`>>> ${code}`, result, ...outputLines];
      } catch (err) {
        // On error, show the traceback or error message
        outputLines = [`>>> ${code}`, String(err), ...outputLines];
      }
    }

    function handleStdOut(output) {
      console.log("STDOUT: ", output);
      outputLines = [output, ...outputLines];
    }

    onMount(async () => {
        console.log("PyodideREPL onMount");
        pyodide = await doLoadPyodide( handleStdOut );
    });
  </script>
  
  <style>
    /* Fixed REPL at bottom of screen */
    .repl {
      
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 200px;
      background-color: #222;
      color: #eee;
      display: flex;
      flex-direction: column;
      font-family: monospace;
      z-index: 999; /* ensure it's above other elements */
      /* display: none; */
    }
  
    .output {
      flex: 1;
      overflow: auto;
      padding: 5px;
    }
  
    .line {
      white-space: pre-wrap;
      margin: 0 0 2px 0;
    }
  
    .input-area {
      border-top: 1px solid #555;
      padding: 5px;
      background: #333;
    }
  
    input {
      width: 100%;
      border: none;
      background: #333;
      color: #eee;
      font-family: inherit;
      font-size: 14px;
      padding: 3px;
      outline: none;
    }
  </style>
  
  <div class="repl">
    <!-- Output region showing command + result lines -->
    <div class="output">
      {#each outputLines as line}
        <div class="line">{line}</div>
      {/each}
    </div>
  
    <!-- Single-line input for Python commands -->
    <div class="input-area">
      <input
        type="text"
        bind:value={userInput}
        on:keydown={(e) => {
          if (e.key === 'Enter') {
            handleEnter();
          }
        }}
        placeholder="Type Python code and press Enter..."
      />
    </div>
  </div>