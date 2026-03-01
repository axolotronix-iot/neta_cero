import asyncio
from engine import MQTTIngestor

async def main():
    ingestor = MQTTIngestor()
    try:
        await ingestor.init_db()
        await ingestor.run()
    except Exception as e:
        print(f"Error fatal: {e}")
    finally:
        await ingestor.close_db()

if __name__=="__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass