import sys
from pathlib import Path
sys.path.insert(0, r"c:\Users\madha\OneDrive\Documents\NovaNest-main\python")
from analytics.kpi_engine import compute_all_kpis

df, summary = compute_all_kpis()
out = []
for idx, r in df.iterrows():
    out.append(f"### {r['kpi_id']}: {r['name']}")
    out.append(f"- **Value**: {r['value']} {r['unit']}")
    out.append(f"- **Definition**: {r['business_definition']}")
    out.append(f"- **Formula**: `{r['mathematical_formula']}`")
    out.append(f"- **SQL Equivalent**:\n```sql\n{r['sql_equivalent'].strip()}\n```")
    out.append(f"- **DAX Equivalent**:\n```dax\n{r['dax_equivalent'].strip()}\n```")
    out.append(f"- **Filters**: {r['filters']}")
    out.append(f"- **Notes**: {r['notes']}\n")

with open(r"c:\Users\madha\OneDrive\Documents\NovaNest-main\NEWCHAGES\PHASE24_KPI_DATA_CONSISTENCY\kpi_summary_dump.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Dumped 16 KPIs successfully.")
