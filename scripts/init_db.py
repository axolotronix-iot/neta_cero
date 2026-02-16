import psycopg2
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SQL_DIR = BASE_DIR / "sql"
SQL_FILE = SQL_DIR / "create_table.sql"

print("Archivo de incialización: ", SQL_FILE)

def init_db():
    with open(SQL_FILE, "r") as f:
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
    print("¡Tabla creada!")

if __name__=="__main__":
    init_db()