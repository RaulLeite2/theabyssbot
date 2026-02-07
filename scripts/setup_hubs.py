"""
Script para criar hubs de exemplo

Nota: As migrations foram consolidadas em db/schema.sql
Certifique-se de que o schema está aplicado ao banco antes de executar este script.
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada! Verifique seu arquivo .env")
        return
    
    pool = await asyncpg.create_pool(dsn=DATABASE_URL)
    
    try:
        print("ℹ️  Verificando schema...")
        
        async with pool.acquire() as conn:
            # Verifica se a tabela zone existe
            zone_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'zone'
                )
            """)
            
            if not zone_exists:
                print("""
                ❌ Tabela 'zone' não encontrada!
                
                Execute db/schema.sql no seu banco de dados antes de usar este script:
                    psql -U seu_usuario -h seu_host -d sua_database -f db/schema.sql
                """)
                return
            
            print("✅ Schema validado!\n")
            
            # Verifica items
            result = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_items,
                    SUM(CASE WHEN is_collectible THEN 1 ELSE 0 END) as collectible_items,
                    SUM(CASE WHEN NOT is_collectible THEN 1 ELSE 0 END) as regular_items
                FROM items
            """)
            
            print(f"📊 Total de items: {result['total_items']}")
            print(f"📦 Items coletáveis: {result['collectible_items']}")
            print(f"⚔️ Items regulares: {result['regular_items']}")
            
            print("\n🏛️ Criando Hubs de exemplo...")
            
            # Cria hubs se não existirem
            hubs = [
                ("Capital do Abismo", 1, True),
                ("Cidade de Ferro", 3, True),
                ("Citadela Celestial", 5, True),
            ]
            
            hubs_created = 0
            for hub_name, tier, is_hub in hubs:
                # Verifica se já existe
                exists = await conn.fetchval(
                    "SELECT 1 FROM zone WHERE nome = $1",
                    hub_name
                )
                
                if not exists:
                    await conn.execute(
                        """
                        INSERT INTO zone (nome, tier, is_hub, is_hideout, permanent)
                        VALUES ($1, $2, $3, FALSE, TRUE)
                        """,
                        hub_name, tier, is_hub
                    )
                    hubs_created += 1
                    print(f"  ✅ Hub criado: {hub_name} (Tier {tier})")
                else:
                    print(f"  ⚠️ Hub já existe: {hub_name}")
            
            if hubs_created > 0:
                print(f"\n✨ {hubs_created} hub(s) criado(s) com sucesso!")
            else:
                print("\n✨ Todos os hubs já existem!")
            
            # Lista todos os hubs
            hubs_list = await conn.fetch(
                """
                SELECT zone_id, nome, tier
                FROM zone
                WHERE is_hub = TRUE
                ORDER BY tier ASC
                """
            )
            
            print(f"\n🏛️ Hubs disponíveis ({len(hubs_list)}):")
            for hub in hubs_list:
                print(f"  • {hub['nome']} (Tier {hub['tier']}) - ID: {hub['zone_id']}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        await pool.close()
        print("\n✅ Concluído!")

if __name__ == "__main__":
    asyncio.run(main())
