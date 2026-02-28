import asyncio
import asyncpg
import json
import time
from datetime import datetime, timezone
from aiomqtt import Client
from env_manager import settings


class MQTTIngestor:
    """
    Consumidor asíncrono para ingesta de datos MQTT en PostgreSQL.

    Esta clase gestiona la conexión a un broker MQTT, escucha tópicos específicos,
    y utiliza una cola interna (asyncio.Queue) para procesar e insertar los 
    datos de manera eficiente en una base de datos PostgreSQL.

    Attributes:
        config (Settings): Configuración de conexión para asyncpg.
        pool (asyncpg.pool.Pool): Pool de conexiones a la base de datos.
        queue (asyncio.Queue): Cola para comunicación entre el listener y el worker.
    """    
    def __init__(self, config=settings):
        """
        Inicializa el ingestor con la configuración de la base de datos.

        Args:
            config (Settings): Instancia de Pydantic con la configuración cargada.
        """
        self.config = config
        self.pool = None
        self.queue = None

    async def init_db(self, retries: int = 5, delay: int = 5):
        """
        Crea y valida el pool de conexiones a PostgreSQL.

        Establece un pool de conexiones persistentes (asyncpg) y ejecuta una 
        consulta de prueba (SELECT 1) para asegurar que el acceso está disponible.

        Raises:
            Exception: Si la conexión a la base de datos falla durante la inicialización.
        """
        for i in range(retries):
            try:
                self.pool = await asyncpg.create_pool(
                    user=self.config.postgres_user,
                    password=self.config.postgres_password,
                    database=self.config.postgres_db,
                    host=self.config.postgres_host,
                    port=self.config.postgres_port,
                    min_size=1,
                    max_size=5,
                    command_timeout=60
                )

                # Validar conexion real
                async with self.pool.acquire() as conn:
                    await conn.execute("SELECT 1;")
                    print(f"[Init DB] DB pool creado correctamente al intento {i+1}")
                    return # Éxito, salimos del metodo
            except Exception as e:
                print(f"[Init DB] Intento {i+1}/{retries} fallido. DB no lista: {e}")
                if i < retries - 1:
                    await asyncio.sleep(delay)
                else:
                    print("[Init DB] No se pudo conectar a la DB tras varios intentos.")
                    raise        
    
    async def close_db(self):
        """
        Cierra de forma segura el pool de conexiones de la base de datos.

        Se debe llamar al finalizar la aplicación para liberar correctamente 
        los recursos del servidor PostgreSQL.
        """
        if self.pool:
            await self.pool.close()
            print("[Close DB] DB pool cerrado correctamente")

    async def mqtt_listener(self, reconnect_interval: int = 5, max_reconnect_interval: int = 60):
        """
        Gestiona la conexión con el Broker MQTT y la escucha de mensajes.

        Mantiene un bucle infinito con lógica de reconexión exponencial. Suscribe 
        al cliente al tópico configurado, procesa los mensajes entrantes mediante 
        el parser y los añade a la cola interna de procesamiento.

        Args:
            reconnect_interval (int): Tiempo inicial de espera en segundos tras un fallo.
            max_reconnect_interval (int): Tiempo máximo permitido entre intentos de reconexión.

        Raises:
            asyncio.CancelledError: Si la tarea es cancelada durante el apagado del sistema.
        """
        interval = reconnect_interval
        while True:
            try:
                print(f"[MQTT Listener] Conectando al broker: {self.config.mqtt_broker}...")
                async with Client(
                    self.config.mqtt_broker,
                    port=self.config.mqtt_port
                ) as client:
                    print(f"[MQTT Listener] Conectado exitosamente a {self.config.mqtt_broker}")

                    # Suscripción al tópico (usando # para capturar todo)
                    await client.subscribe(self.config.mqtt_topic)
                    print(f"[MQTT Listener] Suscrito a {self.config.mqtt_topic}")

                    # En las versiones nuevas de aiomqtt, simplemente iteras sobre el cliente
                    async for message in client.messages:
                        # 1. Pasamos el mensaje por el parser
                        clear_data = self.parse_message(
                            str(message.topic),
                            message.payload
                        )
                        # 2. Si es valido, lo metemos a la cola
                        if clear_data:
                            try:
                                self.queue.put_nowait(clear_data) # No espera si la cola esta llena, descarta el mensaje
                            except asyncio.QueueFull:
                                print(f"[MQTT Listener] Cola llena, mensaje descartado: {clear_data['device_id']}")

            except asyncio.CancelledError:
                print("[MQTT Listener] Cancelado, saliendo...")
                # Importante: Permitir que la cancelación suba
                raise
            except Exception as e:
                print(f"[MQTT Listener] Error de conexión MQTT: {e}. Reintentando en {interval}s...")
                await asyncio.sleep(interval)
                interval = min(2 * interval, max_reconnect_interval) # Espera exponencial: 2^1 * interval

    async def db_worker(self):
        """
        Consumidor asíncrono que persiste los datos de la cola en la base de datos.

        Extrae mensajes de la cola interna de forma secuencial. Incluye una lógica 
        de reintentos (backoff simple) para manejar fallos temporales de escritura 
        en la base de datos antes de marcar la tarea como completada.

        Note:
            Este método se ejecuta como una tarea de fondo (background task).
        """
        while True:
            data = await self.queue.get()
            try:
                # Ya no validamos llaves aquí, parse_message lo hizo antes.
                sensor_id = data["device_id"]
                value = data["value"]
                ts_sensor = datetime.fromtimestamp(data["ts"], tz=timezone.utc)

                # logica de reintento simple
                attempts = 0
                max_attempts = 3
                while attempts < max_attempts:
                    try:
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
                        break # Éxito, salimos del bucle de reintento
                    except Exception as e:
                        attempts += 1
                        print(f"[DB Worker] Intento {attempts}/{max_attempts}, error en DB: {e}")
                        await asyncio.sleep(1 * attempts) # Espera exponencial simple

                if attempts == max_attempts:
                    print(f"[DB Worker] No se pudo insertar dato después de {max_attempts} intentos.")

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[DB Worker] Error inesperado: {e}")
            finally:
                self.queue.task_done()

    def parse_message(self, topic: str, payload_bytes: bytes) -> dict | None:
        """
        Limpia, valida y normaliza los mensajes MQTT entrantes.

        Convierte el payload de bytes a JSON y extrae metadatos (device_id, metric).
        Si el payload está incompleto, intenta inferir la información a partir de 
        la estructura del tópico (sensor/<metric>/<device_id>).

        Args:
            topic (str): El tópico completo donde se recibió el mensaje.
            payload_bytes (bytes): El cuerpo del mensaje recibido del broker.

        Returns:
            dict | None: Un diccionario estandarizado con keys ['device_id', 'metric', 
                'value', 'ts', 'raw_topic'] o None si el mensaje es inválido.
        """
        try:
            # 1. Decodificación
            payload = json.loads(payload_bytes.decode("utf-8"))

            # 2. Segmentación del tópico
            parts = topic.split("/") # Ej: ["sensor", "temperature", "device001"]

            # 3. Extracción con "Fallback" (Si no esta en el JSON, lo saca del tópico)
            # Ej. Para "sensor/temperature/device001":
            # parts[1] es 'temperature' (metric)
            # parts[2] es 'device001' (device_id)
            device_id = payload.get("device_id")
            if not device_id:
                device_id = parts[2] if len(parts) >= 3 else "unknown_device"

            metric = payload.get("metric")
            if not metric:
                metric = parts[1] if len (parts) >= 2 else "unknown_metric"

            # 4. Validación de Valor (Obligatorio)
            if "value" not in payload:
                print(f"[Parser] Mensaje sin 'value' en {topic}")
                return None
            val_numeric = float(payload["value"])

            # 5. Validación de Timestamp (Resiliente)
            try:
                ts_raw = payload.get("ts")
                ts_final = int(ts_raw) if ts_raw is not None else int(time.time())
            except (ValueError, TypeError):
                ts_final = int(time.time())
                print(f"[Parser] TS inválido en {topic}, usando tiempo local.")

            # 6. Return consistente
            return {
                "device_id": str(device_id),
                "metric": str(metric),
                "value": val_numeric,
                "ts": ts_final,
                "raw_topic": topic
            }

        except Exception as e:
            print(f"[Parser] Fallo inesperado: {e}")
            return None


    async def run(self):
        """
        Orquestador principal que inicia el ciclo de vida del ingestor.

        Inicializa la cola interna de asyncio, lanza el trabajador de base de datos 
        como una tarea concurrente y bloquea la ejecución con el listener de MQTT. 
        Gestiona la limpieza y cancelación de tareas al recibir una interrupción.
        """
        # Inicialización de la cola
        self.queue = asyncio.Queue(maxsize=100)

        # 1. DB Worker como tarea de fondo
        worker_task = asyncio.create_task(self.db_worker())

        # 2. Ejecución del listener (se bloquea escuchando)
        try:
            await self.mqtt_listener()
        except (asyncio.CancelledError, KeyboardInterrupt):
            print("[Runner] Finalizado por el usuario...")
        finally:
            # 3. Limpieza al salir
            worker_task.cancel()
            await asyncio.gather(worker_task, return_exceptions=True)
            print("[Runner] Ingestor detenido exitosamente.")