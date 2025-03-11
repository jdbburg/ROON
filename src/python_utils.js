export async function writeFileToFS( filename ) {
    const file_data = await (await fetch(`/${filename}`)).text();
    pyodide.FS.writeFile(`/${filename}`, file_data, { encoding: "utf8" });
}

export async function doLoadPyodide( handleStdOut ) {
    handleStdOut("Setting up Pyodide...");
    let pyodide = await window.loadPyodide();
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

    writeFileToFS("engine.py");
    writeFileToFS("example_functions.py");
    writeFileToFS("matplotlib_nodes.py");

    document.pyodideMplTarget = document.getElementById('MPL-container');

    pyodide.setStdout({ batched: handleStdOut });
    pyodide.setStderr({ batched: handleStdOut });
    
    window.pyodide = pyodide;
    handleStdOut("Pyodide done loading");
  return pyodide;
}

export async function runEngine( graphData ) {
    // 1) Load engine.py from your server (or embed it directly)
    
    // This executes the code in engine.py so that its functions become available in Pyodide
    let pyodide = window.pyodide;
    

    
    let graph_namespace = pyodide.toPy( { graphData: graphData } );

    // 3) Build a Python snippet that:
    //    - Imports json and engine
    //    - Parses graphJson
    //    - Calls the evaluate function
    //    - Returns the result as a JSON string
    const pythonCode = `
import json

# Convert the string into a Python dict
#graph_dict = json.loads( graphData )

# Evaluate using your DAG logic in engine.py
script_source = generate_python_script(graphData)
script_source
`;

    const enginePy = await (await fetch('/engine.py')).text();
    await pyodide.runPythonAsync(enginePy, { globals: graph_namespace });

    // 4) Run the Python code
    console.log('Running engine...');
    console.log('Python code:', pythonCode);
    const output = pyodide.runPython(pythonCode, { globals: graph_namespace });

    // output is whatever the last expression returns, so we have a JSON string
    console.log('Engine raw output:\n', output);

    await runrun( output );
}

async function runrun( script ){
    console.log("Running Running...");
    let pyodide = window.pyodide;
    let graph_namespace = pyodide.toPy( { graphData: graphData } );
    try {
        let source = script
        console.log("Running generated script...:", source );
        let output = pyodide.runPython( source );
        console.log("Run generated script complete:", output);
    }  catch (err) {
        console.error("Error running generated script:", String(err) );

    }
    console.log("Running Engine Complete");
    let mpl = document.getElementById('MPL-container');
    // hide the mpl container
    mpl.style.display = "block";
}