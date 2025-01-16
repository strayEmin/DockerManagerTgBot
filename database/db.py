import aiosqlite

DATABASE = "database/users.sqlite"

# Функция для создания таблицы, если она не существует
async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT NOT NULL,
            ip TEXT NOT NULL,
            PRIMARY KEY (id, ip)
        )
        """)
        await db.commit()


async def add_user_ip(user_id: str, ip: str):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
        INSERT OR IGNORE INTO users (id, ip) VALUES (?, ?)
        """, (user_id, ip))
        await db.commit()


async def get_ips_by_user_id(user_id: str):
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("""
        SELECT ip FROM users WHERE id = ?
        """, (user_id,))
        ips = await cursor.fetchall()
        return [row[0] for row in ips]


async def check_user_ip(user_id: str, ip: str) -> bool:
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("""
        SELECT 1 FROM users WHERE id = ? AND ip = ?
        """, (user_id, ip))
        result = await cursor.fetchone()
        return result is not None


async def delete_user_ip(user_id: str, ip: str):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
        DELETE FROM users WHERE id = ? AND ip = ?
        """, (user_id, ip))
        await db.commit()

# async def main():
#     await init_db()
#
#     await add_user_ip("user1", "192.168.0.1")
#     await add_user_ip("user1", "192.168.0.2")
#     await add_user_ip("user2", "10.0.0.1")
#
#     user1_ips = await get_ips_by_user_id("user1")
#     print(f"IP-адреса пользователя user1: {user1_ips}")
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
