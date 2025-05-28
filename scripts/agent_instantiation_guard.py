#!/usr/bin/env python3
"""
Codemod to scan for direct agent instantiations outside of the orchestrator
and suggest/apply fixes using orchestrator.load_agent().

Requires LibCST: pip install libcst
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Add current script's directory to path to find sibling modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

import libcst as cst

# Import our custom wrapper for CodemodContext
from legion_codemod_context import CodemodContext
from libcst.codemod import VisitorBasedCodemodCommand
from libcst.metadata import PositionProvider, QualifiedNameProvider, ScopeProvider

# Agent classes to target (ensure these match the exact class names)
AGENT_CLASSES: Set[str] = {
    "ArchitectAgent"
    "TherapistAgent"
    "MetricsAgent"
    "UxDesignerAgent",  # Assuming 'Ux' not 'UX' based on previous interaction
    "PingAgent"
    "EchoAgent"
}

# Path to the orchestrator module, relative to repo root, using OS-specific separators
ORCHESTRATOR_MODULE_PATH_PARTS: Tuple[str, ...] = ("legion", "agents", "python")
ORCHESTRATOR_FILE_PATH_STR: str = str(Path("legion") / "orchestrator.py")

# Expected import prefix for agent classes
AGENT_IMPORT_PREFIX: Tuple[str, ...] = ("legion", "agents", "python")


def class_name_to_agent_key(class_name: str) -> str:
    """Converts Agent ClassName to snake_case_key (e.g., ArchitectAgent -> architect)."""
    if class_name.endswith("Agent"):
        base_name = class_name[: -len("Agent")]
    else:
        base_name = class_name  # Should not happen with current AGENT_CLASSES
    # Convert CamelCase (like UXDesigner) to snake_case (ux_designer)
    return re.sub(r"(?<!^)(?=[A-Z])", "_", base_name).lower()


class ImportRemover(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, classes_to_remove: Set[str]):
        super().__init__()
        self.classes_to_remove = classes_to_remove

    def leave_ImportFrom(  # noqa: N802
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> cst.CSTNode | cst.RemovalSentinel:
        module_path_parts = []
        current_module_part = updated_node.module
        while isinstance(current_module_part, cst.Attribute):
            if isinstance(current_module_part.attr, cst.Name):
                module_path_parts.insert(0, current_module_part.attr.value)
            current_module_part = current_module_part.value
        if isinstance(current_module_part, cst.Name):
            module_path_parts.insert(0, current_module_part.value)

        if tuple(module_path_parts[: len(AGENT_IMPORT_PREFIX)]) != AGENT_IMPORT_PREFIX:
            return updated_node

        if isinstance(updated_node.names, cst.ImportStar):
            # If we removed specific agent classes that were later imported via '*'
            # this import * might become risky. For now, don't touch it.
            # A more advanced check could see if any AGENT_CLASSES were in this module.
            return updated_node

        new_names: List[cst.ImportAlias] = []
        modified = False
        for import_alias in updated_node.names:
            # import_alias.name is the original name (e.g., ArchitectAgent)
            original_imported_name = import_alias.name.value
            if original_imported_name in self.classes_to_remove:
                modified = True
            else:
                new_names.append(import_alias)

        if modified:
            if not new_names:  # All names from this import statement were removed
                return cst.RemoveFromParent()
            return updated_node.with_changes(names=tuple(new_names))
        return updated_node


class AgentInstantiationCodemod(VisitorBasedCodemodCommand):
    DESCRIPTION: str = (
        "Detects direct agent instantiations and replaces them "
        "with orchestrator.load_agent()."
    )
    METADATA_DEPENDENCIES = (PositionProvider, ScopeProvider, QualifiedNameProvider)

    @staticmethod
    def add_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--apply"
            action="store_true"
            help="Apply changes to files."
        )
        # The 'paths' argument is implicitly handled by run_codemod or the calling script

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        # Determine apply_fixes from codemod context scratch if provided
        self.apply_fixes: bool = getattr(context, "scratch", {}).get("apply", False)
        self.warnings: List[str] = []
        # Stores agent class names whose instantiations were transformed in the current file
        self.transformed_agent_classes_current_file: Set[str] = set()

        # Determine the root directory for relative path calculations
        # This assumes the script is run with paths relative to some common root
        # or paths are absolute. LibCST's context.filename is usually relative.
        self.repo_root: Path = context.scratch.get("repo_root", Path.cwd())

    def should_skip_file(self) -> bool:
        """Checks if the current file is legion/orchestrator.py."""
        try:
            # context.full_path is preferred if available and absolute
            # context.filename is often relative to where the command is run
            current_file_path = Path(self.context.filename)
            if not current_file_path.is_absolute():
                current_file_path = (self.repo_root / current_file_path).resolve()

            orchestrator_abs_path = (
                self.repo_root / ORCHESTRATOR_FILE_PATH_STR
            ).resolve()
            return current_file_path == orchestrator_abs_path
        except Exception:
            # If path resolution fails, err on the side of caution and process the file
            return False

    def visit_Call(self, node: cst.Call) -> None:  # noqa: N802
        if self.should_skip_file():
            return

        # Try to resolve the function being called
        try:
            # Get qualified names for the function/class being called
            qualified_names = self.get_metadata(QualifiedNameProvider, node.func)
        except KeyError:  # Metadata might not be available for all nodes
            qualified_names = None

        resolved_class_name = None
        if isinstance(node.func, cst.Name):
            # Direct call like `ArchitectAgent()`
            # Check if it's one of our agent classes
            # For simple names, check if they are imported from the expected agent modules
            if qualified_names:
                for qn in qualified_names:
                    if qn.name.startswith(f"{'.'.join(AGENT_IMPORT_PREFIX)}."):
                        class_part = qn.name.split(".")[-1]
                        if class_part in AGENT_CLASSES:
                            resolved_class_name = class_part
                            break
            elif node.func.value in AGENT_CLASSES:  # Fallback for no qualified name
                resolved_class_name = node.func.value

        if resolved_class_name:
            agent_key = class_name_to_agent_key(resolved_class_name)
            pos = self.get_metadata(PositionProvider, node)

            # Use relative path for warning if possible
            try:
                relative_path = Path(self.context.filename).relative_to(self.repo_root)
            except ValueError:
                relative_path = Path(self.context.filename)

            warning_message = (
                f"{relative_path}:{pos.start.line}: Direct instantiation of {resolved_class_name} "
                f"detected; use `orchestrator.load_agent('{agent_key}')` instead."
            )
            if (
                warning_message not in self.warnings
            ):  # Avoid duplicate warnings for same node if visited multiple times
                self.warnings.append(warning_message)

            if self.apply_fixes:
                # Mark this class name for import removal if we successfully transform it
                # The actual transformation happens in leave_Call
                pass  # Handled in leave_Call

    def leave_Call(  # noqa: N802
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.CSTNode:
        if not self.apply_fixes or self.should_skip_file():
            return updated_node

        try:
            qualified_names = self.get_metadata(
                QualifiedNameProvider, original_node.func
            )
        except KeyError:
            qualified_names = None

        resolved_class_name = None
        if isinstance(original_node.func, cst.Name):
            if qualified_names:
                for qn in qualified_names:
                    if qn.name.startswith(f"{'.'.join(AGENT_IMPORT_PREFIX)}."):
                        class_part = qn.name.split(".")[-1]
                        if class_part in AGENT_CLASSES:
                            resolved_class_name = class_part
                            break
            elif original_node.func.value in AGENT_CLASSES:
                resolved_class_name = original_node.func.value

        if resolved_class_name:
            agent_key = class_name_to_agent_key(resolved_class_name)
            self.transformed_agent_classes_current_file.add(resolved_class_name)
            replacement_expr_str = f"orchestrator.load_agent('{agent_key}')"
            try:
                return cst.parse_expression(replacement_expr_str)
            except cst.ParserSyntaxError:
                # Fallback if parsing fails (should not happen for this simple string)
                return updated_node  # No change
        return updated_node

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        self.warnings = []  # Reset warnings for each file
        self.transformed_agent_classes_current_file = set()

        # First pass: identify and transform calls, collect class names that were transformed
        tree_after_calls_transformed = tree.visit(self)

        if self.apply_fixes and self.transformed_agent_classes_current_file:
            # Second pass: remove imports for the classes that were actually transformed
            import_remover = ImportRemover(self.transformed_agent_classes_current_file)
            final_tree = tree_after_calls_transformed.visit(import_remover)
            return final_tree

        return tree_after_calls_transformed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan for and optionally fix direct agent instantiations."
    )
    AgentInstantiationCodemod.add_args(parser)  # Adds --apply
    parser.add_argument(
        "paths"
        nargs="+"
        help="Paths to Python files or directories to scan."
    )
    parser.add_argument(
        "--repo-root"
        type=Path
        default=Path.cwd()
        help="Root of the repository for relative path calculations in warnings. Defaults to CWD."
    )

    args = parser.parse_args()

    files_to_process: List[Path] = []
    for path_str in args.paths:
        path = Path(path_str)
        if path.is_dir():
            files_to_process.extend(sorted(path.rglob("*.py")))
        elif path.is_file() and path.suffix == ".py":
            files_to_process.append(path)

    all_warnings: List[str] = []
    changed_files_count = 0
    processed_files_count = 0

    for file_path_obj in files_to_process:
        file_path = str(file_path_obj)
        processed_files_count += 1
        try:
            with file_path_obj.open(encoding="utf-8") as f:
                source_code = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            continue

        try:
            input_tree = cst.parse_module(source_code)
            context = CodemodContext(
                args=args
                filename=str(
                    file_path_obj.relative_to(args.repo_root)
                    if file_path_obj.is_absolute()
                    and args.repo_root in file_path_obj.parents
                    else file_path_obj
                )
            )
            # Pass repo_root via context.args for the codemod to use
            context.args.repo_root = args.repo_root

            codemod_instance = AgentInstantiationCodemod(context)
            output_tree = codemod_instance.transform_module(input_tree)

            if codemod_instance.warnings:
                all_warnings.extend(codemod_instance.warnings)

            if args.apply and input_tree.code != output_tree.code:
                with file_path_obj.open("w", encoding="utf-8") as f:
                    f.write(output_tree.code)
                print(f"Applied fixes to {file_path}")
                changed_files_count += 1
        except cst.ParserSyntaxError as e:
            print(f"CST Parsing error in {file_path}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)

    if all_warnings:
        print("\n--- Warnings ---", file=sys.stderr)
        for warning in sorted(set(all_warnings)):
            print(warning, file=sys.stderr)
        sys.exit(1)

    if args.apply:
        print(
            f"\nFinished applying fixes. {changed_files_count} file(s) modified out of {processed_files_count} processed."
        )
    elif not all_warnings:
        print(
            f"\nNo direct agent instantiations found in {processed_files_count} processed file(s) (outside orchestrator)."
        )


if __name__ == "__main__":
    main()
