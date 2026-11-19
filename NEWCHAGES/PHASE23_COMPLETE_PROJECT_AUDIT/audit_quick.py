import os
import re
from pathlib import Path

BASE_DIR = Path(r"c:\Users\madha\OneDrive\Documents\NovaNest-main")

def audit_api():
    main_py = BASE_DIR / "api" / "main.py"
    if not main_py.exists():
        print("api/main.py not found")
        return
    text = main_py.read_text(encoding="utf-8")
    routes = re.findall(r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']', text)
    print(f"Total API endpoints defined via @app decorators: {len(routes)}")
    methods = {}
    for m, p in routes:
        methods[m.upper()] = methods.get(m.upper(), 0) + 1
    print("Method distribution:", methods)
    
    # Check CORS
    has_cors = "CORSMiddleware" in text
    cors_origins = re.findall(r'allow_origins\s*=\s*(\[[^\]]+\])', text)
    print(f"CORS configured: {has_cors}, origins: {cors_origins}")

    # Check Auth
    has_jwt = "jwt" in text.lower() or "jose" in text.lower() or "bearer" in text.lower()
    has_api_key = "api_key" in text.lower() or "x-api-key" in text.lower()
    print(f"Auth references in main.py: JWT/Bearer={has_jwt}, API-Key={has_api_key}")

def audit_models():
    models_dir = BASE_DIR / "models"
    if not models_dir.exists():
        print("models/ not found")
        return
    subdirs = [d for d in models_dir.iterdir() if d.is_dir()]
    print(f"\nFound {len(subdirs)} model directories in models/:")
    for d in subdirs:
        files = [f.name for f in d.iterdir()]
        meta_file = d / "metadata_v3.json"
        has_meta = meta_file.exists()
        has_art = any("artifact" in f or f.endswith((".joblib", ".pkl")) for f in files)
        print(f"- {d.name}: {len(files)} files, has_metadata={has_meta}, has_artifact={has_art}")
        if has_meta:
            import json
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                metrics = meta.get("evaluation_metrics", {})
                algo = meta.get("algorithm", "unknown")
                gate = meta.get("operational_confidence_gate", "none")
                print(f"    algo={algo}, gate={gate}, metrics={metrics}")
            except Exception as e:
                print(f"    error reading meta: {e}")

if __name__ == "__main__":
    audit_api()
    audit_models()
