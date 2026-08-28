from typing import Dict, Any, List, Tuple

class GraphValidationError(Exception):
    """Raised when a graph fails static structural integrity validation."""
    pass

def validate_graph(graph_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates a graph data structure to guarantee structural integrity:
    1. No duplicate node IDs.
    2. Every edge's source and target reference valid nodes in the node set.
    3. Every VERIFIED edge carries non-empty evidence (file, line).
    4. Every VERIFIED edge target actually exists in the node set.
    Returns (is_valid, list_of_error_messages).
    """
    errors = []
    nodes = graph_data.get("nodes", [])
    links = graph_data.get("links", [])

    # Check 1: No duplicate node IDs
    node_ids = set()
    for idx, node in enumerate(nodes):
        nid = node.get("id")
        if not nid:
            errors.append(f"Node at index {idx} missing 'id' field.")
            continue
        if nid in node_ids:
            errors.append(f"Duplicate node ID detected: '{nid}'")
        node_ids.add(nid)

    # Check 2, 3, 4: Edge integrity and evidence
    for idx, link in enumerate(links):
        src = link.get("source")
        tgt = link.get("target")
        rel_status = link.get("resolution_status")
        evidence = link.get("evidence", {})

        if not src or src not in node_ids:
            errors.append(f"Edge index {idx} ({link.get('id')}) references unknown source node '{src}'")

        if not tgt or tgt not in node_ids:
            errors.append(f"Edge index {idx} ({link.get('id')}) references unknown target node '{tgt}'")

        if rel_status == "VERIFIED":
            # Check 3: Non-empty evidence
            if not isinstance(evidence, dict) or not evidence.get("file") or not evidence.get("line"):
                errors.append(
                    f"VERIFIED edge '{link.get('id')}' ({src} -> {tgt}) is missing required evidence (file and line)."
                )

            # Check 4: VERIFIED target exists in node set
            if tgt not in node_ids:
                errors.append(
                    f"VERIFIED edge '{link.get('id')}' references target node '{tgt}' which is missing from node set."
                )

    is_valid = len(errors) == 0
    return is_valid, errors
