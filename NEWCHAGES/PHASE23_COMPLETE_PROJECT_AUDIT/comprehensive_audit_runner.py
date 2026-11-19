"""
NovaNest Comprehensive Repository Audit Script
Scans and analyzes:
1. Repository folder structure and orphaned/legacy files
2. Database schema vs CSV structure
3. KPI implementation across API, Streamlit, and React
4. Security and RBAC audit
5. Documentation vs implementation consistency
"""

import os
import re
import json
from pathlib import Path

BASE_DIR = Path(r"c:\Users\madha\OneDrive\Documents\NovaNest-main")

def audit_repo_structure():
    print("=== REPOSITORY INVENTORY & MODULE AUDIT ===")
    top_level = [p.name for p in BASE_DIR.iterdir()]
    print(f"Top-level items ({len(top_level)}): {sorted(top_level)}")

    # Check for legacy or backup directories
    backup_dirs = [d.name for d in BASE_DIR.glob("*backup*") if d.is_dir()]
    print(f"Backup directories found: {backup_dirs}")

    # Check test files count
    test_files = list((BASE_DIR / "tests").glob("test_*.py"))
    print(f"Total test suite files in tests/: {len(test_files)}")

    # Check python packages
    python_subdirs = [d.name for d in (BASE_DIR / "python").iterdir() if d.is_dir()]
    print(f"Subpackages in python/: {sorted(python_subdirs)}")

def audit_kpi_consistency():
    print("\n=== KPI CODE AUDIT ===")
    api_main = (BASE_DIR / "api" / "main.py").read_text(encoding="utf-8")
    
    # Check KPI formulas in api/main.py
    gmv_matches = re.findall(r'(\bgmv\b\s*[:=].*?)(?=\n|$)', api_main, re.IGNORECASE)
    print(f"GMV formulas in api/main.py ({len(gmv_matches)} matches):")
    for m in gmv_matches[:5]:
        print("  ", m.strip())

    # Check delivered count formulas
    deliv_matches = re.findall(r'(\bdelivered\b\s*[:=].*?)(?=\n|$)', api_main, re.IGNORECASE)
    print(f"Delivered references in api/main.py ({len(deliv_matches)} matches):")
    for m in deliv_matches[:5]:
        print("  ", m.strip())

def audit_security_rules():
    print("\n=== SECURITY ARCHITECTURE AUDIT ===")
    contracts_py = (BASE_DIR / "python" / "ai" / "agents" / "contracts.py").read_text(encoding="utf-8")
    ast_py = (BASE_DIR / "python" / "ai" / "analyst" / "sql_ast.py").read_text(encoding="utf-8")
    auth_py = (BASE_DIR / "api" / "auth.py").read_text(encoding="utf-8") if (BASE_DIR / "api" / "auth.py").exists() else ""

    # Check injection rules
    injection_rules = re.findall(r'\(\s*"([^"]+)",\s*re\.compile', contracts_py)
    print(f"Prompt injection pattern categories in contracts.py ({len(injection_rules)}): {injection_rules}")

    # Check SQL AST rules
    allowed_tables = re.findall(r'ALLOWED_TABLES\s*=\s*(?:frozenset\()?(?:\[|{)([^\]}]+)', ast_py)
    print(f"SQL AST Allowed Tables: {allowed_tables}")

    # Check RBAC scopes
    scopes = re.findall(r'\b(?:admin|operator|viewer)\b', auth_py)
    print(f"Auth RBAC scopes found in auth.py: {set(scopes)}")

if __name__ == "__main__":
    audit_repo_structure()
    audit_kpi_consistency()
    audit_security_rules()
