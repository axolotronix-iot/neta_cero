import psycopg2

conn = psycopg2.connect(
    host="postgres",
    database="iot_db",
    user="iot_user",
    password="iot_password",
    port=5432
)

cur = conn.cursor()
cur.execute("SELECT now();")
print(cur.fetchone())

cur.close()
conn.close()