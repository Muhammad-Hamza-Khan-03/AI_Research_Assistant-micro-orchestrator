from redis.asyncio import Redis
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

r = Redis.from_url(os.getenv("REDIS_URI"))
async def test():
    await r.set("test_key", "hello async redis")
    v = await r.get("test_key")
    print("Async Redis OK:", v.decode())

asyncio.run(test())