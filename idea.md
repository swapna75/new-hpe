# Root Cause Detection using Backtracking

## Objective
Identify whether a raised alert corresponds to a root cause by recursively checking upstream dependencies using backtracking.

## Description
In a service dependency graph, an alert at a node may result from failures in its parent nodes. We recursively traverse the graph from the alert node and backtrack to find the actual root that has no alerted parents.

## Algorithm
1. Input: Alerted node ID
2. Track visited nodes to avoid cycles
3. For the current node:
   - If it has no parents or all parents are healthy → it's possibly the root
   - Else, recursively check its parents
4. Return the topmost node in the alert chain with no alerted parents

## Pseudocode
```python
def is_root_cause(node, graph, alerted, visited):
    if node.id in visited:
        return None
    visited.add(node.id)

    if node.id not in alerted:
        return None

    for parent in node.parents:
        result = is_root_cause(parent, graph, alerted, visited)
        if result:
            return result

    return node.id
