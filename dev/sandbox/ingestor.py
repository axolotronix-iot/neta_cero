import asyncio
import json
from aiomqtt import Client
from datetime import datetime
from pathlib import Path
from datetime import datetime, timezone

#===============================
# Configuración
#===============================

BROKER = "ax-mosquitto"
TOPIC = "sensors/#"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STORAGE_FILE = DATA_DIR / "events.json"

print("Ruta almacenamiento:", DATA_DIR)
print("Archivo de almacenamiento:", STORAGE_FILE)

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
        if "device_id" not in payload or "value" not in payload:
            print("Payload invalido", payload)
            return
        
        payload["ingested_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        print("Mensaje recibido:", payload)

        await save_to_file(payload)

    except json.JSONDecodeError:
        print("Error: payload no es un JSON valido")
    except Exception as e:
        print("Error procesando mensaje:", e)

#===============================
# Función para guardar los datos
#===============================

async def save_to_file(data):
    try:

        # Crear carpeta si no existe
        DATA_DIR.mkdir(exist_ok=True)

        # Modo append: crea archivo si no existe
        with open(STORAGE_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")

    except Exception as e:
        print("Error guardando archivo:", e)

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
            print("Worken cancelado correctamente.")
            raise

#===============================
# Entrada del programa
#===============================

if __name__=="__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Ingestor detenido correctamente.")