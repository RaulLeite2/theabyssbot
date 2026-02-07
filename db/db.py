import asyncpg
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

# Railway usa DATABASE_URL, dev local usa variáveis individuais
DATABASE_URL = os.getenv("DATABASE_URL")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

class Database:
    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    # =========================
    # CONNECTION
    # =========================
    async def connect(self):
        import asyncio
        max_retries = 5
        retry_delay = 2  # segundos
        
        for attempt in range(1, max_retries + 1):
            try:
                # Prioriza DATABASE_URL (Railway/produção)
                if DATABASE_URL:
                    print(f"[Tentativa {attempt}/{max_retries}] Conectando via DATABASE_URL...")
                    self.pool = await asyncpg.create_pool(
                        dsn=DATABASE_URL,
                        min_size=1,
                        max_size=10
                    )
                    print(f"✅ Conexão estabelecida via DATABASE_URL!")
                    return
                else:
                    # Fallback para variáveis individuais (desenvolvimento local)
                    print(f"[Tentativa {attempt}/{max_retries}] Conectando via DB_USER, DB_HOST...")
                    self.pool = await asyncpg.create_pool(
                        user=DB_USER,
                        password=DB_PASSWORD,
                        database=DB_NAME,
                        host=DB_HOST,
                        port=5432,
                        min_size=1,
                        max_size=10
                    )
                    print(f"✅ Conexão estabelecida via variáveis individuais!")
                    return
                    
            except Exception as e:
                print(f"❌ Tentativa {attempt}/{max_retries} falhou: {e}")
                if attempt < max_retries:
                    print(f"⏳ Aguardando {retry_delay} segundos antes da próxima tentativa...")
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"❌ Falha após {max_retries} tentativas. Verifique:")
                    if DATABASE_URL:
                        print(f"   - DATABASE_URL está correta?")
                        print(f"   - PostgreSQL está rodando no Railway?")
                    else:
                        print(f"   - DB_USER: {DB_USER}")
                        print(f"   - DB_HOST: {DB_HOST}")
                        print(f"   - DB_NAME: {DB_NAME}")
                        print(f"   - PostgreSQL está instalado e rodando?")
                    raise

    async def close(self):
        if self.pool:
            await self.pool.close()

    # =========================
    # LOW LEVEL ACCESS
    # =========================
    @asynccontextmanager
    async def acquire(self):
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        async with self.pool.acquire() as conn:
            yield conn

    # =========================
    # EXECUTION HELPERS
    # =========================
    async def execute(self, sql, *args):
        async with self.acquire() as conn:
            await conn.execute(sql, *args)

    async def file_execute(self, file, *args):
        with open(file, "r", encoding="utf-8") as f:
            sql = f.read()

        async with self.acquire() as conn:
            await conn.execute(sql, *args)

    async def fetchrow(self, sql, *args):
        async with self.acquire() as conn:
            return await conn.fetchrow(sql, *args)

    async def fetch(self, sql, *args):
        async with self.acquire() as conn:
            return await conn.fetch(sql, *args)

    async def fetchval(self, sql, *args):
        async with self.acquire() as conn:
            return await conn.fetchval(sql, *args)

    # =========================
    # TRANSACTIONS
    # =========================
    @asynccontextmanager
    async def transaction(self):
        async with self.acquire() as conn:
            async with conn.transaction():
                yield conn

    @asynccontextmanager
    async def nested_transaction(self, conn):
        async with conn.transaction():
            yield conn
    
    @asynccontextmanager
    async def savepoint(self, conn):
        async with conn.transaction():
            yield conn