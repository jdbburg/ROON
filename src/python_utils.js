
import PythonExecutor from './PythonExecutor';

const PYTHON_BACKEND = process.env.PYTHON_BACKEND || 'auto';

export const executor = new PythonExecutor( PYTHON_BACKEND );

const pythonEngineCode = `
import json
import sys
import roon.engine as engine
import sys
sys.path.append('./roon/')

# Evaluate using your DAG logic in engine.py
result = engine.generate_python_script(graphData)
result
`;

export async function runPython2JSON( module_path ) {
    console.log("Running Python2JSON...");
    const pythonCode = `
import json
import importlib.resources as resources
with resources.path("roon", "static") as static_path:
    sys.path.append(str(static_path))
import sys
sys.path.append('/user-data/')
sys.path.append('./nodes/')
import roon.allpy2json
import roon.builtin2json as builtin2json

script_source = "Running allpy2json..."
#print("Running allpy2json...")
# Evaluate using your DAG logic in engine.py
#script_source = allpy2json.analyze_module_functions( "${module_path}", None, "" )
defs = builtin2json.analyze_installed_module_functions( "${module_path}", None )
#print(script_source)
result = defs
`;

    let output = null;
    
    try {
        // output = generic_python_runner( pythonCode );
        output = await executor.execute( pythonCode, {}, {} );
        console.log("JSON Output:", output);
        // if (output !== undefined) {
        //     // console.log( JSON.parse(output)) ;
        //     return JSON.parse(output)["result"];
        // }
           
    }
    catch (err) {
        console.error("Error running NODE DEFS:", String(err) );
        output = { error: String(err), result: null };
    }
    return output;
}

export async function runEngine( graphData, execute = true ) {
    console.log("Running Engine...");
    let output = null;
    try{
        output = await executor.execute( pythonEngineCode, {graphData: graphData}, {} );
    } catch (err) {
        console.error("Error running engine:", String(err) );
        stdout( String(err) );
    }
    
    console.log("Engine Output:", output);

    if (!execute) {
        return output;
    }

    console.log("Running Engine Complete");
    console.log("Running generated graph script...");
    let script_output = await executor.execute( output["result"], {graphData: graphData}, {} );
    executor.stdoutHandler( script_output["stdout"] );
    executor.stderrHandler( script_output["stderr"] );

    // append the output to the stdout buffer
    // if (stdoutHandler) {
    //     stdoutHandler( script_output["stdout"] );
    // } else {
    //     console.log("NO HANDLER: stdout:", script_output["stdout"]);
    // }
    // if (stderrHandler) {
    //     stderrHandler( script_output["stderr"] );
    // }

    console.log("Running generated graph script complete");
    console.log("Script Output:", script_output);
    // await runrun( output["result"] );

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
    

    // 4) Run the Python code
    console.log('Running engine...');
    console.debug('Python code:', pythonCode);
    // let output = null;
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