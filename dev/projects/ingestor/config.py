import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn

# Si existe la variable ENV_FILE en el sistema, úsala. Si no, usa ".env" por defecto.
env_path = os.getenv("ENV_FILE", "/workspace/.env")

class Settings(BaseSettings):
    # MQTT Config
    mqtt_broker: str = Field(alias="MQTT_BROKER")
    mqtt_port: int = Field(default=1883, alias="MQTT_PORT")
    mqtt_topic: str = Field(alias="MQTT_TOPIC")

    # Postgres Config
    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_host: str = Field(alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    # Configuración de Pydantic para leer el archivo .env
    model_config = SettingsConfigDict(
        env_file=env_path, 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

# Instancia global para usar en el proyecto
settings = Settings()