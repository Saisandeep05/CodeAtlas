import os
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.api.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    RepoMetadataResponse,
    PathResponse,
    EdgeEvidenceResponse,
    NodeDetailResponse,
    ChatRequest,
    ChatResponse
)
from app.services.github_service import GithubService, RepositoryValidationError
from app.services.code_parser import parse_file
from app.services.graph_builder import build_graph, project_graph_mode
from app.services.graph_query_service import GraphQueryService
from app.services.llm_service import LLMService
from app.services.stats_service import compute_statistics
from app.database.database import Database
from config import ANALYZER_VERSION

router = APIRouter()
db = Database()
llm_service = LLMService()

def _build_file_tree(py_files_rel: list) -> dict:
    root = {"name": "root", "type": "directory", "children": []}

    for file_path in sorted(py_files_rel):
        parts = file_path.replace("\\", "/").split("/")
        current = root

        for i, part in enumerate(parts):
            is_file = (i == len(parts) - 1)

            if is_file:
                current["children"].append({
                    "name": part,
                    "type": "file",
                    "path": file_path
                })
            else:
                existing = None
                for child in current["children"]:
                    if child["type"] == "directory" and child["name"] == part:
                        existing = child
                        break

                if existing is None:
                    existing = {"name": part, "type": "directory", "children": []}
                    current["children"].append(existing)

                current = existing

    return root

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repo(request: AnalyzeRequest):
    repo_url = request.repo_url.strip()
    github_service = GithubService()

    try:
        github_service.validate_url(repo_url)
    except RepositoryValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    commit_hash = github_service.get_latest_commit_hash(repo_url)

    cached_repo = db.get_repo_by_url(repo_url)
    if cached_repo and cached_repo.get("commit_hash") == commit_hash and cached_repo.get("analyzer_version") == ANALYZER_VERSION:
        graph = db.get_cached_graph(cached_repo["id"])
        statistics = db.get_cached_statistics(cached_repo["id"])
        file_tree = db.get_cached_file_tree(cached_repo["id"])
        if graph and statistics and file_tree:
            return {
                "repo_id": cached_repo["id"],
                "repository_name": cached_repo.get("repository_name", ""),
                "status": "cached",
                "commit_hash": commit_hash,
                "analyzer_version": ANALYZER_VERSION,
                "graph": graph,
                "statistics": statistics,
                "file_tree": file_tree
            }

    start_time = time.time()
    repo_path = ""
    try:
        repo_path, commit_hash = github_service.clone_repo(repo_url)
        _, repo_name = github_service.validate_url(repo_url)
        py_files = github_service.get_python_files(repo_path)

        parsed_results = []
        source_cache = {}
        py_files_rel = []

        for py_file in py_files:
            res = parse_file(py_file, repo_path)
            parsed_results.append(res)

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    rel_path = os.path.relpath(py_file, repo_path).replace("\\", "/")
                    source_cache[rel_path] = f.read()
                    py_files_rel.append(rel_path)
            except Exception:
                pass

        graph_data = build_graph(parsed_results)
        analysis_duration = time.time() - start_time
        resolved_edges = graph_data.get("links", [])
        statistics = compute_statistics(parsed_results, resolved_edges, analysis_duration)
        file_tree = _build_file_tree(py_files_rel)

        repo_id = db.create_or_update_repo(
            repo_url, commit_hash,
            repository_name=repo_name,
            analysis_duration=analysis_duration,
            analyzer_version=ANALYZER_VERSION
        )
        db.cache_analysis(repo_id, graph_data, source_cache, file_tree, statistics, analyzer_version=ANALYZER_VERSION)

        return {
            "repo_id": repo_id,
            "repository_name": repo_name,
            "status": "analyzed",
            "commit_hash": commit_hash,
            "analyzer_version": ANALYZER_VERSION,
            "graph": graph_data,
            "statistics": statistics,
            "file_tree": file_tree
        }

    except RepositoryValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if repo_path:
            github_service.cleanup(repo_path)

