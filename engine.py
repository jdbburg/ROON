import json
from collections import defaultdict, deque
import uproot  # Required for some source code examples
from example_functions import *

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

def evaluate_dag(data):
    # Build adjacency list and incoming degree for topological sort
    adj_list = defaultdict(list)
    incoming_degree = defaultdict(int)
    connections_map = defaultdict(dict)

    # Process connections
    for conn in data["connections"]:
        from_node = conn["from"]["node"]
        to_node = conn["to"]["node"]
        to_input = conn["to"]["input"]
        output_name = conn["from"]["output"]

        # If the connection is to an input (not source), it's a dependency
        if to_input != "source":
            adj_list[from_node].append(to_node)
            incoming_degree[to_node] += 1
        # Map connections for inputs and source
        connections_map[to_node][to_input] = (from_node, output_name)

    # Initialize queue with nodes that have no dependencies
    queue = deque([n["id"] for n in data["nodes"] if incoming_degree[n["id"]] == 0])
    outputs = {}

    while queue:
        node_id = queue.popleft()
        node = next(n for n in data["nodes"] if n["id"] == node_id)

        # Collect inputs (excluding 'source' as an input)
        inputs_dict = {}
        for input_spec in node.get("inputs", []):
            input_name = input_spec["name"]
            if input_name == "source":
                continue  # 'source' is handled separately
            if node_id in connections_map and input_name in connections_map[node_id]:
                pred_node, output_name = connections_map[node_id][input_name]
                value = outputs[pred_node][output_name]
            else:
                value = input_spec.get("default")
            inputs_dict[input_name] = value

        # Determine the source code
        if "source" in node:
            source_code = node["source"]  # Static source
        elif node_id in connections_map and "source" in connections_map[node_id]:
            # Dynamic source from another node's output
            pred_node, output_name = connections_map[node_id]["source"]
            source_code = outputs[pred_node][output_name]
        else:
            source_code = None

        # Define and get the function
        if source_code:
            # Execute source code in a local namespace during evaluation
            local_ns = {}
            exec(source_code, globals(), local_ns)
            function = local_ns[node["name"]]
        else:
            # Use predefined function if no source is provided
            function = functions[node_id]

        # Execute the function
        try:
            result = function(**inputs_dict)
        except Exception as e:
            print(f"Error evaluating node {node_id} ({node['name']}): {e}")
            result = None

        # Store outputs
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

    return outputs

# Example usage
with open("graph.json") as f:
    data = json.load(f)

# Ensure required modules are imported
outputs = evaluate_dag(data)
print(outputs)