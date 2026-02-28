import time
from ingestor.config import Settings

print("Ingestor iniciado correctamente")
print("Base de datos en:", Settings.DATABASE_URL)

while True:
    time.sleep(10)
    print("Ingestor sigue vivo...")