@router.get("/repo/{repo_id}", response_model=RepoMetadataResponse)
async def get_repo_metadata(repo_id: int):
    repo = db.get_repo_by_id(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    statistics = db.get_cached_statistics(repo_id)

    return {
        "id": repo["id"],
        "url": repo["url"],
        "repository_name": repo.get("repository_name"),
        "commit_hash": repo["commit_hash"],
        "status": repo["status"],
        "analyzer_version": repo.get("analyzer_version", ANALYZER_VERSION),
        "analysis_duration": repo.get("analysis_duration"),
        "analyzed_at": repo["analyzed_at"],
        "statistics": statistics
    }

@router.get("/repo/{repo_id}/tree")
async def get_repo_tree(repo_id: int):
    file_tree = db.get_cached_file_tree(repo_id)
    if not file_tree:
        raise HTTPException(status_code=404, detail="File tree not found.")
    return file_tree

@router.get("/repo/{repo_id}/graph")
async def get_repo_graph(
    repo_id: int,
    mode: Optional[str] = Query("FILES", pattern="^(FILES|CLASSES|FUNCTIONS|FULL)$")
):
    graph = db.get_cached_graph(repo_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    return project_graph_mode(graph, mode)

@router.get("/repo/{repo_id}/subgraph/{node_id:path}")
async def get_subgraph(repo_id: int, node_id: str, depth: int = Query(2, ge=1, le=5)):
    graph = db.get_cached_graph(repo_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    service = GraphQueryService(graph)
    return service.get_subgraph(node_id, depth)

@router.get("/repo/{repo_id}/dependencies/{node_id:path}")
async def get_dependencies(repo_id: int, node_id: str, transitive: bool = Query(False)):
    graph = db.get_cached_graph(repo_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    service = GraphQueryService(graph)
    return service.get_dependencies(node_id, transitive)

@router.get("/repo/{repo_id}/callers/{node_id:path}")
async def get_callers(repo_id: int, node_id: str, transitive: bool = Query(False)):
    graph = db.get_cached_graph(repo_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    service = GraphQueryService(graph)
    return service.get_callers(node_id, transitive)

@router.get("/repo/{repo_id}/path", response_model=PathResponse)
async def get_shortest_path(repo_id: int, source: str = Query(...), target: str = Query(...)):
    graph = db.get_cached_graph(repo_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    service = GraphQueryService(graph)
    path_info = service.find_path(source, target)
    if not path_info:
        raise HTTPException(status_code=404, detail="No verified path exists between source and target.")
    return path_info

@router.get("/repo/{repo_id}/node/{node_id:path}", response_model=NodeDetailResponse)
async def get_node_details(repo_id: int, node_id: str):
    graph = db.get_cached_graph(repo_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    service = GraphQueryService(graph)
    summary = service.get_node_summary(node_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found.")

    return summary

@router.get("/repo/{repo_id}/evidence/{edge_id}", response_model=EdgeEvidenceResponse)
async def get_edge_evidence(repo_id: int, edge_id: str):
    graph = db.get_cached_graph(repo_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    service = GraphQueryService(graph)
    evidence = service.get_edge_evidence(edge_id)
    if not evidence:
        raise HTTPException(status_code=404, detail=f"Edge '{edge_id}' not found.")

    return evidence

@router.get("/repo/{repo_id}/impact/{node_id:path}")
async def get_impact_analysis(repo_id: int, node_id: str):
    graph = db.get_cached_graph(repo_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    service = GraphQueryService(graph)
    impact = service.get_impact_analysis(node_id)
    if not impact:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found.")

    return impact

@router.post("/chat", response_model=ChatResponse)
async def chat_with_repo(request: ChatRequest):
    repo = db.get_repo_by_id(request.repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not analyzed.")

    cached_graph = db.get_cached_graph(request.repo_id)
    if not cached_graph:
        raise HTTPException(status_code=404, detail="Repo graph not found.")

    source_cache = db.get_cached_source(request.repo_id) or {}
    query_service = GraphQueryService(cached_graph)

    if query_service.is_structural_question(request.question):
        if not request.node_id:
            return {
                "answer": "Please select a specific node in the graph to inspect structural relationships.",
                "answer_type": "GRAPH",
                "response_source": "GRAPH",
                "verification_level": "VERIFIED_GRAPH_QUERY",
                "llm_used": False,
                "verified_context_used": True
            }
        res_dict = query_service.query_structural(request.node_id, request.question)
        return {
            "answer": res_dict["answer"],
            "answer_type": "GRAPH",
            "response_source": "GRAPH",
            "verification_level": "VERIFIED_GRAPH_QUERY",
            "llm_used": False,
            "verified_context_used": True
        }
    else:
        if not request.node_id:
            return {
                "answer": "Please select a node to explain its logic.",
                "answer_type": "LLM",
                "response_source": "LLM",
                "verification_level": "LLM_GROUNDED_SUMMARY",
                "llm_used": False,
                "verified_context_used": False
            }

        node_file = None
        for node in cached_graph.get("nodes", []):
            if node["id"] == request.node_id:
                node_file = node.get("file")
                break

        source_code = None
        if node_file and node_file in source_cache:
            source_code = source_cache[node_file]

        answer = llm_service.answer_fuzzy_question(
            request.question,
            request.node_id,
            cached_graph,
            source_code,
            request_api_key=request.api_key
        )
        return {
            "answer": answer,
            "answer_type": "LLM",
            "response_source": "LLM",
            "verification_level": "LLM_GROUNDED_SUMMARY",
            "llm_used": True,
            "verified_context_used": True
        }
