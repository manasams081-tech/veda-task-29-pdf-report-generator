from pathlib import Path
import pandas as pd

print("Checking VEDA Task 29 setup...")
for pkg in ["pandas", "reportlab"]:
    __import__(pkg)
    print(f"[OK] {pkg}")

df = pd.read_csv(Path(__file__).parent / "sample_data.csv")
required = {"date","region","product","customer","quantity","unit_price","revenue"}
missing = required - set(df.columns)
if missing:
    raise SystemExit(f"[FAIL] Missing columns: {sorted(missing)}")
print(f"[OK] Sample CSV loaded: {len(df)} records")
print("[OK] Setup verification passed.")
