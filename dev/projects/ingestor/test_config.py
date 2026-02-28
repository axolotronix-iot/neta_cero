from config import settings

try:
    print(f"Conectando a MQTT en: {settings.mqtt_broker}:{settings.mqtt_port}")
    print(f"Base de datos: {settings.postgres_db} en {settings.postgres_host}")
    print("¡Configuración cargada y validada exitosamente!")
except Exception as e:
    print(f"Error en la configuración: {e}")