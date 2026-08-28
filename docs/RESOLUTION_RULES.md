# CodeAtlas Symbol Resolution Rules

CodeAtlas classifies every relationship in the repository into one of 4 strict statuses:

## 1. `VERIFIED`
- **Definition**: Relationship is conclusively proven by static AST analysis of repository source files.
- **Criteria**: The target symbol exists in the repository index, import statements match the qualified symbol name, and exact line-level AST evidence (`file`, `line`, `expression`) is recorded.
- **Example**: `from utils import helper` -> `helper()` call in `main.py` resolving to `utils.py:helper`.

## 2. `EXTERNAL`
- **Definition**: Target symbol references standard library or a third-party package not contained in the repository.
- **Criteria**: Symbol name is imported or referenced but missing from repository AST index.
- **Example**: `import os`, `import requests`, `import fastapi`.

## 3. `UNRESOLVED`
- **Definition**: Reference is statically indeterminate due to dynamic Python features (e.g. `getattr()`, `importlib`, dynamic `*args`/`**kwargs` dispatch).
- **Criteria**: Symbol reference cannot be mapped to any candidate in the index or standard external modules.

## 4. `AMBIGUOUS`
- **Definition**: Multiple symbol definitions match the target call site without sufficient qualification to disambiguate.
- **Criteria**: Call site uses short name `calculate()` and multiple un-imported classes/modules define `calculate()` in scope.
