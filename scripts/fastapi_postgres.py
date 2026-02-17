from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
import asyncpg


# ==============================
# Variables de entorno
# ==============================

DB_HOST = "postgres"
DB_USER = "iot_user"
DB_PASSWORD = "iot_password"
DB_NAME = "iot_db"
DB_PORT = 5432

pool: Optional[asyncpg.Pool] = None


# ==============================
# Lifespan (startup / shutdown moderno)
# ==============================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool

    # Startup
    pool = await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        min_size=1,
        max_size=5,
    )

    print("DB pool creado")

    yield

    # Shutdown
    if pool is not None:
        await pool.close()
        print("DB pool terminado")


# 👉 Crear app DESPUÉS de definir lifespan
app = FastAPI(lifespan=lifespan)


# ==============================
# Endpoint: Health check
# ==============================

@app.get("/health")
async def health():
    if pool is None:
        raise HTTPException(status_code=500, detail="Base de datos no inicializada")

    async with pool.acquire() as conn:
        await conn.execute("SELECT 1")

    return {"status": "ok"}


# ==============================
# Endpoint: obtener último registro
# ==============================

@app.get("/latest")
async def get_latest(
    sensor: str = Query(..., description="Nombre del sensor")
):
    if pool is None:
        raise HTTPException(status_code=500, detail="Base de datos no inicializada")

    sensor_clean = sensor.strip()

    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            """
            SELECT id, sensor, value, ts, ts_ingest
            FROM sensor_data
            WHERE sensor = $1
            ORDER BY ts DESC
            LIMIT 1
            """,
            sensor_clean,
        )

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for sensor '{sensor_clean}'"
            )

        return dict(row)


# =====================================
# Endpoint: obtener rango de registros
# =====================================

@app.get("/range")
async def get_range(
    sensor: str = Query(..., description="Nombre del sensor"),
    limit: int = Query(100, ge=1, le=1000),
):
    if pool is None:
        raise HTTPException(status_code=500, detail="Base de datos no inicializada")

    sensor_clean = sensor.strip()

    async with pool.acquire() as connection:
        rows = await connection.fetch(
            """
            SELECT id, sensor, value, ts, ts_ingest
            FROM sensor_data
            WHERE sensor = $1
            ORDER BY ts DESC
            LIMIT $2
            """,
            sensor_clean,
            limit,
        )

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Datos no encontrados para el sensor '{sensor_clean}'"
            )

        # Orden cronológico ascendente (viejo → nuevo)
        result = [dict(r) for r in reversed(rows)]

        return {
            "sensor": sensor_clean,
            "count": len(result),
            "data": result,
        }