import asyncio
from taskiq import AsyncBroker

from .di.container import create_container


async def main():

    container = create_container()

    broker = await container.get(AsyncBroker)

    return broker

broker: AsyncBroker = asyncio.run(main())
