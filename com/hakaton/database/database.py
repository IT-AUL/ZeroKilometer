import asyncio

import aiosqlite
from datetime import datetime, timedelta
from random import choice


class DatabaseManager:
    def __init__(self, db_name):
        self.connection = None
        self.db_name = db_name

    async def create_connection(self):
        self.connection = await aiosqlite.connect(self.db_name)

    async def close_connection(self):
        await self.connection.close()

    async def create_table(self):
        await self.connection.execute(f"""
                    CREATE TABLE IF NOT EXISTS players (
                        user_id INTEGER PRIMARY KEY,
                        chapter_id TEXT DEFAULT 'ch0',
                        quest_id TEXT DEFAULT 'q0')
                        """)
        await self.connection.commit()

    async def save(self, user_id, chapter_id, quest_id):
        await self.connection.execute("""
                INSERT INTO players (
                    user_id, 
                    chapter_id, 
                    quest_id)
                    VALUES (?, ?, ?)
                    """, (user_id, chapter_id, quest_id))
        await self.connection.commit()

    async def get(self, user_id):
        async with self.connection.execute("""SELECT * FROM players WHERE user_id=?""", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"chapter_id": row[0], "quest_id": row[1]}
            else:
                return None

