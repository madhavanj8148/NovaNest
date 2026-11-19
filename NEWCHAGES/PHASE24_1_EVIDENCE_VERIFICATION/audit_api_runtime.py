import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

token = os.getenv("NOVANEST_API_KEY") or os.getenv("NOVANEST_ADMIN_KEY")
headers = {"X-API-Key": token}

endpoints = [
    ("/api/overview", "Executive Overview", {"city": "All"}),
    ("/api/overview?city=Bangalore", "Overview (Bangalore)", {"city": "Bangalore"}),
    ("/api/overview?city=Chennai", "Overview (Chennai)", {"city": "Chennai"}),
    ("/api/financial/overview", "Financial Overview", {"city": "All"}),
    ("/api/operations/overview", "Operations Overview", {"city": "All"}),
    ("/api/customer/overview", "Customer Overview", {"city": "All"}),
    ("/api/restaurant/overview", "Restaurant Overview", {"city": "All"})
]

print("=== FASTAPI IN-PROCESS TESTCLIENT RUNTIME AUDIT ===")
for path, label, params in endpoints:
    resp = client.get(path, headers=headers)
    print(f"\nEndpoint: {path} | Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        if "kpi_cards" in data:
            cards = data["kpi_cards"]
            gmv = cards.get("total_gmv", {}).get("value")
            rev = cards.get("net_platform_revenue", {}).get("value")
            orders = cards.get("total_orders", {}).get("value")
            deliv = cards.get("delivered_orders", {}).get("value")
            aov = cards.get("avg_order_value", {}).get("value")
            margin = cards.get("contribution_margin", {}).get("value")
            print(f"  [{label}] GMV: {gmv} | Net Rev: {rev} | Orders: {orders} | Deliv: {deliv} | AOV: {aov} | Margin%: {margin}")
        elif "metrics" in data:
            m = data["metrics"]
            print(f"  [{label}] Metrics: {m}")
        elif "summary_cards" in data:
            print(f"  [{label}] Summary cards: {data['summary_cards']}")
        else:
            print(f"  [{label}] Keys: {list(data.keys())[:8]}")
    else:
        print(f"  Response text: {resp.text[:200]}")
