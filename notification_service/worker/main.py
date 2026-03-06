from kafka import KafkaConsumer
from settings import Settings
import time, json
from core.sender import Sender
import asyncio
from aiokafka import AIOKafkaConsumer

settings = Settings()


async def run(consumer: KafkaConsumer, sender: Sender):
    try:
        async for message in consumer:
            print(f"{message.value=}")
            await sender.send(message.value)
    finally:
        await consumer.stop()


async def main():
    sender = Sender()
    consumer = AIOKafkaConsumer(
        "event",
        bootstrap_servers=settings.consumer_server,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset='latest',
        enable_auto_commit=settings.enable_auto_commit,
        group_id=settings.consumer_group,
        consumer_timeout_ms=30000
    )
    await consumer.start()
    while True:
        try:
            await run(consumer=consumer, sender=sender)
        except Exception as e:
            raise e
        finally:
            time.sleep(3)


if __name__ == '__main__':
    asyncio.run(main())
