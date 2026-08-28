"""
Analysis Statistics Service
Computes analysis statistics from parsed files and resolved edges.
"""
from typing import Dict, Any, List


def compute_statistics(
    parsed_files: List[Dict[str, Any]],
    resolved_edges: List[Dict[str, Any]],
    analysis_duration: float = 0.0
) -> Dict[str, Any]:
    """
    Computes comprehensive analysis statistics.

    Args:
        parsed_files: List of parsed file results from code_parser.
        resolved_edges: List of resolved edge dicts from the graph builder.
        analysis_duration: Wall-clock seconds for the entire analysis.

    Returns:
        A dictionary of analysis statistics.
    """
    total_files = 0
    total_classes = 0
    total_functions = 0
    total_imports = 0
    error_files = 0

    for f in parsed_files:
        if "error" in f:
            error_files += 1
            continue
        total_files += 1
        total_classes += len(f.get("classes", []))
        total_functions += len(f.get("functions", []))
        total_imports += len(f.get("imports", []))

    # Edge classification counts
    verified_count = 0
    external_count = 0
    unresolved_count = 0
    ambiguous_count = 0

    for edge in resolved_edges:
        status = edge.get("resolution_status", "UNKNOWN")
        if status == "VERIFIED":
            verified_count += 1
        elif status == "EXTERNAL":
            external_count += 1
        elif status == "UNRESOLVED":
            unresolved_count += 1
        elif status == "AMBIGUOUS":
            ambiguous_count += 1

    total_relationships = len(resolved_edges)

    return {
        "total_python_files": total_files,
        "error_files": error_files,
        "total_classes": total_classes,
        "total_functions": total_functions,
        "total_imports": total_imports,
        "total_relationships": total_relationships,
        "verified_count": verified_count,
        "external_count": external_count,
        "unresolved_count": unresolved_count,
        "ambiguous_count": ambiguous_count,
        "analysis_duration_seconds": round(analysis_duration, 2)
    }
