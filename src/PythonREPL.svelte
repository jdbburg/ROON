<script>
    import { onMount, createEventDispatcher } from "svelte";
    import { executor } from "./python_utils.js";
    import CodeEditor from "./CodeEditor.svelte";

    const dispatch = createEventDispatcher();

    export let pyodide; // the Pyodide instance passed from the parent
    export let pythonCode;
    let executionCount = 0;


    function handleCodeChange(newCode) {
        pythonCode = newCode;
        dispatch('update', pythonCode);  // Notify parent of the change
    }

    // State for the REPL
    let outputLines = [];

    // Execute the entered code on pressing Enter
    async function handleEnter(v) {
      console.log("handleEnter, code=", v);
      let code = v;

      try {
        // let result = await pyodide.runPythonAsync(code);
        let result = await executor.execute(code, {}, {});
        if (result === undefined) {
            result = "";
        }
        // result = result["stdout"];
        let execStdOut = `[${executionCount}] ${result["stdout"]}`;
        if (result["stdout"] === "") {
            execStdOut = "";
        }
        if (result["stderr"] !== "") {
            execStdOut += `\nERROR:${result["stderr"]}`;
        }
        executionCount++;
        // later take care of stderr and return code
        // Append the command + result to our output
        outputLines = [`>>> ${code}`, execStdOut, ...outputLines];
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
        // setup the Python executor

        executor.stdoutHandler = handleStdOut;
        executor.stderrHandler = handleStdOut;
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
      overflow-y: auto;
      /* background: #333; */
    }

    .fullscreen {
      position: fixed;
      top: 1em;
      left: 2%;
      width: 96%;
      height: calc( 100% - 2em);
      max-height: 100%;
      overflow-y: auto;
      z-index: 9999;
    }

    .side-by-side {
      display: flex;
      flex-direction: row;
      /* width: 100%; */
      /* height: 100%; */
    }

    .top-bottom {
      display: flex;
      flex-direction: column;
    }

    .top {
      flex: 6;
      padding: 0px;
      background-color: #222;
      color: #eee;
    }

    .bottom {
      flex: 1;
      padding: 0px;
      background-color: #333;
      color: #eee;
    }
    .left {
      flex: 1;
      padding: 0px;
      background-color: #222;
      color: #eee;
    }
    .hidden {
      display: none;
    }
    .right {
      flex: 1;
      padding: 0px;
      background-color: #333;
      color: #eee;
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

  <div id="repl" class="repl top-bottom">
    <!-- Output region showing command + result lines -->
    <div id="console-output" class="output top">
      {#each outputLines as line}
        <div class="line">{line}</div>
      {/each}
    </div>
    
    <!-- Input for Python commands, uses codemirror -->
    <div id="code-editor" class="input-area bottom">
      <CodeEditor value={pythonCode} onChange={handleCodeChange} onShiftEnter={handleEnter} immediateMode={true}/>
    </div>  
    <div class="fullscreen hidden side-by-side left right" style="display:none;"></div>
    <div class="fullscreen hidden side-by-side right" style="display:none;"></div>
  </div>