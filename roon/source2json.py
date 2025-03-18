import json
import inspect
import sys
import ast
import textwrap
import types
from typing import get_type_hints, Tuple, Dict, get_origin, get_args

def format_type(type_obj):
    """Convert type objects to clean string representations."""
    if type_obj is None or type_obj == inspect._empty:
        return "any"
    if type_obj in (int, float, str, bool, list):
        return type_obj.__name__
    origin = get_origin(type_obj)
    if origin:
        args = get_args(type_obj)
        if origin in (tuple, Tuple):
            return f"tuple[{', '.join(format_type(arg) for arg in args)}]"
        elif origin in (dict, Dict):
            return f"dict[{format_type(args[0])}, {format_type(args[1])}]"
        elif origin == list:
            return f"list[{format_type(args[0])}]"
    return str(type_obj).replace("<class '", "").replace("'>", "")

def analyze_source_code_functions(source_code, output_dir="", module_name="<string>"):
    """
    Analyzes functions in a Python source code string and generates JSON representations.
    
    Args:
        source_code (str): String containing Python source code
        output_dir (str): Directory where JSON files will be saved (default: current dir)
        module_name (str): Identifier for the source code in JSON output (default: "<string>")
    
    Returns:
        dict: Mapping of function names to their JSON file paths or JSON strings
    """
    # Parse the source code into an AST
    tree = ast.parse(source_code)
    lines = source_code.splitlines()

    # Extract source code for top-level functions
    function_sources = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            # Determine start line (including decorators)
            start_line = (min(decorator.lineno for decorator in node.decorator_list)
                          if node.decorator_list else node.lineno)
            end_line = node.end_lineno
            # Extract and dedent source code
            source_lines = lines[start_line - 1:end_line]
            func_source = '\n'.join(source_lines)
            func_source = textwrap.dedent(func_source)
            function_sources[node.name] = func_source

    # Create a new module and execute the source code
    module = types.ModuleType("module_to_analyze")
    exec(source_code, module.__dict__)

    # Get all functions
    functions = [(name, obj) for name, obj in inspect.getmembers(module, inspect.isfunction)]

    result = {}
    for func_name, func in functions:
        # Get function signature and type hints
        signature = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # Analyze parameters
        inputs = []
        for param_name, param in signature.parameters.items():
            param_info = {
                "name": param_name,
                "type": format_type(type_hints.get(param_name)),
                "default": str(param.default) if param.default != inspect.Parameter.empty else None,
                "kind": str(param.kind)
            }
            inputs.append(param_info)
        
        # Analyze return value
        return_type = type_hints.get('return', 'any')
        outputs = []
        if isinstance(return_type, type) and issubclass(return_type, dict) and hasattr(return_type, '__annotations__'):
            for field_name, field_type in return_type.__annotations__.items():
                outputs.append({"name": field_name, "type": format_type(field_type)})
        elif get_origin(return_type) in (tuple, Tuple):
            outputs.append({"name": "return_value", "type": format_type(return_type)})
        elif get_origin(return_type) in (dict, Dict):
            outputs.append({"name": "return_value", "type": format_type(return_type)})
        elif get_origin(return_type) == list:
            outputs.append({"name": "return_value", "type": format_type(return_type)})
        else:
            outputs.append({"name": "return_value", "type": format_type(return_type)})
        
        # Get source code from the dictionary
        source_code = function_sources.get(func_name, "Source code unavailable")

        # Create JSON structure
        function_json = {
            "name": func_name,
            "inputs": inputs,
            "outputs": outputs,
            "docstring": inspect.getdoc(func) or "",
            "source": source_code,
            "module": module_name
        }
        
        # Handle output based on output_dir
        if output_dir == None:
            result[func_name] = json.dumps(function_json, indent=4)
            continue

        output_file = f"{output_dir}{func_name}.json"
        with open(output_file, 'w') as f:
            json.dump(function_json, f, indent=4)
        result[func_name] = output_file
    
    return result