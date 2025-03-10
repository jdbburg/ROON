<script>
    import { onMount } from "svelte";

    export let pyodide; // the Pyodide instance passed from the parent
  
    // State for the REPL
    let userInput = "";
    let outputLines = [];

  
    async function doLoadPyodide() {
		pyodide = await window.loadPyodide();
        await pyodide.loadPackage("micropip");
        const micropip = pyodide.pyimport("micropip");
        await micropip.install('numpy');
        console.log("Installed numpy");
        await micropip.install('awkward');
        console.log("Installed awkward");
        await micropip.install('matplotlib');
        console.log("Installed matplotlib");
        await micropip.install('uproot');
        console.log("Installed uproot");

        // 1) Load engine.py from your server (or embed it directly)
        const enginePy = await (await fetch('/engine.py')).text();
        // This executes the code in engine.py so that its functions become available in Pyodide
        await pyodide.runPythonAsync(enginePy);

        // const example_fns = await (await fetch('/example_functions.py')).text();

        pyodide.setStdout({ batched: 
          (output) => {
              console.log("STDOUT: ", output);
              outputLines = [...outputLines, output];
            }
          }
          );

        pyodide.setStderr({ batched: 
          (output) => {
              console.log("STDERR: ", output);
              outputLines = [...outputLines, output];
            }
          }
          );
        
        window.pyodide = pyodide;
	  return pyodide;
	}

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
              // 1) Redirect sys.stdout to a StringIO buffer
      //    We'll set it fresh for each command so we start empty.
//       await pyodide.runPythonAsync(`
// import io, sys
// sys.stdout = io.StringIO()
//       `);

      // 2) Execute the user code
      const result = await pyodide.runPythonAsync(code);

      let printed = "";
      // 3) Capture everything that was printed
//       const printed = await pyodide.runPythonAsync(`
// _ = sys.stdout.getvalue()
// sys.stdout.truncate(0)
// sys.stdout.seek(0)
// _
//       `);
        // Run the code in Pyodide
        // const result = await pyodide.runPythonAsync(code);

        // Append the command + result to our output
        outputLines = [`>>> ${code}`, result, printed, ...outputLines];
      } catch (err) {
        // On error, show the traceback or error message
        outputLines = [`>>> ${code}`, String(err), ...outputLines];
      }
    }

    onMount(async () => {
        console.log("PyodideREPL onMount");
        await doLoadPyodide();
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