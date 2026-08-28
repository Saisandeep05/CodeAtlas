# CodeAtlas Architecture & Design Specification

## Overview
CodeAtlas is a web-based verified architecture explorer designed to analyze Python repositories statically, build an evidence-backed NetworkX graph, and enable both zero-LLM structural queries and LLM-grounded architectural explanations.

## Two-Pass Analysis Subsystem

### Pass 1: AST Extraction (`code_parser.py`)
Parses Python source code into abstract syntax trees (`ast.parse()`).
- Collects imports (`Import`, `ImportFrom`).
- Collects class definitions (`ClassDef`), base classes, method definitions.
- Collects function definitions (`FunctionDef`), calls (`Call`), and expressions.
- Captures line-level evidence (`file`, `line`, `expression`).

### Pass 2: Global Symbol Resolution (`symbol_resolver.py` & `symbol_index.py`)
- Builds `SymbolIndex` across all parsed repository files.
- Resolves import aliases, relative imports, and class inheritance trees.
- Classifies each relationship into `VERIFIED`, `EXTERNAL`, `UNRESOLVED`, or `AMBIGUOUS`.

## Graph & Query Engine (`graph_builder.py`, `graph_query_service.py`)
- Constructs NetworkX graph with node types (`FILE`, `MODULE`, `CLASS`, `FUNCTION`, `METHOD`, `EXTERNAL`, `UNRESOLVED`, `AMBIGUOUS`) and edge types (`IMPORTS`, `CALLS`, `INHERITS`, `DEFINES`).
- Executes graph validation pass asserting duplicate node check, endpoint validity, evidence non-emptiness, and target presence.
- Routes structural questions directly to `GraphQueryService` (`response_source = "GRAPH"`, `verification_level = "VERIFIED_GRAPH_QUERY"`).
