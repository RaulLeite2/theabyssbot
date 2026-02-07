"""
Script para executar comandos SQL ou arquivos SQL no banco de dados
Uso: 
  python upload.py "SELECT * FROM users LIMIT 5"
  python upload.py -f db/migration_npc_system.sql
"""
import asyncpg
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

async def execute_query(query: str):
    """Executa uma query SQL no banco de dados"""
    database_url = "postgresql://postgres:evYHCjGIvAJVOmCsDlgqojPGgBuxmoVl@yamanote.proxy.rlwy.net:14445/railway"
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada no arquivo .env")
        print("💡 Adicione DATABASE_URL no arquivo .env com a URL PÚBLICA do banco")
        print("   Exemplo: DATABASE_URL=postgresql://postgres:senha@monorail.proxy.rlwy.net:12345/railway")
        return
    
    # Verifica se está usando URL interna do Railway
    if "railway.internal" in database_url or ".internal" in database_url:
        print("❌ Você está usando a URL INTERNA do Railway!")
        print("💡 Use a URL PÚBLICA do banco de dados para conectar de fora do Railway")
        print("   A URL pública deve ser algo como: postgresql://...@monorail.proxy.rlwy.net:...")
        print("   Você pode encontrar no painel do Railway > PostgreSQL > Connect")
        return
    
    pool = await asyncpg.create_pool(dsn=database_url)
    
    try:
        async with pool.acquire() as conn:
            query_upper = query.strip().upper()
            
            # Detecta tipo de query
            if query_upper.startswith('SELECT') or query_upper.startswith('WITH'):
                # Query de leitura - retorna resultados
                results = await conn.fetch(query)
                
                if not results:
                    print("✅ Query executada com sucesso! (0 resultados)")
                    return
                
                print(f"\n✅ Query executada com sucesso! ({len(results)} resultado(s))\n")
                
                # Exibe resultados
                for i, row in enumerate(results, 1):
                    print(f"[{i}] {dict(row)}")
                
            else:
                # Query de modificação/DDL
                result = await conn.execute(query)
                print(f"✅ Query executada com sucesso!")
                print(f"📊 Resultado: {result}")
                    
    except Exception as e:
        print(f"❌ Erro ao executar query:")
        print(f"   {type(e).__name__}: {e}")
        
    finally:
        await pool.close()


async def execute_file(file_path: str):
    """Executa um arquivo SQL no banco de dados"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada no arquivo .env")
        return
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
    
    print(f"📁 Lendo arquivo: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    pool = await asyncpg.create_pool(dsn=database_url)
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(sql)
            print(f"✅ Arquivo {file_path} executado com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao executar arquivo:")
        print(f"   {type(e).__name__}: {e}")
        
    finally:
        await pool.close()


def show_help():
    """Mostra ajuda do comando"""
    help_text = """
╔═══════════════════════════════════════════════════════════╗
║         Upload.py - Executor de Comandos SQL              ║
╚═══════════════════════════════════════════════════════════╝

📖 USO:
  python upload.py "<query>"              # Executa uma query SQL
  python upload.py -f <arquivo.sql>       # Executa um arquivo SQL
  python upload.py --help                 # Mostra esta ajuda

📝 EXEMPLOS:

  # Ver usuários
  python upload.py "SELECT * FROM users LIMIT 5"

  # Ver hubs
  python upload.py "SELECT nome, tier, is_hub FROM zone WHERE is_hub = TRUE"

  # Adicionar ouro
  python upload.py "UPDATE economy SET gold = gold + 10000 WHERE user_id = 123456789"

  # Executar migration
  python upload.py -f db/migration_npc_system.sql

🔗 DATABASE_URL: Carregada automaticamente do arquivo .env
"""
    print(help_text)


def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python upload.py \"<query>\" ou python upload.py <arquivo.sql>")
        print("💡 Use --help para mais informações")
        return
    
    # Verifica flag de ajuda
    if sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
        return
    
    # Verifica flag de arquivo
    if sys.argv[1] in ['-f', '--file']:
        if len(sys.argv) < 3:
            print("❌ Especifique o arquivo: python upload.py -f <arquivo.sql>")
            return
        asyncio.run(execute_file(sys.argv[2]))
        return
    
    # Detecta automaticamente se é um arquivo .sql
    arg = sys.argv[1]
    if arg.endswith('.sql') or '\\' in arg or '/' in arg:
        # Provavelmente é um caminho de arquivo
        asyncio.run(execute_file(arg))
        return
    
    # Executa query
    query = sys.argv[1]
    asyncio.run(execute_query(query))


if __name__ == "__main__":
    main()