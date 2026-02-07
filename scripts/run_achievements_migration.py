import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    """
    ⚠️ DEPRECATED: Esta script não é mais necessária.
    
    Todas as migrations foram consolidadas no arquivo db/schema.sql
    Execute o script direto no banco de dados alternativamente.
    
    Para aplicar o schema completo, conecte ao banco e execute:
        psql -U usuario -h host -d database -f db/schema.sql
    """
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada!")
        return
    
    print("""
    ⚠️  Script Descontinuado
    
    As migrations foram consolidadas no arquivo: db/schema.sql
    
    Para aplicar o schema completo:
    1. Todas as tabelas, funções e dados iniciais estão em db/schema.sql
    2. Execute o schema.sql no seu banco PostgreSQL
    
    Exemplo:
        psql -U seu_usuario -h seu_host -d sua_database -f db/schema.sql
    """)
    
    print("✅ Schema consolidado com sucesso!")

if __name__ == "__main__":
    asyncio.run(run_migration())
