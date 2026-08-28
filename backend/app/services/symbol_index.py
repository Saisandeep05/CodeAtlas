from typing import Dict, List, Any, Optional
from app.services.domain_models import SymbolMetadata

class SymbolIndex:
    def __init__(self, parsed_files: List[Dict[str, Any]] = None):
        # module_name -> file_path
        self.modules: Dict[str, str] = {}
        # symbol_full_name -> Symbol Metadata dict
        self.symbols: Dict[str, Dict[str, Any]] = {}
        # short_name -> list of symbol_full_names (for ambiguous matching)
        self.short_name_index: Dict[str, List[str]] = {}
        # class_full_name -> list of base class raw names
        self.class_bases: Dict[str, List[str]] = {}
        # package_reexports: pkg_module -> dict of exported_name -> target_full_name
        self.package_reexports: Dict[str, Dict[str, str]] = {}

        if parsed_files:
            self.build_index(parsed_files)

    def build_index(self, parsed_files: List[Dict[str, Any]]):
        for f in parsed_files:
            if "error" in f:
                continue

            file_path = f["file"]
            module_name = f["module"]
            self.modules[module_name] = file_path

            # Index classes
            for cls in f.get("classes", []):
                full_name = f"{module_name}.{cls['name']}"
                self._add_symbol(full_name, {
                    "type": "CLASS",
                    "name": cls["name"],
                    "full_name": full_name,
                    "file": file_path,
                    "line": cls["line"],
                    "module": module_name,
                    "bases": cls.get("bases", []),
                    "decorators": cls.get("decorators", [])
                })
                self.class_bases[full_name] = cls.get("bases", [])

            # Index functions
            for func in f.get("functions", []):
                if func.get("parent_class"):
                    full_name = f"{module_name}.{func['parent_class']}.{func['name']}"
                else:
                    full_name = f"{module_name}.{func['name']}"

                self._add_symbol(full_name, {
                    "type": "FUNCTION",
                    "name": func["name"],
                    "full_name": full_name,
                    "file": file_path,
                    "line": func["line"],
                    "module": module_name,
                    "parent_class": func.get("parent_class"),
                    "is_async": func.get("is_async", False),
                    "is_property": func.get("is_property", False),
                    "is_staticmethod": func.get("is_staticmethod", False),
                    "decorators": func.get("decorators", [])
                })

        # Second Pass for __init__.py package re-exports
        for f in parsed_files:
            if "error" in f:
                continue

            module_name = f["module"]
            if module_name.endswith(".__init__") or module_name == "__init__":
                pkg_module = module_name[:-9] if module_name.endswith(".__init__") else ""
                self.package_reexports[pkg_module] = {}

                for imp in f.get("imports", []):
                    if imp["type"] == "import_from":
                        rel_level = imp.get("level", 0)
                        sub_mod = imp.get("module", "")
                        sym_name = imp.get("name")
                        asname = imp.get("asname") or sym_name

                        target_mod = sub_mod
                        if rel_level > 0:
                            pkg_parts = pkg_module.split(".") if pkg_module else []
                            steps = rel_level - 1
                            if steps > 0 and len(pkg_parts) >= steps:
                                pkg_parts = pkg_parts[:-steps]
                            target_mod = ".".join(pkg_parts + ([sub_mod] if sub_mod else []))

                        target_full = f"{target_mod}.{sym_name}" if target_mod else sym_name
                        sym = self.lookup(target_full)
                        if sym:
                            pkg_export_full = f"{pkg_module}.{asname}" if pkg_module else asname
                            self.package_reexports[pkg_module][asname] = target_full
                            # Also register pkg_export_full in symbols index
                            export_meta = dict(sym)
                            export_meta["full_name"] = pkg_export_full
                            self.symbols[pkg_export_full] = export_meta

    def _add_symbol(self, full_name: str, meta: Dict[str, Any]):
        self.symbols[full_name] = meta
        short_name = meta["name"]
        if short_name not in self.short_name_index:
            self.short_name_index[short_name] = []
        if full_name not in self.short_name_index[short_name]:
            self.short_name_index[short_name].append(full_name)

    def lookup(self, full_name: str) -> Optional[Dict[str, Any]]:
        return self.symbols.get(full_name)

    def lookup_short_name(self, short_name: str) -> List[Dict[str, Any]]:
        full_names = self.short_name_index.get(short_name, [])
        return [self.symbols[fn] for fn in full_names if fn in self.symbols]

    def find_method_in_class_hierarchy(self, class_full_name: str, method_name: str, visited: set = None) -> Optional[Dict[str, Any]]:
        if visited is None:
            visited = set()

        if class_full_name in visited:
            return None
        visited.add(class_full_name)

        # 1. Direct method lookup in current class
        direct_method_key = f"{class_full_name}.{method_name}"
        sym = self.lookup(direct_method_key)
        if sym and sym["type"] == "FUNCTION":
            return sym

        # 2. Search parent classes
        bases = self.class_bases.get(class_full_name, [])
        cls_meta = self.lookup(class_full_name)
        cls_module = cls_meta["module"] if cls_meta else class_full_name.rsplit(".", 1)[0]

        for base_raw in bases:
            candidate_full = f"{cls_module}.{base_raw}"
            if not self.lookup(candidate_full):
                candidates = [c for c in self.lookup_short_name(base_raw) if c["type"] == "CLASS"]
                if len(candidates) == 1:
                    candidate_full = candidates[0]["full_name"]

            if self.lookup(candidate_full):
                found = self.find_method_in_class_hierarchy(candidate_full, method_name, visited)
                if found:
                    return found

        return None
