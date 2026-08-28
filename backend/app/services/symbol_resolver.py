from typing import List, Dict, Any, Optional, Tuple
from app.services.symbol_index import SymbolIndex
from app.services.domain_models import Evidence, ResolvedRelationship, get_canonical_node_id

class SymbolResolver:
    def __init__(self, index: SymbolIndex):
        self.index = index

    def _resolve_relative_module(self, current_module: str, level: int, target_module: str) -> str:
        parts = current_module.split(".")

        if parts[-1] == "__init__":
            package_parts = parts[:-1]
        else:
            package_parts = parts[:-1]

        steps_up = level - 1

        if steps_up > 0:
            if steps_up >= len(package_parts):
                return target_module if target_module else ""
            package_parts = package_parts[:-steps_up]

        if target_module:
            return ".".join(package_parts + [target_module]) if package_parts else target_module
        else:
            return ".".join(package_parts) if package_parts else ""

    def resolve_relationships(self, parsed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        edges: List[Dict[str, Any]] = []

        for f in parsed_files:
            if "error" in f:
                continue

            file_path = f["file"]
            file_id = get_canonical_node_id("FILE", file_path, "")
            module_name = f["module"]

            # 1. Structure Definitions (VERIFIED)
            for cls in f.get("classes", []):
                cls_id = get_canonical_node_id("CLASS", file_path, cls["name"])
                reasoning = "Class definition in repository"
                rel = ResolvedRelationship(
                    source=file_id,
                    target=cls_id,
                    relationship_type="DEFINES",
                    resolution_status="VERIFIED",
                    reasoning=reasoning,
                    evidence=Evidence(file=file_path, line=cls["line"], expression=cls["evidence"])
                )
                edges.append(rel.to_dict())

            for func in f.get("functions", []):
                if func.get("parent_class"):
                    func_name = f"{func['parent_class']}.{func['name']}"
                    func_id = get_canonical_node_id("METHOD", file_path, func_name)
                    parent_id = get_canonical_node_id("CLASS", file_path, func["parent_class"])
                    reasoning = "Method definition on class in repository"
                    rel = ResolvedRelationship(
                        source=parent_id,
                        target=func_id,
                        relationship_type="DEFINES",
                        resolution_status="VERIFIED",
                        reasoning=reasoning,
                        evidence=Evidence(file=file_path, line=func["line"], expression=func["evidence"])
                    )
                    edges.append(rel.to_dict())
                else:
                    func_id = get_canonical_node_id("FUNCTION", file_path, func["name"])
                    reasoning = "Function definition in repository"
                    rel = ResolvedRelationship(
                        source=file_id,
                        target=func_id,
                        relationship_type="DEFINES",
                        resolution_status="VERIFIED",
                        reasoning=reasoning,
                        evidence=Evidence(file=file_path, line=func["line"], expression=func["evidence"])
                    )
                    edges.append(rel.to_dict())

            # 2. Imports Resolution with Alias & Re-export Support
            local_imports: Dict[str, Tuple[str, bool]] = {}  # bound_alias -> (full_target, is_explicit_alias)

            for imp in f.get("imports", []):
                if imp["type"] == "import":
                    target_module = imp["module"]
                    bound_name = imp.get("asname") or target_module
                    is_alias = bool(imp.get("asname"))

                    is_internal = target_module in self.index.modules
                    if is_internal:
                        status = "VERIFIED"
                        target_id = get_canonical_node_id("FILE", self.index.modules[target_module], "")
                        reasoning = "Resolved via import alias mapping" if is_alias else "Imported internal module"
                    else:
                        status = "EXTERNAL"
                        target_id = f"module:{target_module}"
                        reasoning = "External library or standard library package"

                    rel = ResolvedRelationship(
                        source=file_id,
                        target=target_id,
                        relationship_type="IMPORTS",
                        resolution_status=status,
                        reasoning=reasoning,
                        evidence=Evidence(file=file_path, line=imp["line"], expression=imp["evidence"])
                    )
                    edges.append(rel.to_dict())
                    local_imports[bound_name] = (target_module, is_alias)

                elif imp["type"] == "import_from":
                    source_module = imp["module"]
                    symbol_name = imp["name"]
                    bound_name = imp.get("asname") or symbol_name
                    is_alias = bool(imp.get("asname"))
                    level = imp.get("level", 0)

                    if level > 0:
                        source_module = self._resolve_relative_module(module_name, level, source_module)

                    full_target = f"{source_module}.{symbol_name}" if source_module else symbol_name

                    sym = self.index.lookup(full_target)
                    if sym:
                        status = "VERIFIED"
                        name_key = f"{sym['parent_class']}.{sym['name']}" if sym.get("parent_class") else sym["name"]
                        target_id = get_canonical_node_id(sym["type"], sym["file"], name_key)
                        if is_alias:
                            reasoning = "Resolved via import alias mapping"
                        elif source_module in self.index.package_reexports:
                            reasoning = "Resolved via __init__.py package re-export"
                        else:
                            reasoning = "Imported from internal module"
                    elif source_module in self.index.modules:
                        status = "VERIFIED"
                        target_id = get_canonical_node_id("FILE", self.index.modules[source_module], "")
                        reasoning = "Imported from internal module"
                    else:
                        status = "EXTERNAL"
                        target_id = f"external:{full_target}"
                        reasoning = "External library or standard library package"

                    rel = ResolvedRelationship(
                        source=file_id,
                        target=target_id,
                        relationship_type="IMPORTS",
                        resolution_status=status,
                        reasoning=reasoning,
                        evidence=Evidence(file=file_path, line=imp["line"], expression=imp["evidence"])
                    )
                    edges.append(rel.to_dict())
                    local_imports[bound_name] = (full_target, is_alias)

            # 3. Inheritance Resolution
            for cls in f.get("classes", []):
                cls_id = get_canonical_node_id("CLASS", file_path, cls["name"])
                for base in cls.get("bases", []):
                    target_id = None
                    status = "UNRESOLVED"
                    reasoning = ""

                    if base in local_imports:
                        full_base, is_alias = local_imports[base]
                        sym = self.index.lookup(full_base)
                        if sym and sym["type"] == "CLASS":
                            target_id = get_canonical_node_id("CLASS", sym["file"], sym["name"])
                            status = "VERIFIED"
                            reasoning = "Direct base class definition in repository"
                        else:
                            target_id = f"external:{full_base}"
                            status = "EXTERNAL"
                            reasoning = "External library or standard library package"
                    else:
                        local_target = f"{module_name}.{base}"
                        sym = self.index.lookup(local_target)
                        if sym and sym["type"] == "CLASS":
                            target_id = get_canonical_node_id("CLASS", sym["file"], sym["name"])
                            status = "VERIFIED"
                            reasoning = "Direct base class definition in repository"
                        else:
                            candidates = self.index.lookup_short_name(base)
                            class_candidates = [c for c in candidates if c["type"] == "CLASS"]
                            if len(class_candidates) == 1:
                                target_id = get_canonical_node_id("CLASS", class_candidates[0]["file"], class_candidates[0]["name"])
                                status = "VERIFIED"
                                reasoning = "Direct base class definition in repository"
                            elif len(class_candidates) > 1:
                                target_id = f"ambiguous:{base}"
                                status = "AMBIGUOUS"
                                reasoning = "Multiple candidate symbols match without disambiguating scope"
                            else:
                                target_id = f"external:{base}"
                                status = "EXTERNAL"
                                reasoning = "External library or standard library package"

                    rel = ResolvedRelationship(
                        source=cls_id,
                        target=target_id,
                        relationship_type="INHERITS",
                        resolution_status=status,
                        reasoning=reasoning,
                        evidence=Evidence(file=file_path, line=cls["line"], expression=cls["evidence"])
                    )
                    edges.append(rel.to_dict())

            # 4. Calls Resolution
            for call in f.get("calls", []):
                if call["caller_class"]:
                    caller_func_name = f"{call['caller_class']}.{call['caller_func']}"
                    caller_id = get_canonical_node_id("METHOD", file_path, caller_func_name)
                elif call["caller_func"]:
                    caller_id = get_canonical_node_id("FUNCTION", file_path, call["caller_func"])
                else:
                    caller_id = file_id

                callee = call["callee"]
                is_attr = call["is_attribute"]

                target_id = None
                status = "UNRESOLVED"
                reasoning = ""

                # Check dynamic calls first
                if callee in ["getattr", "globals", "importlib", "exec", "eval"] or "getattr" in callee or "importlib" in callee:
                    status = "UNRESOLVED"
                    target_id = f"unresolved:{callee}"
                    reasoning = "Dynamic runtime symbol evaluation cannot be proven statically"

                # Check self.method() or super().method() in class scope
                elif is_attr and call["caller_class"]:
                    parts = callee.split(".", 1)
                    obj_name = parts[0]
                    method_name = parts[1] if len(parts) > 1 else ""

                    current_class_full = f"{module_name}.{call['caller_class']}"

                    if obj_name == "self" and method_name:
                        found_method = self.index.find_method_in_class_hierarchy(current_class_full, method_name)
                        if found_method:
                            full_m_name = f"{found_method['parent_class']}.{found_method['name']}" if found_method.get("parent_class") else found_method["name"]
                            target_id = get_canonical_node_id("METHOD", found_method["file"], full_m_name)
                            status = "VERIFIED"
                            if found_method["parent_class"] == call["caller_class"]:
                                reasoning = "Method defined on current class"
                            else:
                                reasoning = "Method resolved on parent class in inheritance hierarchy"

                    elif obj_name == "super()" and method_name:
                        bases = self.index.class_bases.get(current_class_full, [])
                        for base_raw in bases:
                            parent_candidate = f"{module_name}.{base_raw}"
                            if not self.index.lookup(parent_candidate):
                                class_cands = [c for c in self.index.lookup_short_name(base_raw) if c["type"] == "CLASS"]
                                if len(class_cands) == 1:
                                    parent_candidate = class_cands[0]["full_name"]

                            found_method = self.index.find_method_in_class_hierarchy(parent_candidate, method_name)
                            if found_method:
                                full_m_name = f"{found_method['parent_class']}.{found_method['name']}" if found_method.get("parent_class") else found_method["name"]
                                target_id = get_canonical_node_id("METHOD", found_method["file"], full_m_name)
                                status = "VERIFIED"
                                reasoning = "Resolved via super() parent class method lookup"
                                break

                # Standard function / alias / module attribute resolution
                if status == "UNRESOLVED" and not reasoning:
                    if not is_attr:
                        if callee in local_imports:
                            full_sym, is_alias = local_imports[callee]
                            sym = self.index.lookup(full_sym)
                            if sym:
                                name_key = f"{sym['parent_class']}.{sym['name']}" if sym.get("parent_class") else sym["name"]
                                target_id = get_canonical_node_id(sym["type"], sym["file"], name_key)
                                status = "VERIFIED"
                                reasoning = "Resolved via import alias mapping" if is_alias else "Imported from internal module"
                            else:
                                target_id = f"external:{full_sym}"
                                status = "EXTERNAL"
                                reasoning = "External library or standard library package"
                        else:
                            # Local function definition in same file
                            local_func = f"{module_name}.{callee}"
                            sym = self.index.lookup(local_func)
                            if sym:
                                name_key = f"{sym['parent_class']}.{sym['name']}" if sym.get("parent_class") else sym["name"]
                                target_id = get_canonical_node_id(sym["type"], sym["file"], name_key)
                                status = "VERIFIED"
                                reasoning = "Local function definition in same file"
                            else:
                                candidates = self.index.lookup_short_name(callee)
                                if len(candidates) == 1:
                                    c = candidates[0]
                                    name_key = f"{c['parent_class']}.{c['name']}" if c.get("parent_class") else c["name"]
                                    target_id = get_canonical_node_id(c["type"], c["file"], name_key)
                                    status = "VERIFIED"
                                    reasoning = "Imported from internal module"
                                elif len(candidates) > 1:
                                    target_id = f"ambiguous:{callee}"
                                    status = "AMBIGUOUS"
                                    reasoning = "Multiple candidate symbols match without disambiguating scope"
                                else:
                                    if callee in ["print", "len", "str", "int", "dict", "list", "set", "range", "open", "requests", "sys", "os"]:
                                        target_id = f"external:{callee}"
                                        status = "EXTERNAL"
                                        reasoning = "External library or standard library package"
                                    else:
                                        target_id = f"unresolved:{callee}"
                                        status = "UNRESOLVED"
                                        reasoning = "Symbol definition not found in repository index"
                    else:
                        parts = callee.split(".")
                        if len(parts) == 2:
                            cls_name, method_name = parts[0], parts[1]
                            cls_sym = None
                            if cls_name in local_imports:
                                target_full, _ = local_imports[cls_name]
                                cls_sym = self.index.lookup(target_full)
                            if not cls_sym:
                                local_cls = f"{module_name}.{cls_name}"
                                cls_sym = self.index.lookup(local_cls)
                            if not cls_sym:
                                class_cands = [c for c in self.index.lookup_short_name(cls_name) if c["type"] == "CLASS"]
                                if len(class_cands) == 1:
                                    cls_sym = class_cands[0]

                            if cls_sym and cls_sym["type"] == "CLASS":
                                method_sym = self.index.find_method_in_class_hierarchy(cls_sym["full_name"], method_name)
                                if method_sym and method_sym.get("is_staticmethod"):
                                    name_key = f"{method_sym['parent_class']}.{method_sym['name']}" if method_sym.get("parent_class") else method_sym["name"]
                                    target_id = get_canonical_node_id("METHOD", method_sym["file"], name_key)
                                    status = "VERIFIED"
                                    reasoning = "Resolved via static method lookup on a known class"

                        if status == "UNRESOLVED" and len(parts) == 2 and parts[0] in local_imports:
                            mod_target, is_alias = local_imports[parts[0]]
                            full_sym = f"{mod_target}.{parts[1]}"
                            sym = self.index.lookup(full_sym)
                            if sym:
                                name_key = f"{sym['parent_class']}.{sym['name']}" if sym.get("parent_class") else sym["name"]
                                target_id = get_canonical_node_id(sym["type"], sym["file"], name_key)
                                status = "VERIFIED"
                                reasoning = "Resolved via module attribute lookup"
                            else:
                                target_id = f"external:{full_sym}"
                                status = "EXTERNAL"
                                reasoning = "External library or standard library package"
                        elif status == "UNRESOLVED":
                            if parts[0] in ["requests", "sys", "os", "json", "math", "logging"]:
                                target_id = f"external:{callee}"
                                status = "EXTERNAL"
                                reasoning = "External library or standard library package"
                            else:
                                target_id = f"unresolved:{callee}"
                                status = "UNRESOLVED"
                                reasoning = "Symbol definition not found in repository index"

                rel = ResolvedRelationship(
                    source=caller_id,
                    target=target_id,
                    relationship_type="CALLS",
                    resolution_status=status,
                    reasoning=reasoning,
                    evidence=Evidence(file=file_path, line=call["line"], expression=call["evidence"])
                )
                edges.append(rel.to_dict())

        return edges
