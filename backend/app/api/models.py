from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AnalyzeRequest(BaseModel):
    repo_url: str = Field(..., description="Public GitHub repository URL (e.g., https://github.com/psf/requests)")

class AnalyzeResponse(BaseModel):
    repo_id: int
    repository_name: str
    status: str
    commit_hash: str
    analyzer_version: str
    graph: Dict[str, Any]
    statistics: Dict[str, Any]
    file_tree: Dict[str, Any]

class RepoMetadataResponse(BaseModel):
    id: int
    url: str
    repository_name: Optional[str] = None
    commit_hash: str
    status: str
    analyzer_version: str
    analysis_duration: Optional[float] = None
    analyzed_at: str
    statistics: Optional[Dict[str, Any]] = None

class PathResponse(BaseModel):
    source: str
    target: str
    path: List[str]
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    hop_count: Optional[int] = None

class EdgeEvidenceResponse(BaseModel):
    id: str
    source: Optional[str] = None
    target: Optional[str] = None
    type: Optional[str] = None
    resolution_status: Optional[str] = None
    reasoning: Optional[str] = None
    evidence: Dict[str, Any] = Field(default_factory=dict)

class NodeDetailResponse(BaseModel):
    node: Dict[str, Any]
    incoming_count: int
    outgoing_count: int
    dependencies: List[Dict[str, Any]]
    callers: List[Dict[str, Any]]

class ChatRequest(BaseModel):
    repo_id: int
    node_id: Optional[str] = None
    question: str
    api_key: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    answer_type: str  # GRAPH | LLM
    response_source: str  # GRAPH | LLM
    verification_level: str  # VERIFIED_GRAPH_QUERY | LLM_GROUNDED_SUMMARY
    llm_used: bool
    verified_context_used: bool = True
