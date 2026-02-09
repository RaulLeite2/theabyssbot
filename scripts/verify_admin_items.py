#!/usr/bin/env python3
"""
Script de verificação rápida: Confere se os itens de admin foram inseridos
Uso: python scripts/verify_admin_items.py
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_admin_items():
    """Verifica se os itens de admin existem no banco"""
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL não encontrado no .env")
        return False
    
    print("=" * 60)
    print("🔍 VERIFICANDO ITENS DE ADMIN")
    print("=" * 60)
    print()
    
    try:
        # Conectar ao banco
        print("⏳ Conectando ao banco de dados...")
        conn = await asyncpg.connect(database_url)
        print("✓ Conectado!\n")
        
        # Verificar se as colunas existem
        print("⏳ Verificando schema...")
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'items' 
            AND column_name IN ('depth_new', 'quality_new')
        """)
        
        if len(columns) < 2:
            print("❌ PROBLEMA: Colunas depth_new/quality_new não existem!")
            print("   Execute: psql $DATABASE_URL < db/migrations/000_add_depth_quality_columns.sql")
            await conn.close()
            return False
        
        print("✓ Colunas depth_new e quality_new existem\n")
        
        # Contar itens de admin
        print("⏳ Buscando itens de admin...")
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_admin_items,
                MAX(basedamage) as max_damage,
                MAX(basedefense) as max_defense
            FROM items
            WHERE depth_new = 99 AND quality_new = 'ADMIN'
        """)
        
        if stats['total_admin_items'] == 0:
            print("❌ PROBLEMA: Nenhum item de admin encontrado!")
            print()
            print("   Soluções:")
            print("   1. Reinicie o bot (migrations rodam automaticamente)")
            print("   2. Execute manualmente:")
            print("      psql $DATABASE_URL < db/migrations/002_add_admin_items.sql")
            await conn.close()
            return False
        
        print(f"✓ {stats['total_admin_items']} itens de admin encontrados!")
        print(f"  • Maior dano: {stats['max_damage']:,}")
        print(f"  • Maior defesa: {stats['max_defense']:,}")
        print()
        
        # Listar os itens
        print("📋 Lista de Itens de Admin:")
        print("-" * 60)
        
        items = await conn.fetch("""
            SELECT 
                name,
                basedamage,
                basedefense,
                CASE slot_id
                    WHEN 0 THEN 'Consumable'
                    WHEN 1 THEN 'Amulet'
                    WHEN 2 THEN 'Head'
                    WHEN 3 THEN 'Legs'
                    WHEN 4 THEN 'Chest'
                    WHEN 5 THEN 'Feet'
                    WHEN 6 THEN 'Weapon'
                    WHEN 7 THEN 'Ring'
                    WHEN 8 THEN 'Shield'
                END as slot
            FROM items 
            WHERE quality_new = 'ADMIN' 
            ORDER BY slot_id, basedamage DESC
        """)
        
        for item in items:
            display_name = item['name'].replace('_', ' ').title()
            dmg = f"{item['basedamage']:,}" if item['basedamage'] > 0 else "-"
            def_val = f"{item['basedefense']:,}" if item['basedefense'] > 0 else "-"
            print(f"  • {display_name:30s} [{item['slot']:10s}] DMG: {dmg:>10s} DEF: {def_val:>10s}")
        
        print()
        print("=" * 60)
        print("✅ TUDO CERTO! Itens de admin estão no banco.")
        print("=" * 60)
        print()
        print("🎮 Teste no Discord:")
        print("   /giveadminitem item:espada_do_desenvolvedor")
        print("   /giveadminkit")
        print()
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        print()
        print("Verifique:")
        print("  • DATABASE_URL está correto no .env")
        print("  • Você tem acesso ao banco de dados")
        print("  • O banco está online")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_admin_items())
    exit(0 if success else 1)
