import json
import inspect
import importlib.util
import sys
from typing import TypedDict, get_type_hints, Tuple, Dict, get_origin, get_args
import argparse

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

def analyze_module_functions(module_path, output_dir="", base_path=None):
    """
    Analyzes all functions in a module and generates JSON representations including source code.
    
    Args:
        module_path (str): Path to the Python file containing the module
        output_dir (str): Directory where JSON files will be saved (default: current dir)
    
    Returns:
        dict: Mapping of function names to their JSON file paths
    """
    # Load the module dynamically
    spec = importlib.util.spec_from_file_location("module_to_analyze", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module_to_analyze"] = module
    spec.loader.exec_module(module)

    # normalize the module path by removing the base_path if it is not None
    if base_path is not None:
        module_path = module_path.replace(base_path, '')
    
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
                outputs.append({
                    "name": field_name,
                    "type": format_type(field_type)
                })
        elif get_origin(return_type) in (tuple, Tuple):
            outputs.append({
                "name": "return_value",
                "type": format_type(return_type)
            })
        elif get_origin(return_type) in (dict, Dict):
            outputs.append({
                "name": "return_value",
                "type": format_type(return_type)
            })
        elif get_origin(return_type) == list:
            outputs.append({
                "name": "return_value",
                "type": format_type(return_type)
            })
        else:
            outputs.append({
                "name": "return_value",
                "type": format_type(return_type)
            })
        
        # Get the raw source code
        try:
            source_code = inspect.getsource(func).strip()
        except (OSError, TypeError) as e:
            source_code = f"Source code unavailable: {str(e)}"

        # Create JSON structure
        function_json = {
            "name": func_name,
            "inputs": inputs,
            "outputs": outputs,
            "docstring": inspect.getdoc(func) or "",
            "source": source_code,
            "module": module_path
        }
        
        if output_dir == None:
            result[func_name] = json.dumps(function_json, indent=4)
            continue

        # Write to JSON file
        output_file = f"{output_dir}{func_name}.json"
        with open(output_file, 'w') as f:
            json.dump(function_json, f, indent=4)
        
        result[func_name] = output_file
    
    return result

# Example usage
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Convert python functions to node definitions")
        # add argument for specifying the python file to analyze
        parser.add_argument('file', help='Generate node defs from .py file')
        args = parser.parse_args()
        if not args.file.endswith('.py'):
            raise ValueError("Input file must be a Python file")
        module_path = args.file
        results = analyze_module_functions(module_path)
        for func_name, file_path in results.items():
            print(f"Generated JSON for {func_name} at {file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")