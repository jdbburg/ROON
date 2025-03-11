import json
from collections import defaultdict, deque
import uproot  # Required for some source code examples
from example_functions import *
import argparse
import textwrap

# Predefine functions for nodes without source
def add_numbers(a=5, b=3):
    return a + b

def print_result(value):
    print(value)

# Map of predefined functions
functions = {
    "1": add_numbers,
    "2": print_result
}

def evaluate_dag(data, generate_code=False):
    # Build adjacency list and incoming degree for topological sort
    adj_list = defaultdict(list)
    incoming_degree = defaultdict(int)
    connections_map = defaultdict(dict)

    # For code generation
    function_defs = []
    execution_lines = []
    seen_functions = set()  # Track defined functions to avoid duplicates

    # Process connections
    for conn in data["connections"]:
        from_node = conn["from"]["node"]
        to_node = conn["to"]["node"]
        to_input = conn["to"]["input"]
        output_name = conn["from"]["output"]

        if to_input != "source":
            adj_list[from_node].append(to_node)
            incoming_degree[to_node] += 1
        connections_map[to_node][to_input] = (from_node, output_name)

    # Initialize queue with nodes that have no dependencies
    queue = deque([n["id"] for n in data["nodes"] if incoming_degree[n["id"]] == 0])
    outputs = {}

    while queue:
        node_id = queue.popleft()
        node = next(n for n in data["nodes"] if n["id"] == node_id)

        # Collect inputs
        inputs_dict = {}
        for input_spec in node.get("inputs", []):
            input_name = input_spec["name"]
            if input_name == "source":
                continue
            if node_id in connections_map and input_name in connections_map[node_id]:
                pred_node, output_name = connections_map[node_id][input_name]
                value = outputs[pred_node][output_name]
                inputs_dict[input_name] = value
            else:
                value = input_spec.get("default")
                inputs_dict[input_name] = value

        # Determine the source code
        if "source" in node:
            source_code = node["source"]
        elif node_id in connections_map and "source" in connections_map[node_id]:
            pred_node, output_name = connections_map[node_id]["source"]
            source_code = outputs[pred_node][output_name]
        else:
            source_code = None

        # Define and get the function
        if source_code:
            local_ns = {}
            if not generate_code:
                exec(source_code, globals(), local_ns)
                function = local_ns[node["name"]]
            # For code generation
            indented_code = textwrap.indent(source_code, '    ')
            func_def = f"def {node['name']}({', '.join(inputs_dict.keys())}):\n{indented_code}"
            if node['name'] not in seen_functions:
                function_defs.append(func_def)
                seen_functions.add(node['name'])
        else:
            function = functions[node_id]
            # For code generation, assume function is predefined elsewhere
            if node_id not in seen_functions:
                function_defs.append(f"# Predefined function: {function.__name__}")
                seen_functions.add(node_id)

        # Execute or generate execution line
        if not generate_code:
            try:
                result = function(**inputs_dict)
            except Exception as e:
                print(f"Error evaluating node {node_id} ({node['name']}): {e}")
                result = None
        else:
            # Generate variable names for outputs
            if node["outputs"]:
                output_names = [f"output_{node_id}_{out['name']}" for out in node["outputs"]]
                call = f"{', '.join(output_names)} = {node['name']}({', '.join(f'{k}={repr(v)}' for k, v in inputs_dict.items())})"
            else:
                call = f"{node['name']}({', '.join(f'{k}={repr(v)}' for k, v in inputs_dict.items())})"
            execution_lines.append(call)

        # Store outputs (only if not generating code)
        if not generate_code:
            if not node["outputs"]:
                outputs[node_id] = {}
            elif len(node["outputs"]) == 1:
                output_name = node["outputs"][0]["name"]
                outputs[node_id] = {output_name: result}
            else:
                outputs[node_id] = result  # Assume result is a dict

        # Update dependencies
        for neighbor in adj_list[node_id]:
            incoming_degree[neighbor] -= 1
            if incoming_degree[neighbor] == 0:
                queue.append(neighbor)

    # Generate .py file if requested
    if generate_code:
        script = "import uproot\n\n" + "\n\n".join(function_defs) + "\n\nif __name__ == '__main__':\n" + "\n".join(
            f"    {line}" for line in execution_lines
        )
        with open('generated.py', 'w') as f:
            f.write(script)
        return None  # Don't return outputs when generating code

    return outputs

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Evaluate a DAG or generate executable code.")
parser.add_argument('--generate-code', action='store_true', help='Generate a .py file instead of executing')
args = parser.parse_args()

# Example usage
with open("graph.json") as f:
    data = json.load(f)

# Execute or generate code based on argument
outputs = evaluate_dag(data, generate_code=args.generate_code)
if not args.generate_code:
    print(outputs)