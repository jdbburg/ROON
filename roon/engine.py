import json
from collections import defaultdict, deque

def module_import_star(module_path):
    return f"import {module_path}"

def normalize_module_path(module_path):
    if module_path.endswith(".py"):
        module_path = module_path[:-3]
    if module_path.startswith("./"):
        module_path = module_path[2:]
    return module_path.replace("/", ".")

def generate_python_script(json_data):
    nodes = json_data['nodes']
    connections = json_data['connections']
    node_dict = {node['id']: node for node in nodes}

    # Build dependency graph for topological sort
    adj_list = defaultdict(list)
    incoming_degree = {node['id']: 0 for node in nodes}
    for conn in connections:
        from_node = conn['from']['node']
        to_node = conn['to']['node']
        adj_list[from_node].append(to_node)
        incoming_degree[to_node] += 1

    # Topological sort
    queue = deque([nid for nid in incoming_degree if incoming_degree[nid] == 0])
    order = []
    while queue:
        node_id = queue.popleft()
        order.append(node_id)
        for neighbor in adj_list[node_id]:
            incoming_degree[neighbor] -= 1
            if incoming_degree[neighbor] == 0:
                queue.append(neighbor)
    if len(order) != len(nodes):
        raise ValueError("Cycle detected in the node graph")

    # Map connections: (to_node, input_name) → (from_node, output_name)
    connections_map = {
        (conn['to']['node'], conn['to']['input']): (conn['from']['node'], conn['from']['output'])
        for conn in connections
    }

    # Extract function definitions and module dependencies
    dependency_modules = set()
    function_defs = []
    for node in nodes:
        if 'module' in node:
            dependency_modules.add(normalize_module_path(node['module']))
            continue
        if 'source' not in node:
            continue
        function_defs.append(node['source'])

    # Generate execution lines
    execution_lines = []
    for node_id in order:
        node = node_dict[node_id]
        func_name = node['name']
        if 'module' in node:
            func_name = f"{normalize_module_path(node['module'])}.{func_name}"

        # Collect arguments
        args = []
        for input_spec in node['inputs']:
            input_name = input_spec['name']
            if (node_id, input_name) in connections_map:
                from_node, output_name = connections_map[(node_id, input_name)]
                if len(node_dict[from_node]['outputs']) == 1:
                    args.append(f"node_{from_node}_{output_name}")
                else:
                    args.append(f"node_{from_node}_result['{output_name}']")
            elif input_spec['default'] is not None:
                default_value = repr(input_spec['default'])
                args.append(default_value)
            else:
                raise ValueError(f"Missing required input '{input_name}' for node {node_id}")
        arg_str = ', '.join(args)
        call = f"{func_name}({arg_str})"

        # Assign return values based on output count
        if node['outputs']:
            if len(node['outputs']) == 1:
                output_name = node['outputs'][0]['name']
                output_var = f"node_{node_id}_{output_name}"
                execution_lines.append(f"{output_var} = {call}")
            else:
                output_var = f"node_{node_id}_result"
                execution_lines.append(f"{output_var} = {call}")
        else:
            execution_lines.append(call)

    # Assemble the script
    module_import_star_lines = [module_import_star(module) for module in dependency_modules]
    script = (
        "import sys\n\nsys.path.append('/Users/brandenburg.89/Development/rune/svelte/svelte-node-graph/nodes/')\n\n" +
        "\n\n".join(module_import_star_lines) + "\n\n" +
        "\n\n".join(function_defs) + "\n\n" +
        "\n".join(execution_lines)
    )
    return script