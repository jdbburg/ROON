
import PythonExecutor from './PythonExecutor';

const PYTHON_BACKEND = process.env.PYTHON_BACKEND || 'auto';

export const executor = new PythonExecutor( PYTHON_BACKEND );

// this is the callback used to update the REPL output
export let stdout = null;

export async function runPython2JSON( module_path) {
    console.log("Running Python2JSON...");
    return null;
    let pyodide = window.pyodide;

    let namespace = pyodide.toPy( {  } );
    const pythonCode = `
import json
import sys
sys.path.append('/user-data/')
sys.path.append('./nodes/')
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
        // output = generic_python_runner( pythonCode );
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
    console.log("Running Engine...");
    return null;
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
    let lastNamespace = pyodide.toPy( { graphData: graphData } );
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