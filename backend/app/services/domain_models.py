from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Evidence:
    file: str
    line: int
    expression: str
    context: Optional[str] = None

@dataclass
class ImportBinding:
    bound_name: str
    target_module: str
    symbol_name: Optional[str] = None
    asname: Optional[str] = None
    level: int = 0
    file_path: str = ""
    line: int = 0
    evidence: str = ""

@dataclass
class RawImport:
    type: str  # "import" | "import_from"
    module: str
    name: Optional[str] = None
    asname: Optional[str] = None
    level: int = 0
    file: str = ""
    line: int = 0
    evidence: str = ""

@dataclass
class RawCall:
    caller_func: Optional[str] = None
    caller_class: Optional[str] = None
    callee: str = ""
    is_attribute: bool = False
    file: str = ""
    line: int = 0
    evidence: str = ""

@dataclass
class RawClass:
    name: str
    file: str
    module: str
    line: int
    bases: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    evidence: str = ""

@dataclass
class RawFunction:
    name: str
    file: str
    module: str
    line: int
    parent_class: Optional[str] = None
    is_async: bool = False
    is_property: bool = False
    is_staticmethod: bool = False
    decorators: List[str] = field(default_factory=list)
    evidence: str = ""

@dataclass
class SymbolMetadata:
    symbol_type: str  # "FILE" | "CLASS" | "FUNCTION" | "METHOD"
    name: str
    full_name: str
    file_path: str
    line: int
    module: str
    parent_class: Optional[str] = None
    bases: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    is_property: bool = False
    is_staticmethod: bool = False

@dataclass
class CanonicalNode:
    id: str  # file:<path> | class:<path>:<Name> | function:<path>:<func>
    name: str
    type: str
    file: Optional[str] = None
    module: Optional[str] = None
    group: int = 1

def get_canonical_node_id(symbol_type: str, file_path: str, name: str) -> str:
    """
    Constructs a collision-proof canonical node ID:
    - File: file:<file_path>
    - Class: class:<file_path>:<class_name>
    - Function/Method: function:<file_path>:<name> or function:<file_path>:<class_name>.<method_name>
    """
    normalized_file = file_path.replace("\\", "/")
    if symbol_type == "FILE":
        return f"file:{normalized_file}"
    elif symbol_type == "CLASS":
        return f"class:{normalized_file}:{name}"
    elif symbol_type in ["FUNCTION", "METHOD"]:
        return f"function:{normalized_file}:{name}"
    return f"{symbol_type.lower()}:{normalized_file}:{name}"

@dataclass
class ResolvedRelationship:
    source: str  # source canonical ID
    target: str  # target canonical ID
    relationship_type: str  # IMPORTS | CALLS | INHERITS | DEFINES
    resolution_status: str  # VERIFIED | EXTERNAL | UNRESOLVED | AMBIGUOUS
    reasoning: str  # Explains WHY it was classified this way
    evidence: Evidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.relationship_type,
            "resolution_status": self.resolution_status,
            "reasoning": self.reasoning,
            "evidence": {
                "file": self.evidence.file,
                "line": self.evidence.line,
                "expression": self.evidence.expression,
                "context": self.evidence.context
            }
        }

@dataclass
class ResolutionResult:
    relationships: List[ResolvedRelationship] = field(default_factory=list)
    verified_count: int = 0
    external_count: int = 0
    unresolved_count: int = 0
    ambiguous_count: int = 0

@dataclass
class RepositoryAnalysisResult:
    parsed_files: List[Dict[str, Any]] = field(default_factory=list)
    symbols: Dict[str, SymbolMetadata] = field(default_factory=dict)
    relationships: List[ResolvedRelationship] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
