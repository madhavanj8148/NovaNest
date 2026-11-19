import os
import sys
import json
import sqlite3
import pandas as pd
import numpy as np

def run_consistency_audit():
    data_dir = 'datasets/cleaned'
    tables = {
        'customers': 'customers.csv',
        'restaurants': 'restaurants.csv',
        'riders': 'riders.csv',
        'orders': 'orders.csv',
        'deliveries': 'deliveries.csv',
        'payments': 'payments.csv',
        'ratings_reviews': 'ratings_reviews.csv',
        'menu_items': 'menu_items.csv',
        'promotions': 'promotions.csv',
        'app_events': 'app_events.csv'
    }

    dfs = {}
    print("--- 1. TABLE STATS & DATA QUALITY AUDIT ---")
    total_records = 0
    null_counts = {}
    dup_counts = {}
    for name, file in tables.items():
        path = os.path.join(data_dir, file)
        df = pd.read_csv(path)
        dfs[name] = df
        total_records += len(df)
        null_total = int(df.isnull().sum().sum())
        null_counts[name] = null_total
        dup_total = int(df.duplicated().sum())
        dup_counts[name] = dup_total
        print(f"Table: {name:14} | Rows: {len(df):7} | Cols: {len(df.columns):2} | Nulls: {null_total:3} | Dups: {dup_total:3}")

    print(f"Total Dataset Records: {total_records}")

    print("\n--- 2. REFERENTIAL INTEGRITY AUDIT ---")
    orphan_orders_cust = (~dfs['orders']['customer_id'].isin(dfs['customers']['customer_id'])).sum()
    print(f"Orphan Orders -> Customers: {orphan_orders_cust}")
    orphan_orders_rest = (~dfs['orders']['restaurant_id'].isin(dfs['restaurants']['restaurant_id'])).sum()
    print(f"Orphan Orders -> Restaurants: {orphan_orders_rest}")
    orphan_deliv_orders = (~dfs['deliveries']['order_id'].isin(dfs['orders']['order_id'])).sum()
    print(f"Orphan Deliveries -> Orders: {orphan_deliv_orders}")
    orphan_deliv_riders = (~dfs['deliveries']['rider_id'].isin(dfs['riders']['rider_id'])).sum()
    print(f"Orphan Deliveries -> Riders: {orphan_deliv_riders}")
    orphan_pay_orders = (~dfs['payments']['order_id'].isin(dfs['orders']['order_id'])).sum()
    print(f"Orphan Payments -> Orders: {orphan_pay_orders}")
    orphan_ratings_orders = (~dfs['ratings_reviews']['order_id'].isin(dfs['orders']['order_id'])).sum()
    print(f"Orphan Ratings -> Orders: {orphan_ratings_orders}")
    orphan_menu_rest = (~dfs['menu_items']['restaurant_id'].isin(dfs['restaurants']['restaurant_id'])).sum()
    print(f"Orphan Menu Items -> Restaurants: {orphan_menu_rest}")

    print("\n--- 3. ORDER STATUS BREAKDOWN ---")
    status_counts = dfs['orders']['order_status'].value_counts()
    print(status_counts.to_string())

    print("\n--- 4. FINANCIAL TOTALS & INVARIANT AUDIT ---")
    all_order_amount = dfs['orders']['order_amount'].sum()
    all_final_amount = dfs['orders']['final_amount'].sum()
    deliv_orders = dfs['orders'][dfs['orders']['order_status'] == 'Delivered']
    non_canc_orders = dfs['orders'][dfs['orders']['order_status'] != 'Cancelled']
    canc_orders = dfs['orders'][dfs['orders']['order_status'] == 'Cancelled']
    
    print(f"Gross Placed Value (All Orders order_amount):   INR {all_order_amount:,.2f}")
    print(f"Delivered Food Amount (Delivered order_amount):  INR {deliv_orders['order_amount'].sum():,.2f}")
    print(f"Non-Cancelled Food Amount (KPI-01 GMV):          INR {non_canc_orders['order_amount'].sum():,.2f}")
    print(f"Delivered Final Amount (KPI-02 Net Revenue):     INR {deliv_orders['final_amount'].sum():,.2f}")
    print(f"All Orders Final Amount:                         INR {all_final_amount:,.2f}")
    print(f"Cancelled Food Amount:                           INR {canc_orders['order_amount'].sum():,.2f}")
    print(f"Cancelled Final Amount:                          INR {canc_orders['final_amount'].sum():,.2f}")

    # Minimum payment floor invariant audit
    linear = dfs['orders']['order_amount'] + dfs['orders']['delivery_fee'] - dfs['orders']['discount_amount']
    clamped = linear.clip(lower=50.0)
    floor_diff = dfs['orders']['final_amount'] - linear
    clamped_rows = dfs['orders'][floor_diff != 0]
    is_clamped_valid = np.allclose(dfs['orders']['final_amount'], clamped)

    print(f"\n--- 5. PLATFORM MINIMUM ORDER FLOOR AUDIT (max(50, linear)) ---")
    print(f"Invariant Formula: final_amount = max(50.0, order_amount + delivery_fee - discount_amount)")
    print(f"All 49,971 Orders Adhere to Floor: {is_clamped_valid}")
    print(f"Total Orders Clamped to Floor (< INR 50 linear): {len(clamped_rows)}")
    print(f"  - Delivered Clamped: {len(clamped_rows[clamped_rows['order_status'] == 'Delivered'])}")
    print(f"  - Cancelled Clamped: {len(clamped_rows[clamped_rows['order_status'] == 'Cancelled'])}")
    print(f"Total Retained Cash Adjustment from Floor:       +INR {floor_diff.sum():,.2f}")
    print(f"Delivered Retained Cash Adjustment from Floor:   +INR {(deliv_orders['final_amount'] - (deliv_orders['order_amount'] + deliv_orders['delivery_fee'] - deliv_orders['discount_amount'])).sum():,.2f}")

    print("\n--- 6. RESTAURANT MONETIZATION & REPEAT METRICS ---")
    net_rev = deliv_orders['final_amount'].sum()
    reg_restaurants = len(dfs['restaurants'])
    active_partners = deliv_orders['restaurant_id'].nunique()
    print(f"KPI-11 Avg Revenue per Registered Restaurant (N={reg_restaurants}): INR {net_rev / reg_restaurants:,.2f}")
    print(f"Active Partner Avg Inflow (N={active_partners}):                  INR {net_rev / active_partners:,.2f}")
    print(f"Dormant Partner R00369 Order Count:                             {(dfs['orders']['restaurant_id'] == 'R00369').sum()}")

    cust_order_counts = dfs['orders'].groupby('customer_id').size()
    rep_cust_count = (cust_order_counts > 1).sum()
    tot_cust_count = len(dfs['customers'])
    print(f"KPI-14 Customer Repeat Rate:  {rep_cust_count}/{tot_cust_count} = {rep_cust_count/tot_cust_count*100:.2f}%")
    
    tot_orders_count = len(dfs['orders'])
    repeat_trans_count = tot_orders_count - tot_cust_count
    print(f"Transaction Repeat Order Share: {repeat_trans_count}/{tot_orders_count} = {repeat_trans_count/tot_orders_count*100:.2f}%")

    print("\n--- 7. SQL IN-MEMORY (SQLITE) RECONCILIATION ---")
    conn = sqlite3.connect(':memory:')
    for name, df in dfs.items():
        df.to_sql(name, conn, index=False)

    cur = conn.cursor()
    cur.execute("SELECT SUM(order_amount) FROM orders WHERE order_status != 'Cancelled'")
    sql_gmv = cur.fetchone()[0]
    cur.execute("SELECT SUM(final_amount) FROM orders WHERE order_status = 'Delivered'")
    sql_net_rev = cur.fetchone()[0]
    cur.execute("SELECT ROUND(AVG(final_amount), 2) FROM orders WHERE order_status = 'Delivered'")
    sql_net_aov = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM orders")
    sql_total_orders = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'Delivered'")
    sql_deliv_orders = cur.fetchone()[0]
    cur.execute("SELECT ROUND(100.0 * SUM(CASE WHEN order_status='Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2) FROM orders")
    sql_cancel_rate = cur.fetchone()[0]
    cur.execute("SELECT ROUND(100.0 * SUM(CASE WHEN delivery_duration > 45 THEN 1 ELSE 0 END) / COUNT(*), 2) FROM deliveries")
    sql_sla_breach = cur.fetchone()[0]
    cur.execute("SELECT ROUND(AVG(delivery_duration), 2) FROM deliveries")
    sql_avg_duration = cur.fetchone()[0]
    cur.execute("SELECT ROUND(SUM(final_amount) / (SELECT COUNT(*) FROM restaurants), 2) FROM orders WHERE order_status = 'Delivered'")
    sql_kpi11 = cur.fetchone()[0]

    print(f"SQL KPI-01 GMV:            {sql_gmv} vs {non_canc_orders['order_amount'].sum():.2f}")
    print(f"SQL KPI-02 Net Revenue:    {sql_net_rev} vs {deliv_orders['final_amount'].sum():.2f}")
    print(f"SQL KPI-03 Net AOV:        {sql_net_aov} vs {deliv_orders['final_amount'].mean():.2f}")
    print(f"SQL KPI-05 Total Orders:   {sql_total_orders} vs {len(dfs['orders'])}")
    print(f"SQL KPI-06 Delivered:      {sql_deliv_orders} vs {len(deliv_orders)}")
    print(f"SQL KPI-07 Cancel Rate %:  {sql_cancel_rate}% vs {len(canc_orders)/len(dfs['orders'])*100:.2f}%")
    print(f"SQL KPI-08 SLA Breach %:   {sql_sla_breach}% vs {(dfs['deliveries']['delivery_duration'] > 45).mean()*100:.2f}%")
    print(f"SQL KPI-09 Avg Duration:   {sql_avg_duration} mins vs {dfs['deliveries']['delivery_duration'].mean():.2f} mins")
    print(f"SQL KPI-11 Avg Rev/Rest:   INR {sql_kpi11} vs {net_rev / reg_restaurants:.2f}")

    conn.close()

if __name__ == '__main__':
    run_consistency_audit()
