import asyncio
import asyncpg
import json
import time
import random
from datetime import datetime, timezone
from aiomqtt import Client

BROKER = "ax.mosquitto"
TOPIC = "sensor/#"

PG_CONFIG = {
    "host": "postgres",
    "database": "iot_db",
    "user": "iot_user",
    "password": "iot_password",
    "port": 5432,
}

class MQTTIngestor:
    def __init__(self, pg_config):
        self.pg_config = pg_config
        self.pool = None
        self.queue = None

    async def init_db(self):
        try:
            self.pool = await asyncpg.create_pool(
                **self.pg_config,
                min_size=1,
                max_size=5,
                command_timeout=60
            )

            # Validar conexion real
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1;")
                print("DB pool creado correctamente")
        except Exception as e:
            print("Error inicializando DB:", e)
            raise
    
    async def close(self):
        if self.pool:
            await self.pool.close()
            print("DB pool cerrado correctamente")

    async def mqtt_listener(self):
        pass

    async def db_worker(self):
        while True:
            data = await self.queue.get()
            try:
                sensor_id = data["device_id"]
                value = data["value"]
                ts_sensor = datetime.fromtimestamp(data["ts"], tz=timezone.utc)

                async with self.pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO sensor_data (sensor, value, ts)
                        VALUES ($1, $2, $3);
                        """,
                        sensor_id,
                        value,
                        ts_sensor
                    )
            except asyncio.CancelledError:
                print("db_worker cancelado")
                break
            except Exception as e:
                print("Error en db_worker", e)
            finally:
                self.queue.task_done()

    async def run(self):
        self.queue = asyncio.Queue(maxsize=100)

        worker_task = asyncio.create_task(self.db_worker())

        for _ in range(5):
            await self.queue.put({
                "device_id": "device001", 
                "value": round(random.uniform(20.0, 30.0), 2), 
                "ts": int(time.time())
            })
        

        await self.queue.join()

        worker_task.cancel()

        try:
            await worker_task
        except asyncio.CancelledError:
            print("Worker cancelado correctamente")

async def main():
    ingestor = MQTTIngestor(PG_CONFIG)
    await ingestor.init_db()
    await ingestor.run()
    await ingestor.close()

if __name__=="__main__":
    asyncio.run(main())