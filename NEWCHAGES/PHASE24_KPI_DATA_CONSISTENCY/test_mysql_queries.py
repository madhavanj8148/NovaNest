import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv(".env")
user = os.getenv("DB_APP_USER", "novanest_app")
pwd = os.getenv("DB_APP_PASSWORD", "")
host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", 3306))
dbname = os.getenv("DB_NAME", "novanest_db")

conn = mysql.connector.connect(host=host, port=port, user=user, password=pwd, database=dbname)
cur = conn.cursor()

queries = {
    'KPI-01': "SELECT SUM(order_amount) FROM orders_table WHERE order_status != 'Cancelled';",
    'KPI-02': "SELECT SUM(final_amount) FROM orders_table WHERE order_status = 'Delivered';",
    'KPI-03': "SELECT ROUND(AVG(final_amount), 2) FROM orders_table WHERE order_status = 'Delivered';",
    'KPI-05': "SELECT COUNT(*) FROM orders_table;",
    'KPI-06': "SELECT COUNT(*) FROM orders_table WHERE order_status = 'Delivered';",
    'KPI-07': "SELECT ROUND(100.0 * SUM(CASE WHEN order_status='Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2) FROM orders_table;",
    'KPI-08': "SELECT ROUND(100.0 * SUM(CASE WHEN delivery_duration > 45 THEN 1 ELSE 0 END) / COUNT(*), 2) FROM deliveries;",
    'KPI-09': "SELECT ROUND(AVG(delivery_duration), 2) FROM deliveries;",
    'KPI-10': "SELECT ROUND(COUNT(*) / 4000.0, 2) FROM deliveries;",
    'KPI-11_Registered_1500': "SELECT ROUND(SUM(final_amount) / (SELECT COUNT(*) FROM restaurants), 2) FROM orders_table WHERE order_status = 'Delivered';",
    'KPI-11_Active_1499': "SELECT ROUND(SUM(final_amount) / COUNT(DISTINCT restaurant_id), 2) FROM orders_table WHERE order_status = 'Delivered';",
    'KPI-14': "SELECT ROUND(100.0 * COUNT(CASE WHEN c > 1 THEN 1 END) / COUNT(*), 2) FROM (SELECT customer_id, COUNT(*) AS c FROM orders_table GROUP BY customer_id) sub;",
    'KPI-16': "SELECT ROUND(SUM(final_amount) / 5000.0, 2) FROM orders_table WHERE order_status = 'Delivered';"
}

for k, q in queries.items():
    cur.execute(q)
    print(f"{k}: {cur.fetchone()[0]}")

conn.close()
