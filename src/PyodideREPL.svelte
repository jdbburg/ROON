<script>
    import { onMount, createEventDispatcher } from "svelte";
    import { doLoadPyodide, mountDirectory, lastNamespace, generic_python_runner, stdout } from "./python_utils.js";
    import CodeEditor from "./CodeEditor.svelte";

    const dispatch = createEventDispatcher();

    export let pyodide; // the Pyodide instance passed from the parent
    let pythonCode = `print("Hello, Pyodide!")`;

    function handleCodeChange(newCode) {
        // code = newCode;
    }

    // State for the REPL
    let userInput = "";
    let outputLines = [];

    // Execute the entered code on pressing Enter
    async function handleEnter(v) {
      if ( window.pywebview ) {
        // stdout( " USING PYWEBVIEW ");
      }
        console.log("handleEnter, code=", v);
      if (!pyodide && !window.pywebview) {
        console.error("Pyodide not loaded yet and python not ready");
        return;
      }
      // const code = userInput;
      userInput = "";  // clear the input
      let code = v;

      try {
        // let result = await pyodide.runPythonAsync(code);
        let result = await generic_python_runner(code, {})
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
        pyodide = await doLoadPyodide( handleStdOut );
        if ( window.pywebview ) {
          stdout( "nvm, we are native");
          dispatch("pythonReady");
          dispatch("pyodideLoaded");
        } else {
          await mountDirectory(pyodide);
          dispatch("pyodideLoaded");
        }
    });
  </script>
  
  <style>
    /* Fixed REPL at bottom of screen */
    .repl {
      
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 23em;
      max-height: 25%;
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
      padding-bottom: 5px;
      /* background: #333; */
    }
  
    /* input {
      width: 100%;
      border: none;
      background: #333;
      color: #eee;
      font-family: inherit;
      font-size: 14px;
      padding: 3px;
      outline: none;
    } */
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
      
      <!-- <input
        type="text"
        bind:value={userInput}
        on:keydown={(e) => {
          if (e.key === 'Enter') {
            handleEnter();
          }
        }}
        placeholder="Type Python code and press Enter..."
      /> -->

      <CodeEditor value={pythonCode} onChange={handleCodeChange} onShiftEnter={handleEnter} immediateMode={true}/>
    </div>
  </div>