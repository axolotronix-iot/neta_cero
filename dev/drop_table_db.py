import psycopg2
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SQL_DIR = BASE_DIR / "sql"
SQL_FILE = SQL_DIR / "drop_table.sql"

def drop_table(sql_file: str):
    with open(sql_file, "r") as f:
        sql = f.read()
    
    conn = psycopg2.connect(
        host="postgres",
        database="iot_db",
        user="iot_user",
        password="iot_password",
        port=5432
    )
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print("Tabla eliminada")

if __name__=="__main__":
    drop_table(SQL_FILE)