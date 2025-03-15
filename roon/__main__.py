import webview
import os
import io
import sys

import roon.allpy2json as allpy2json
import roon.engine as engine

# Path to your Svelte app's build folder
svelte_build_dir = os.path.abspath("./roon/static/svelte")  # Adjust path as needed

# Serve the Svelte app locally
def start_server():
    import http.server
    import socketserver
    import threading

    os.chdir(svelte_build_dir)
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)

    # Run server in a separate thread
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return f"http://localhost:{PORT}"

# Python functions to expose to JavaScript

exec_globals = {}
class Api:

    # def source_to_json_nodes(self, module_path):
    #     # Call the function from the snippet above
    #     try: 
    #         node_defs = allpy2json.analyze_module_functions(module_path) 
    #     except Exception as e:
    #         return {
    #             "result": None,
    #             "output": None,
    #             "error": str(e)
    #         }
    #     return {
    #             "result": node_defs,
    #             "output": node_defs,
    #             "error": None
    #         }

    def run_python(self, code):
        try:
            # Capture stdout and stderr
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            sys.stdout = stdout_buffer
            sys.stderr = stderr_buffer

            # Execute code
            exec(code, exec_globals)

            # Restore stdout/stderr
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            return {
                "result": exec_globals.get("result", None),
                "output": stdout_buffer.getvalue(),
                "error": stderr_buffer.getvalue()
            }
        except Exception as e:
            return {
                "result": None,
                "output": stdout_buffer.getvalue(),
                "error": str(e)
            }
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

def full_setup():
    # Start the local server
    url = start_server()

    # Create the web view window
    api = Api()
    window = webview.create_window(
        "ROON",
        url,
        js_api=api,  # Expose Python functions to JS
        width=800,
        height=600,
        # frameless=True,
        transparent=True,
        # background_color='#00000000'
        vibrancy=True
    )

      # Inject JS to set a custom flag when the page loads
    window.events.loaded += lambda: window.evaluate_js("""
      window.is_pywebview = true; // Custom flag
      console.log("PyWebView flag set");
    """)

    webview.start(debug=True)

if __name__ == "__main__":
    full_setup()