import json
import inspect
import importlib
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

def analyze_installed_module_functions(module_name, output_dir=""):
    """
    Analyzes functions in an installed Python module and generates JSON representations.
    
    Args:
        module_name (str): Name of the installed module (e.g., "numpy", "matplotlib.pyplot").
        output_dir (str): Directory where JSON files will be saved (default: current directory).
                          If None, returns JSON strings instead.
    
    Returns:
        dict: Mapping of function names to their JSON file paths (if output_dir is provided) or JSON strings.
    """
    # Dynamically import the module
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise ValueError(f"Failed to import module '{module_name}': {e}")

    # Get all functions (Python functions only)
    functions = [(name, obj) for name, obj in inspect.getmembers(module, inspect.isfunction)]

    result = {}
    for func_name, func in functions:
        # Get function signature and type hints
        try:
            signature = inspect.signature(func)
        except ValueError:
            # Some built-in/C functions don't have signatures
            signature = inspect.Signature()
        
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
        
        # Get the raw source code if available
        try:
            source_code = inspect.getsource(func).strip()
        except (OSError, TypeError) as e:
            source_code = f"Source code unavailable: {str(e)} (likely implemented in C)"

        # Create JSON structure
        function_json = {
            "name": func_name,
            "inputs": inputs,
            "outputs": outputs,
            "docstring": inspect.getdoc(func) or "",
            "source": source_code,
            "module": module_name
        }
        
        # Save JSON to file or return as string
        if output_dir is None:
            result[func_name] = json.dumps(function_json, indent=4)
        else:
            output_file = f"{output_dir}{func_name}.json"
            with open(output_file, 'w') as f:
                json.dump(function_json, f, indent=4)
            result[func_name] = output_file
    
    return result



# Example usage
if __name__ == "__main__":
    # Analyze numpy
    numpy_results = analyze_installed_module_functions("numpy", output_dir=None)
    for func_name, file_path in numpy_results.items():
        print(f"Generated JSON for {func_name} at {file_path}")

    # Analyze matplotlib.pyplot
    # plt_results = analyze_installed_module_functions("matplotlib.pyplot", output_dir=None)
    # for func_name, json_str in plt_results.items():
    #     print(f"JSON for {func_name}:\n{json_str}")