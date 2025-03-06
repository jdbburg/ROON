import json
import inspect
import importlib.util
import sys
from typing import TypedDict, get_type_hints, Tuple, Dict, get_origin, get_args

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

def analyze_function_to_json(module_path, function_name, output_file):
    spec = importlib.util.spec_from_file_location("module_to_analyze", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module_to_analyze"] = module
    spec.loader.exec_module(module)
    
    func = getattr(module, function_name)
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)
    
    inputs = []
    for param_name, param in signature.parameters.items():
        param_info = {
            "name": param_name,
            "type": format_type(type_hints.get(param_name)),
            "default": str(param.default) if param.default != inspect.Parameter.empty else None,
            "kind": str(param.kind)
        }
        inputs.append(param_info)
    
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
    
    function_json = {
        "name": function_name,
        "inputs": inputs,
        "outputs": outputs,
        "docstring": inspect.getdoc(func) or ""
    }
    
    with open(output_file, 'w') as f:
        json.dump(function_json, f, indent=4)
    
    return f"JSON representation saved to {output_file}"

if __name__ == "__main__":
    try:
        result = analyze_function_to_json(
            "example_functions.py",
            "open_root_file",
            "function_output.json"
        )
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")