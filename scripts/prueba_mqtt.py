import time
import paho.mqtt.client as mqtt

# Usamos la constante de la librería para definir la versión de la API
from paho.mqtt.enums import CallbackAPIVersion

BROKER = "ax-mosquitto"
TOPIC = "test/topic"

# En API v2, los parámetros cambian ligeramente
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Conectado exitosamente")
        client.subscribe(TOPIC)
    else:
        print(f"Error al conectar: {reason_code}")

def on_message(client, userdata, msg):
    print(f"Recibido: {msg.topic} -> {msg.payload.decode()}")

# --- EL CAMBIO PRINCIPAL ESTÁ AQUÍ ---
# Debemos especificar CallbackAPIVersion.VERSION2
client = mqtt.Client(
    callback_api_version=CallbackAPIVersion.VERSION2, 
    client_id="test_client"
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)

client.loop_start()

time.sleep(0.1)
for i in range(1, 6):
    client.publish(TOPIC, f"Hola MQTT {i}")
    #print("Haciendo otras cosas en el script...")
    time.sleep(1)

client.loop_stop()
client.disconnect()
print("Desconectado, script terminado.")