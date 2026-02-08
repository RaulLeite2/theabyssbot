"""
Script para executar a migration: adicionar colunas depth_new e quality_new
"""
import os
import sys
import asyncio
import asyncpg
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada no .env")
    sys.exit(1)

async def run_migration():
    """Executa a migration para adicionar depth_new e quality_new"""
    
    migration_file = Path("db/migrations/add_depth_quality_columns.sql")
    
    if not migration_file.exists():
        print(f"❌ Arquivo de migration não encontrado: {migration_file}")
        sys.exit(1)
    
    print(f"📖 Lendo migration: {migration_file}")
    migration_sql = migration_file.read_text(encoding="utf-8")
    
    print("🔌 Conectando ao banco de dados...")
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("⚙️ Executando migration...")
        
        # Executa a migration (pode retornar múltiplos resultados devido aos RAISE NOTICE)
        await conn.execute(migration_sql)
        
        print("\n✅ Migration executada com sucesso!")
        
        # Verifica os resultados
        print("\n📊 Verificando resultados...")
        
        # Verifica se as colunas existem
        columns_check = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'items' 
            AND column_name IN ('depth_new', 'quality_new')
            ORDER BY column_name
        """)
        
        print("\n✅ Colunas criadas:")
        for col in columns_check:
            print(f"   - {col['column_name']}: {col['data_type']}")
        
        # Conta itens com depth_new e quality_new
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_items,
                COUNT(depth_new) as items_with_depth,
                COUNT(quality_new) as items_with_quality
            FROM items
        """)
        
        print(f"\n📈 Estatísticas:")
        print(f"   - Total de itens: {stats['total_items']}")
        print(f"   - Itens com depth_new: {stats['items_with_depth']}")
        print(f"   - Itens com quality_new: {stats['items_with_quality']}")
        
        # Mostra distribuição de depth
        depth_dist = await conn.fetch("""
            SELECT depth_new, COUNT(*) as count
            FROM items
            GROUP BY depth_new
            ORDER BY depth_new
        """)
        
        print(f"\n📊 Distribuição por Depth:")
        for row in depth_dist:
            print(f"   - Depth {row['depth_new']}: {row['count']} itens")
        
        # Mostra distribuição de quality
        quality_dist = await conn.fetch("""
            SELECT quality_new, COUNT(*) as count
            FROM items
            GROUP BY quality_new
            ORDER BY 
                CASE quality_new
                    WHEN 'COMMON' THEN 1
                    WHEN 'UNCOMMON' THEN 2
                    WHEN 'RARE' THEN 3
                    WHEN 'EPIC' THEN 4
                    WHEN 'LEGENDARY' THEN 5
                    WHEN 'MYTHIC' THEN 6
                END
        """)
        
        print(f"\n📊 Distribuição por Quality:")
        for row in quality_dist:
            print(f"   - {row['quality_new']}: {row['count']} itens")
        
        print("\n✅ Migration concluída com sucesso!")
        print("\n💡 Agora você pode reiniciar o bot para usar o novo sistema!")
        
    except Exception as e:
        print(f"\n❌ Erro ao executar migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        await conn.close()
        print("\n🔌 Conexão fechada")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Migration: Adicionar depth_new e quality_new")
    print("=" * 60)
    
    asyncio.run(run_migration())
