import asyncio
import unittest

from legion.agents.echo.run_once import run_once
from tests.stubs.fakeredis_stub import StrictRedis


class FakeSocket:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def send_json(self, msg):
        await self.queue.put(msg)

    async def recv_json(self):
        return await self.queue.get()

    def connect(self, addr):
        pass

    def subscribe(self, *_):
        pass

    def close(self):
        pass


class FakeContext:
    def __init__(self):
        self.socket_obj = FakeSocket()

    def socket(self, _):
        return self.socket_obj


class EchoRunOnceTests(unittest.TestCase):
    def test_message_logged(self):
        ctx = FakeContext()
        redis_client = StrictRedis()

        async def send():
            await asyncio.sleep(0.01)
            await ctx.socket_obj.send_json({"msg": "hi"})

        async def _run():
            task = asyncio.create_task(send())
            await run_once(redis_client=redis_client, context=ctx, sub_addr="stub://")
            await task

        asyncio.get_event_loop().run_until_complete(_run())
        self.assertEqual(len(redis_client.lists.get("echo:log", [])), 1)


if __name__ == "__main__":
    unittest.main()
