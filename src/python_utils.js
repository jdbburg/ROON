import { get, set } from 'idb-keyval';
// import { showDirectoryPicker } from 'fs-picker';

export let stdout = null;
// I tried to add this to keep the script context available in the REPL, but not working
export let lastNamespace = null;

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
    let pyodide = await window.loadPyodide({
        packages: ['micropip', 'numpy', 'matplotlib']
    });
    
    const micropip = pyodide.pyimport("micropip");
    
    await micropip.install('awkward');
    console.log("Installed awkward");
    handleStdOut("Installed awkward");

    await micropip.install('uproot');
    console.log("Installed uproot");
    handleStdOut("Installed uproot");

    document.pyodideMplTarget = document.getElementById('MPL-container');

    pyodide.setStdout({ batched: handleStdOut });
    pyodide.setStderr({ batched: handleStdOut });
    
    window.pyodide = pyodide;
    pyodide.setDebug(true);
    handleStdOut("Pyodide done loading");
  return pyodide;
}

export async function runPython2JSON( module_path) {
    let pyodide = window.pyodide;

    let namespace = pyodide.toPy( {  } );
    const pythonCode = `
import json
import sys
sys.path.append('/user-data/')
import allpy2json

script_source = "Running allpy2json..."
#print("Running allpy2json...")
# Evaluate using your DAG logic in engine.py
script_source = allpy2json.analyze_module_functions( "${module_path}", None, "/user-data/" )
#print(script_source)
json.dumps(script_source)
`;

    let output = null;
    try {
        output = await pyodide.runPythonAsync(pythonCode, { globals: namespace });
        console.log("JSON Output:", output);
        if (output !== undefined) {
            console.log( JSON.parse(output)) ;
            return JSON.parse(output);
        }
           
    }
    catch (err) {
        console.error("Error running engine:", String(err) );
        stdout( String(err) );
    }
    return output;
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
    let output = null;
    try {
        output = pyodide.runPython(pythonCode, { globals: graph_namespace });
    }
    catch (err) {
        console.error("Error running engine:", String(err) );
        stdout( String(err) );
    }
    // const output = pyodide.runPython(pythonCode, { globals: graph_namespace });

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
    lastNamespace = pyodide.toPy( { graphData: graphData } );
    try {
        let source = script
        console.log("Running generated script...:", source );
        let output = pyodide.runPython( source, { globals: lastNamespace } );
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

export function generateNodeDefs( name ){

}