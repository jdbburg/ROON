
import { get, set } from 'idb-keyval';
export async function mountDirectory() {
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
    console.log("Loading Pyodide...but first checking for pywebview: ", !!window.is_pywebview);
    if ( window.pywebview ) {
        console.log("Running in pywebview, no need to use Pyodide");
        window.pyodide = null;
        return;
    }
    handleStdOut("Setting up Pyodide...");
    let pyodide = await window.loadPyodide({
        packages: ['micropip', 'numpy', 'matplotlib']
    });

    // sometimes it takes a momemnt for the js_api to load
    if ( window.pywebview ) {
        console.log("Running in pywebview, no need to use Pyodide");
        window.pyodide = null;
        return;
    }
    
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