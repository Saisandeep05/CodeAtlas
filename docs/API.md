# CodeAtlas REST API Specification

OpenAPI Swagger UI is available at `http://localhost:8000/docs`.

## Endpoints Summary

### 1. `POST /api/analyze`
- **Request**: `{ "repo_url": "https://github.com/psf/requests" }`
- **Response**: `{ "repo_id": 1, "repository_name": "requests", "status": "analyzed", "commit_hash": "...", "analyzer_version": "2.0.0", "graph": {...}, "statistics": {...}, "file_tree": {...} }`

### 2. `GET /api/repo/{id}`
- **Response**: Repository metadata, analysis status, and statistics summary.

### 3. `GET /api/repo/{id}/tree`
- **Response**: Hierarchical file tree representation.

### 4. `GET /api/repo/{id}/graph?mode=FILES|CLASSES|FUNCTIONS|FULL`
- **Response**: Filtered graph projection for the requested mode.

### 5. `GET /api/repo/{id}/node/{node_id}`
- **Response**: Detailed node attributes, incoming callers, and outgoing dependencies.

### 6. `GET /api/repo/{id}/dependencies/{node_id}?transitive=false`
- **Response**: Outgoing dependency nodes and edges.

### 7. `GET /api/repo/{id}/callers/{node_id}?transitive=false`
- **Response**: Incoming caller nodes and edges.

### 8. `GET /api/repo/{id}/subgraph/{node_id}?depth=2`
- **Response**: Focused neighborhood subgraph up to requested depth.

### 9. `GET /api/repo/{id}/path?source=nodeA&target=nodeB`
- **Response**: Shortest verified path between source and target nodes.

### 10. `GET /api/repo/{id}/evidence/{edge_id}`
- **Response**: Line-level AST evidence (`file`, `line`, `expression`, `reasoning`).

### 11. `POST /api/chat`
- **Request**: `{ "repo_id": 1, "node_id": "function:main.py:run", "question": "What calls run?" }`
- **Response**: `{ "answer": "...", "response_source": "GRAPH", "verification_level": "VERIFIED_GRAPH_QUERY", "llm_used": false }`
