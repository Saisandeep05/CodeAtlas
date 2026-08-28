import networkx as nx
import re
from typing import Dict, Any, List, Optional

class GraphQueryService:
    def __init__(self, graph_data: Dict[str, Any]):
        self.graph_data = graph_data
        self.G = nx.DiGraph()

        for node in graph_data.get("nodes", []):
            self.G.add_node(node["id"], **node)

        for link in graph_data.get("links", []):
            self.G.add_edge(link["source"], link["target"], **link)

    def is_structural_question(self, question: str) -> bool:
        q = question.lower()
        structural_keywords = ["depend", "import", "call", "called by", "inherit", "use", "calls", "imports", "inherits", "dependencies", "callers", "path"]
        open_ended_keywords = ["explain", "why", "describe", "purpose", "how does", "how do"]

        for kw in open_ended_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', q):
                return False

        for kw in structural_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', q):
                return True

        return False

    def query_structural(self, node_id: str, question: str) -> Dict[str, Any]:
        if not self.G.has_node(node_id):
            return {
                "answer": f"Node '{node_id}' not found in architecture graph.",
                "response_source": "GRAPH",
                "verification_level": "VERIFIED_GRAPH_QUERY"
            }

        node_data = self.G.nodes[node_id]
        node_name = node_data.get("name", node_id)
        q = question.lower()

        if "who calls" in q or "called by" in q or "callers" in q:
            callers = self.get_callers(node_id, transitive="transitive" in q)
            if callers["nodes"]:
                lines = [f"**Verified Callers of {node_name}:**"]
                for c in callers["nodes"]:
                    if c["id"] != node_id:
                        lines.append(f"- {c['name']} ({c['type']})")
                answer_text = "\n".join(lines)
            else:
                answer_text = f"No callers found for **{node_name}** in static graph."

        elif "import" in q or "depend" in q or "calls" in q or "call" in q:
            deps = self.get_dependencies(node_id, transitive="transitive" in q)
            if deps["nodes"]:
                lines = [f"**Verified Dependencies for {node_name}:**"]
                for d in deps["nodes"]:
                    if d["id"] != node_id:
                        lines.append(f"- {d['name']} ({d['type']})")
                answer_text = "\n".join(lines)
            else:
                answer_text = f"No dependencies found for **{node_name}** in static graph."

        else:
            out_edges = self.G.out_edges(node_id, data=True)
            in_edges = self.G.in_edges(node_id, data=True)

            result = [f"**Structural Graph Facts for {node_name}:**"]
            for u, v, data in out_edges:
                target_name = self.G.nodes[v].get("name", v)
                status = data.get("resolution_status", "VERIFIED")
                reasoning = data.get("reasoning", "")
                reason_str = f" - {reasoning}" if reasoning else ""
                result.append(f"- → {data.get('type')} {target_name} ({status}){reason_str}")

            for u, v, data in in_edges:
                source_name = self.G.nodes[u].get("name", u)
                status = data.get("resolution_status", "VERIFIED")
                reasoning = data.get("reasoning", "")
                reason_str = f" - {reasoning}" if reasoning else ""
                result.append(f"- ← {data.get('type')} by {source_name} ({status}){reason_str}")

            answer_text = "\n".join(result)

        return {
            "answer": answer_text,
            "response_source": "GRAPH",
            "verification_level": "VERIFIED_GRAPH_QUERY"
        }

    def get_node_summary(self, node_id: str) -> Optional[Dict[str, Any]]:
        if not self.G.has_node(node_id):
            return None

        attrs = self.G.nodes[node_id]
        deps = self.get_dependencies(node_id, transitive=False)
        callers = self.get_callers(node_id, transitive=False)

        return {
            "node": {
                "id": node_id,
                "name": attrs.get("name", node_id),
                "type": attrs.get("type", "UNKNOWN"),
                "group": attrs.get("group", 1),
                "file": attrs.get("file"),
                "module": attrs.get("module")
            },
            "incoming_count": len(self.G.in_edges(node_id)),
            "outgoing_count": len(self.G.out_edges(node_id)),
            "dependencies": deps["nodes"],
            "callers": callers["nodes"]
        }

    def get_edge_evidence(self, edge_id: str) -> Optional[Dict[str, Any]]:
        for u, v, attrs in self.G.edges(data=True):
            if attrs.get("id") == edge_id:
                return {
                    "id": edge_id,
                    "source": u,
                    "target": v,
                    "type": attrs.get("type"),
                    "resolution_status": attrs.get("resolution_status"),
                    "reasoning": attrs.get("reasoning", ""),
                    "evidence": attrs.get("evidence", {})
                }
        return None

    def get_neighborhood(self, node_id: str, depth: int = 1) -> Dict[str, Any]:
        return self.get_subgraph(node_id, depth=depth)

    def get_subgraph(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        if not self.G.has_node(node_id):
            return {"nodes": [], "links": []}

        undirected = self.G.to_undirected()
        lengths = nx.single_source_shortest_path_length(undirected, node_id, cutoff=depth)
        subgraph_nodes = set(lengths.keys())

        sub_g = self.G.subgraph(subgraph_nodes)

        nodes = []
        for n_id, attrs in sub_g.nodes(data=True):
            nodes.append({
                "id": n_id,
                "name": attrs.get("name", n_id),
                "type": attrs.get("type", "UNKNOWN"),
                "group": attrs.get("group", 1),
                "file": attrs.get("file", None),
                "module": attrs.get("module", None)
            })

        links = []
        for idx, (u, v, attrs) in enumerate(sub_g.edges(data=True)):
            links.append({
                "id": attrs.get("id", f"sub_edge_{idx}"),
                "source": u,
                "target": v,
                "type": attrs.get("type", "RELATES_TO"),
                "resolution_status": attrs.get("resolution_status", "UNKNOWN"),
                "reasoning": attrs.get("reasoning", ""),
                "evidence": attrs.get("evidence", {})
            })

        return {"nodes": nodes, "links": links}

    def find_path(self, source_id: str, target_id: str) -> Optional[Dict[str, Any]]:
        node_path = self.get_shortest_path(source_id, target_id)
        if not node_path or len(node_path) < 2:
            return None

        path_nodes = []
        for n_id in node_path:
            attrs = self.G.nodes[n_id] if self.G.has_node(n_id) else {}
            path_nodes.append({
                "id": n_id,
                "name": attrs.get("name", n_id),
                "type": attrs.get("type", "UNKNOWN")
            })

        path_edges = []
        for i in range(len(node_path) - 1):
            u = node_path[i]
            v = node_path[i + 1]
            edge_data = self.G.get_edge_data(u, v)
            if not edge_data:
                edge_data = self.G.get_edge_data(v, u) or {}

            path_edges.append({
                "source": u,
                "target": v,
                "type": edge_data.get("type", "RELATES_TO"),
                "resolution_status": edge_data.get("resolution_status", "UNKNOWN"),
                "reasoning": edge_data.get("reasoning", ""),
                "evidence": edge_data.get("evidence", {})
            })

        return {
            "source": source_id,
            "target": target_id,
            "path": node_path,
            "nodes": path_nodes,
            "edges": path_edges,
            "hop_count": len(node_path) - 1
        }

    def filter_graph(self, node_types: Optional[List[str]] = None, resolution_statuses: Optional[List[str]] = None) -> Dict[str, Any]:
        nodes = []
        for n_id, attrs in self.G.nodes(data=True):
            if node_types and attrs.get("type") not in node_types:
                continue
            nodes.append({
                "id": n_id,
                "name": attrs.get("name", n_id),
                "type": attrs.get("type", "UNKNOWN"),
                "group": attrs.get("group", 1),
                "file": attrs.get("file", None),
                "module": attrs.get("module", None)
            })

        valid_node_ids = {n["id"] for n in nodes}

        links = []
        for idx, (u, v, attrs) in enumerate(self.G.edges(data=True)):
            if u not in valid_node_ids or v not in valid_node_ids:
                continue
            if resolution_statuses and attrs.get("resolution_status") not in resolution_statuses:
                continue
            links.append({
                "id": attrs.get("id", f"filter_edge_{idx}"),
                "source": u,
                "target": v,
                "type": attrs.get("type", "RELATES_TO"),
                "resolution_status": attrs.get("resolution_status", "UNKNOWN"),
                "reasoning": attrs.get("reasoning", ""),
                "evidence": attrs.get("evidence", {})
            })

        return {"nodes": nodes, "links": links}

    def get_statistics(self) -> Dict[str, Any]:
        nodes_by_type = {}
        for _, attrs in self.G.nodes(data=True):
            ntype = attrs.get("type", "UNKNOWN")
            nodes_by_type[ntype] = nodes_by_type.get(ntype, 0) + 1

        edges_by_type = {}
        edges_by_status = {}
        for _, _, attrs in self.G.edges(data=True):
            etype = attrs.get("type", "UNKNOWN")
            status = attrs.get("resolution_status", "UNKNOWN")
            edges_by_type[etype] = edges_by_type.get(etype, 0) + 1
            edges_by_status[status] = edges_by_status.get(status, 0) + 1

        total_nodes = self.G.number_of_nodes()
        total_edges = self.G.number_of_edges()
        density = nx.density(self.G) if total_nodes > 0 else 0.0
        connected_components = nx.number_weakly_connected_components(self.G) if total_nodes > 0 else 0

        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "density": round(density, 4),
            "connected_components": connected_components,
            "nodes_by_type": nodes_by_type,
            "edges_by_type": edges_by_type,
            "edges_by_status": edges_by_status
        }

    def get_dependencies(self, node_id: str, transitive: bool = False) -> Dict[str, Any]:
        if not self.G.has_node(node_id):
            return {"nodes": [], "links": []}

        if transitive:
            descendants = nx.descendants(self.G, node_id)
            descendants.add(node_id)
            sub_g = self.G.subgraph(descendants)
        else:
            successors = set(self.G.successors(node_id))
            successors.add(node_id)
            sub_g = self.G.subgraph(successors)

        return {
            "nodes": [{"id": n, "name": self.G.nodes[n].get("name", n), "type": self.G.nodes[n].get("type", "UNKNOWN")} for n in sub_g.nodes()],
            "links": [{"source": u, "target": v, "type": data.get("type"), "resolution_status": data.get("resolution_status"), "reasoning": data.get("reasoning", "")} for u, v, data in sub_g.edges(data=True)]
        }

    def get_callers(self, node_id: str, transitive: bool = False) -> Dict[str, Any]:
        if not self.G.has_node(node_id):
            return {"nodes": [], "links": []}

        if transitive:
            ancestors = nx.ancestors(self.G, node_id)
            ancestors.add(node_id)
            sub_g = self.G.subgraph(ancestors)
        else:
            predecessors = set(self.G.predecessors(node_id))
            predecessors.add(node_id)
            sub_g = self.G.subgraph(predecessors)

        return {
            "nodes": [{"id": n, "name": self.G.nodes[n].get("name", n), "type": self.G.nodes[n].get("type", "UNKNOWN")} for n in sub_g.nodes()],
            "links": [{"source": u, "target": v, "type": data.get("type"), "resolution_status": data.get("resolution_status"), "reasoning": data.get("reasoning", "")} for u, v, data in sub_g.edges(data=True)]
        }

    def get_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        if not self.G.has_node(source_id) or not self.G.has_node(target_id):
            return None
        try:
            return nx.shortest_path(self.G, source=source_id, target=target_id)
        except nx.NetworkXNoPath:
            try:
                return nx.shortest_path(self.G.to_undirected(), source=source_id, target=target_id)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                return None
        except nx.NodeNotFound:
            return None

    def get_impact_analysis(self, node_id: str) -> Optional[Dict[str, Any]]:
        if not self.G.has_node(node_id):
            return None

        target_attrs = self.G.nodes[node_id]
        target_name = target_attrs.get("name", node_id)
        target_type = target_attrs.get("type", "UNKNOWN")

        ancestors = nx.ancestors(self.G, node_id)
        affected_nodes = []

        for anc_id in ancestors:
            anc_attrs = self.G.nodes[anc_id]
            try:
                distance = nx.shortest_path_length(self.G, source=anc_id, target=node_id)
            except nx.NetworkXNoPath:
                distance = 1

            affected_nodes.append({
                "id": anc_id,
                "name": anc_attrs.get("name", anc_id),
                "type": anc_attrs.get("type", "UNKNOWN"),
                "file": anc_attrs.get("file", ""),
                "distance": distance
            })

        affected_nodes.sort(key=lambda x: (x["distance"], x["name"]))
        total_affected = len(affected_nodes)

        return {
            "target_symbol": {
                "id": node_id,
                "name": target_name,
                "type": target_type,
                "file": target_attrs.get("file", "")
            },
            "total_affected_sites": total_affected,
            "affected_nodes": affected_nodes,
            "impact_summary": f"If you modify '{target_name}', {total_affected} call/import site{'s' if total_affected != 1 else ''} elsewhere in the repository may be affected."
        }

