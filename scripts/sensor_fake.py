import asyncio
import json
import random
import time
from aiomqtt import Client

BROKER = "ax-mosquitto"
TOPIC = "sensors/temperature/device001"

async def main():
    async with Client(BROKER) as client:
        print(f"Sensor fake conectado al broker: {BROKER}")

        while True:
            payload = {
                "device_id": "device001",
                "ts": int(time.time()),
                "value": round(random.uniform(20.0, 30.0), 2)
            }

            await client.publish(TOPIC, json.dumps(payload))
            print("Publicado:", payload)

            await asyncio.sleep(20)

if __name__=="__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSensor detenido manualmente.")