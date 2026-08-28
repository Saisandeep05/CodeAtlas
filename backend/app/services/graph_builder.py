import networkx as nx
from typing import Dict, Any, List
from app.services.symbol_index import SymbolIndex
from app.services.symbol_resolver import SymbolResolver, get_canonical_node_id
from app.services.graph_validator import validate_graph, GraphValidationError

def build_graph(parsed_files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Builds a NetworkX DiGraph using the SymbolIndex and SymbolResolver pipeline,
    then exports rich nodes and evidence-backed edges to JSON.
    Runs an internal validation pass ensuring no duplicate node IDs, valid source/target endpoints,
    non-empty evidence for VERIFIED edges, and valid target node existence.
    """
    index = SymbolIndex(parsed_files)
    resolver = SymbolResolver(index)
    resolved_edges = resolver.resolve_relationships(parsed_files)

    G = nx.DiGraph()

    # Add explicit nodes from parsed files
    for f in parsed_files:
        if "error" in f:
            continue

        file_path = f["file"]
        file_id = get_canonical_node_id("FILE", file_path, "")
        G.add_node(file_id, id=file_id, name=file_path, type="FILE", group=1, file=file_path)

        for cls in f.get("classes", []):
            cls_id = get_canonical_node_id("CLASS", file_path, cls["name"])
            G.add_node(cls_id, id=cls_id, name=cls["name"], type="CLASS", module=cls["module"], file=file_path, group=2)

        for func in f.get("functions", []):
            if func.get("parent_class"):
                func_name = f"{func['parent_class']}.{func['name']}"
                func_id = get_canonical_node_id("METHOD", file_path, func_name)
                G.add_node(func_id, id=func_id, name=func_name, type="METHOD", file=file_path, group=3)
            else:
                func_id = get_canonical_node_id("FUNCTION", file_path, func["name"])
                G.add_node(func_id, id=func_id, name=func["name"], type="FUNCTION", file=file_path, group=3)

    # Add edges and placeholder nodes for external/unresolved/ambiguous symbols
    for edge in resolved_edges:
        src = edge["source"]
        tgt = edge["target"]

        if not G.has_node(src):
            G.add_node(src, id=src, name=src.split(":")[-1], type="UNKNOWN", group=6)

        if not G.has_node(tgt):
            group_type = "EXTERNAL" if "external" in tgt or "module" in tgt else ("UNRESOLVED" if "unresolved" in tgt else "AMBIGUOUS")
            G.add_node(tgt, id=tgt, name=tgt.split(":")[-1], type=group_type, group=5)

        G.add_edge(src, tgt, **edge)

    # Export Full Nodes
    nodes = []
    for node_id, attrs in G.nodes(data=True):
        nodes.append({
            "id": node_id,
            "name": attrs.get("name", node_id),
            "type": attrs.get("type", "UNKNOWN"),
            "group": attrs.get("group", 1),
            "file": attrs.get("file", None),
            "module": attrs.get("module", None)
        })

    edges = []
    for idx, (source, target, attrs) in enumerate(G.edges(data=True)):
        edges.append({
            "id": f"edge_{idx}",
            "source": source,
            "target": target,
            "type": attrs.get("type", "RELATES_TO"),
            "resolution_status": attrs.get("resolution_status", "UNKNOWN"),
            "reasoning": attrs.get("reasoning", ""),
            "evidence": attrs.get("evidence", {})
        })

    result_graph = {
        "nodes": nodes,
        "links": edges
    }

    # Run Validation Pass
    is_valid, validation_errors = validate_graph(result_graph)
    if not is_valid:
        raise GraphValidationError(f"Graph validation failed: {'; '.join(validation_errors)}")

    return result_graph

def project_graph_mode(graph_data: Dict[str, Any], mode: str) -> Dict[str, Any]:
    if mode == "FULL":
        return graph_data

    nodes = graph_data.get("nodes", [])
    links = graph_data.get("links", [])

    if mode == "FILES":
        file_nodes = [n for n in nodes if n["type"] in ["FILE", "EXTERNAL", "UNRESOLVED", "AMBIGUOUS"]]
        node_map = {n["id"]: n for n in file_nodes}

        symbol_to_file = {}
        for n in nodes:
            if n["type"] == "FILE":
                symbol_to_file[n["id"]] = n["id"]
            elif n.get("file"):
                symbol_to_file[n["id"]] = f"file:{n['file']}"
            else:
                symbol_to_file[n["id"]] = n["id"]

        file_links_map = {}

        for l in links:
            src_file = symbol_to_file.get(l["source"], l["source"])
            tgt_file = symbol_to_file.get(l["target"], l["target"])

            if src_file == tgt_file:
                continue

            pair = (src_file, tgt_file)
            if pair not in file_links_map:
                file_links_map[pair] = {
                    "source": src_file,
                    "target": tgt_file,
                    "type": l["type"],
                    "resolution_status": l["resolution_status"],
                    "reasoning": l.get("reasoning", ""),
                    "relationship_count": 0,
                    "edge_types": set(),
                    "verified_count": 0,
                    "evidence": l.get("evidence", {})
                }

            agg = file_links_map[pair]
            agg["relationship_count"] += 1
            agg["edge_types"].add(l["type"])
            if l.get("resolution_status") == "VERIFIED":
                agg["verified_count"] += 1

        projected_links = []
        for idx, ((src, tgt), agg) in enumerate(file_links_map.items()):
            projected_links.append({
                "id": f"file_edge_{idx}",
                "source": src,
                "target": tgt,
                "type": "/".join(sorted(agg["edge_types"])),
                "resolution_status": "VERIFIED" if agg["verified_count"] > 0 else agg["resolution_status"],
                "reasoning": agg["reasoning"],
                "relationship_count": agg["relationship_count"],
                "verified_count": agg["verified_count"],
                "evidence": agg["evidence"]
            })

        active_node_ids = {n["id"] for n in file_nodes}
        for l in projected_links:
            if l["source"] not in active_node_ids:
                file_nodes.append({"id": l["source"], "name": l["source"].split(":")[-1], "type": "FILE"})
                active_node_ids.add(l["source"])
            if l["target"] not in active_node_ids:
                file_nodes.append({"id": l["target"], "name": l["target"].split(":")[-1], "type": "EXTERNAL"})
                active_node_ids.add(l["target"])

        return {"nodes": file_nodes, "links": projected_links}

    elif mode == "CLASSES":
        allowed = ["FILE", "CLASS", "EXTERNAL", "UNRESOLVED", "AMBIGUOUS"]
        valid_ids = {n["id"] for n in nodes if n["type"] in allowed}
        filtered_nodes = [n for n in nodes if n["id"] in valid_ids]
        filtered_links = [l for l in links if l["source"] in valid_ids and l["target"] in valid_ids]
        return {"nodes": filtered_nodes, "links": filtered_links}

    elif mode == "FUNCTIONS":
        allowed = ["FILE", "FUNCTION", "METHOD", "EXTERNAL", "UNRESOLVED", "AMBIGUOUS"]
        valid_ids = {n["id"] for n in nodes if n["type"] in allowed}
        filtered_nodes = [n for n in nodes if n["id"] in valid_ids]
        filtered_links = [l for l in links if l["source"] in valid_ids and l["target"] in valid_ids]
        return {"nodes": filtered_nodes, "links": filtered_links}

    return graph_data
