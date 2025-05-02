import asyncio

import aiosqlite

from ..base import BaseStore

class InMemoryStore(BaseStore):
    def __init__(self):
        super().__init__()
        self.db_path = ":memory:"
        self.lock = asyncio.Lock()

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        task = loop.create_task(self.initialize_db())
        if not loop.is_running():
            loop.run_until_complete(task)
        self.cleanup_task = asyncio.create_task(self.start_cleanup())

    async def initialize_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ttl INTEGER
                )
            ''')
            await db.commit()

    async def set(self, key, value, ttl):
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO cache (key, value, created_at, ttl)
                    VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                ''', (key, value, ttl))
                await db.commit()

    async def get(self, key):
        await self.cleanup()
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('SELECT value FROM cache WHERE key = ?',
                                      (key,)) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else None

    async def rm(self, key):
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('DELETE FROM cache WHERE key = ?', (key,))
                await db.commit()

    async def cleanup(self):
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    DELETE FROM cache
                    WHERE (strftime('%s', 'now') - strftime('%s', created_at)) >= ttl
                ''')
                await db.commit()

    async def start_cleanup(self):
        while True:
            await asyncio.sleep(10)
            await self.cleanup()