import { get, set } from 'idb-keyval';
// import { showDirectoryPicker } from 'fs-picker';

let stdout = null;

export async function mountDirectory() {
    // Access idb-keyval methods from the global scope (via CDN)
    // const { get, set } = window.idbKeyval;

    let dirHandle;

    // Try to retrieve the stored directory handle
    dirHandle = await get('directoryHandle');

    if (dirHandle) {
        // Verify permissions are still granted
        const permissionStatus = await dirHandle.queryPermission({ mode: 'readwrite' });
        if (permissionStatus !== 'granted') {
            // Request permission again if not granted
            const newPermissionStatus = await dirHandle.requestPermission({ mode: 'readwrite' });
            if (newPermissionStatus !== 'granted') {
                dirHandle = null; // Permission denied, reset to prompt user
            }
        }
    }

    // If no valid handle exists, prompt the user
    if (!dirHandle) {
        dirHandle = await showDirectoryPicker();
        const permissionStatus = await dirHandle.requestPermission({ mode: 'readwrite' });
        if (permissionStatus !== 'granted') {
            throw new Error('readwrite access to directory not granted');
        }
        // Save the handle to IndexedDB
        await set('directoryHandle', dirHandle);
    }

    // Mount the directory in Pyodide
    const nativefs = await window.pyodide.mountNativeFS('/user-data', dirHandle);
    await nativefs.syncfs(); // Sync changes to the native filesystem
    console.log('Directory mounted at /user-data');
}

export async function writeFileToFS( filename ) {
    const file_data = await (await fetch(`/${filename}`)).text();
    pyodide.FS.writeFile(`/${filename}`, file_data, { encoding: "utf8" });
}

export async function doLoadPyodide( handleStdOut ) {
    stdout = handleStdOut;
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
    // const enginePy = await (await fetch('/engine.py')).text();
    // This executes the code in engine.py so that its functions become available in Pyodide
    // await pyodide.runPythonAsync(enginePy);

    // handleStdOut("Writing python files to FS...");
    // writeFileToFS("engine.py");
    // writeFileToFS("example_functions.py");
    // writeFileToFS("matplotlib_nodes.py");
    // writeFileToFS("uproot_nodes.py");

    // handleStdOut("Writing example data to FS...");
    // writeFileToFS("example.root");

    document.pyodideMplTarget = document.getElementById('MPL-container');

    pyodide.setStdout({ batched: handleStdOut });
    pyodide.setStderr({ batched: handleStdOut });
    
    window.pyodide = pyodide;
    handleStdOut("Pyodide done loading");
  return pyodide;
}

export async function runEngine( graphData, execute = true ) {
    // alias our window level pyodide instance
    let pyodide = window.pyodide;

    // 1) Create a Python namespace that contains the graph data
    // this is the cleanest way to pass data between JS and Python
    let graph_namespace = pyodide.toPy( { graphData: graphData } );

    // 2) Load engine.py from your server (or embed it directly)
    // const enginePy = await (await fetch('/engine.py')).text();
    // This executes the code in engine.py so that its functions become available in Pyodide
    // await pyodide.runPythonAsync(enginePy, { globals: graph_namespace });

    // 3) Build a Python snippet that:
    //    - Imports json and engine
    //    - Parses graphJson
    //    - Calls the evaluate function
    //    - Returns the result as a JSON string
    const pythonCode = `
import json
import sys
sys.path.append('/user-data/')
import engine

# Evaluate using your DAG logic in engine.py
script_source = engine.generate_python_script(graphData)
script_source
`;

    // 4) Run the Python code
    console.log('Running engine...');
    console.debug('Python code:', pythonCode);
    const output = pyodide.runPython(pythonCode, { globals: graph_namespace });

    // output is whatever the last expression returns, so we have a JSON string
    console.debug('Engine raw output:\n', output);

    if (!execute) {
        return output;
    }
    await runrun( output );
    return output;
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
        stdout( String(err) );

    }
    console.log("Running Engine Complete");
    let mpl = document.getElementById('MPL-container');
    // hide the mpl container
    mpl.style.display = "block";
}