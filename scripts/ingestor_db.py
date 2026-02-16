import asyncio
import json
import psycopg2
from aiomqtt import Client
from datetime import datetime
from pathlib import Path
from datetime import datetime, timezone

#===============================
# Configuración
#===============================

BROKER = "ax-mosquitto"
TOPIC = "sensors/#"

PG_HOST = "postgres"
PG_DB = "iot_db"
PG_USER = "iot_user"
PG_PASS = "iot_password"
PG_PORT = 5432

#======================================
# Función para guardar en PostgreSQL
#======================================
def save_to_db(sensor_id: str, value: float, ts: int):
    try:
        ts_sensor = datetime.fromtimestamp(ts, tz=timezone.utc)

        conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASS,
            port=PG_PORT
        )
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO sensor_data (sensor, value, ts)
            VALUES (%s, %s, %s)
            RETURNING id, ts, ts_ingest;
            """,
            (sensor_id, value, ts_sensor)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        print(f"Insertado registro: id={row[0]}, ts_sensor={row[1]}, ts_ingest={row[2]}")
    except Exception as e:
        print("Error guardando en DB:", e)

#===============================
# Lógica de procesamiento
#===============================

async def handle_message(message):
    try:

        payload = json.loads(message.payload.decode())

        # Validación mínima
        if not isinstance(payload, dict):
            print("Payload no es dict:", payload)
            return
        if "device_id" not in payload or "value" not in payload or "ts" not in payload:
            print("Payload invalido", payload)
            return

        print("Mensaje recibido:", payload)

        save_to_db(payload["device_id"], float(payload["value"]), int(payload["ts"]))

    except json.JSONDecodeError:
        print("Error: payload no es un JSON valido")
    except Exception as e:
        print("Error procesando mensaje:", e)

#===============================
# Worker principal
#===============================

async def main():
    async with Client(BROKER) as client:
        await client.subscribe(TOPIC)
        print(f"Suscrito a {TOPIC}")

        try:
            async for message in client.messages:
                await handle_message(message)
        except asyncio.CancelledError:
            print("\nWorken cancelado correctamente.")
            raise

#===============================
# Entrada del programa
#===============================

if __name__=="__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Ingestor detenido correctamente.")