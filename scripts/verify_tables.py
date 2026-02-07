import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_tables():
    DATABASE_URL = os.getenv("DATABASE_URL")
    pool = await asyncpg.create_pool(dsn=DATABASE_URL)
    
    try:
        async with pool.acquire() as conn:
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('achievements', 'user_achievements', 'daily_quests', 
                                   'user_daily_quests', 'user_fortune', 'user_stats')
                ORDER BY table_name
            """)
            
            print("✅ Tabelas criadas:")
            for table in tables:
                print(f"  - {table['table_name']}")
            
            print(f"\n📊 Total: {len(tables)}/6 tabelas")
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(verify_tables())
