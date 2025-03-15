import { doLoadPyodide } from "./pyodide_helpers";

class PythonExecutor {
    constructor(backend = 'auto') {
      this.backend = backend === 'auto' ? this.detectBackend() : backend;
      this.pyodide = null; // Will be set if Pyodide is used
      this.initializeBackend();
    }
  
    // Detect the available backend
    detectBackend() {
      if (typeof window !== 'undefined' && window.pywebview) {
        return 'pywebview';
      } else if (typeof pyodide !== 'undefined' || window.loadPyodide) {
        return 'pyodide';
      } else if (typeof WebSocket !== 'undefined') {
        // Check for Jupyter later with actual connection
        return 'jupyter';
      }
      throw new Error('No supported Python backend detected');
    }
  
    // Initialize the backend (e.g., load Pyodide)
    async initializeBackend() {
      if (this.backend === 'pyodide' && !this.pyodide) {
        this.pyodide = await doLoadPyodide( (text) => this.stdoutBuffer.push(text) );
      }
      // Jupyter initialization would go here (WebSocket setup)
    }
  
    // Buffers for capturing stdout/stderr
    stdoutBuffer = [];
    stderrBuffer = [];
  
    // Reset output buffers
    resetBuffers() {
      this.stdoutBuffer = [];
      this.stderrBuffer = [];
    }
  
    // Main execution method
    async execute(code, globals = {}, locals = {}) {
      this.resetBuffers();
      let result = null;
      let error = null;
  
      try {
        switch (this.backend) {
          case 'pyodide':
            result = await this.executePyodide(code, globals, locals);
            break;
          case 'pywebview':
            result = await this.executePyWebView(code, globals, locals);
            break;
          case 'jupyter':
            result = await this.executeJupyter(code, globals, locals);
            break;
          default:
            throw new Error(`Unsupported backend: ${this.backend}`);
        }
      } catch (err) {
        error = err.message || String(err);
      }
  
      return {
        stdout: this.stdoutBuffer.join('\n'),
        stderr: this.stderrBuffer.join('\n'),
        error,
        result
      };
    }
  
    // Pyodide execution
    async executePyodide(code, globals, locals) {
      if (!this.pyodide) {
        throw new Error('Pyodide not initialized');
      }
      // Set globals and locals
      Object.entries(globals).forEach(([key, value]) => this.pyodide.globals.set(key, value));
      Object.entries(locals).forEach(([key, value]) => this.pyodide.globals.set(key, value));
      // Run code
      const result = await this.pyodide.runPythonAsync(code);
      return result; // Returns undefined if no return value
    }
  
    // PyWebView execution
    async executePyWebView(code, globals, locals) {
      if (!window.pywebview) {
        throw new Error('PyWebView not available');
      }
      // PyWebView doesn't natively support globals/locals, so we simulate it
      const contextCode = `
globals().update(${JSON.stringify(globals)});
locals().update(${JSON.stringify(locals)});
${code}
      `;
      const response = await window.pywebview.api.run_python(contextCode);
      this.stdoutBuffer.push(response.output || '');
      console.debug('PyWebView response:', response );
      return response.result; // Assumes PyWebView API returns { result, output }
    }
  
    // Jupyter Kernel Gateway execution (placeholder)
    async executeJupyter(code, globals, locals) {
      // Placeholder: Requires WebSocket setup to a Jupyter Kernel Gateway
      throw new Error('Jupyter backend not implemented yet');
      // Would involve sending code via WebSocket and parsing response
    }
  }
  
  // Export a singleton instance or factory function if preferred
  export default PythonExecutor;