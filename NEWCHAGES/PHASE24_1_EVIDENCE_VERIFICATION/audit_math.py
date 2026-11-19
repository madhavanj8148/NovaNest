import pandas as pd

df = pd.read_csv('datasets/cleaned/orders.csv')
diff = df['final_amount'] - (df['order_amount'] + df['delivery_fee'] - df['discount_amount'])
bad = df[diff.abs() > 0.01]
print(f"Total mismatched rows: {len(bad)}")
for idx, r in bad.head(10).iterrows():
    expected = r['order_amount'] + r['delivery_fee'] - r['discount_amount']
    actual = r['final_amount']
    discrepancy = actual - expected
    print(f"Order {r['order_id']}: amount={r['order_amount']}, fee={r['delivery_fee']}, discount={r['discount_amount']} | expected={expected}, actual={actual}, delta={discrepancy}")

print(f"\nAll 67 actual values are: {bad['final_amount'].unique()}")
