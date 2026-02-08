#!/usr/bin/env python3
"""
Gerador de SQL para ITENS DE ADMIN
Cria itens com stats absurdas para testes e administração

Uso:
    python scripts/generate_admin_items_sql.py
    
Saída: db/seeds/populate_admin_items.sql
"""

import json
from pathlib import Path

# Mapeamento de slot_id para nome do slot
SLOT_NAMES = {
    0: "consumable",
    1: "amulet",
    2: "head",
    3: "legs", 
    4: "chest",
    5: "feet",
    6: "weapon",
    7: "ring",
    8: "shield"
}

def generate_admin_items_sql():
    """Gera SQL para inserir itens de admin no banco"""
    
    # Carregar itens de admin
    admin_items_path = Path(__file__).parent.parent / "data" / "admin_items.json"
    
    if not admin_items_path.exists():
        print(f"❌ Arquivo não encontrado: {admin_items_path}")
        return
    
    with open(admin_items_path, 'r', encoding='utf-8') as f:
        admin_data = json.load(f)
    
    sql_lines = []
    sql_lines.append("-- ================================================")
    sql_lines.append("-- ITENS DE ADMIN - APENAS PARA TESTES/DEBUG")
    sql_lines.append("-- ⚠️  NÃO DISTRIBUIR PARA JOGADORES NORMAIS")
    sql_lines.append("-- ================================================")
    sql_lines.append("")
    sql_lines.append("-- Inserir itens de admin na tabela items")
    sql_lines.append("-- Todos com depth_new = 99 (tier especial de admin)")
    sql_lines.append("-- Todos com quality_new = 'ADMIN' (qualidade especial)")
    sql_lines.append("")
    
    item_count = 0
    
    for tier_name, items in admin_data.items():
        sql_lines.append(f"-- {tier_name.upper()}")
        sql_lines.append("")
        
        for item_name, item_data in items.items():
            item_count += 1
            
            slot_id = item_data.get("slot_id", 0)
            slot_name = SLOT_NAMES.get(slot_id, "unknown")
            base_damage = item_data.get("base_damage", 0)
            base_defense = item_data.get("base_defense", 0)
            scaling = json.dumps(item_data.get("scaling", {}))
            buffs = json.dumps(item_data.get("buffs", []))
            flags = item_data.get("flags", {})
            description = item_data.get("description", "Item de administrador.")
            
            # Escapar aspas simples no JSON
            scaling = scaling.replace("'", "''")
            buffs = buffs.replace("'", "''")
            
            # Gerar nome formatado
            display_name = item_name.replace("_", " ").title()
            
            sql_lines.append(f"-- {display_name}")
            sql_lines.append("INSERT INTO items (")
            sql_lines.append("    name, slot_id, base_damage, base_defense,")
            sql_lines.append("    scaling, buffs, legendary, quest_item,")
            sql_lines.append("    depth_new, quality_new, description")
            sql_lines.append(") VALUES (")
            sql_lines.append(f"    '{item_name}',")
            sql_lines.append(f"    {slot_id},  -- {slot_name}")
            sql_lines.append(f"    {base_damage},")
            sql_lines.append(f"    {base_defense},")
            sql_lines.append(f"    '{scaling}',")
            sql_lines.append(f"    '{buffs}',")
            sql_lines.append(f"    {str(flags.get('legendary', False)).lower()},")
            sql_lines.append(f"    {str(flags.get('quest_item', False)).lower()},")
            sql_lines.append(f"    99,  -- depth_new: Admin Tier")
            sql_lines.append(f"    'ADMIN',  -- quality_new: Qualidade especial de admin")
            sql_lines.append(f"    '{description}'")
            sql_lines.append(");")
            sql_lines.append("")
    
    sql_lines.append("-- ================================================")
    sql_lines.append(f"-- TOTAL: {item_count} itens de admin criados")
    sql_lines.append("-- ================================================")
    sql_lines.append("")
    sql_lines.append("-- Verificar inserções")
    sql_lines.append("SELECT ")
    sql_lines.append("    COUNT(*) as total_admin_items,")
    sql_lines.append("    AVG(base_damage) as avg_damage,")
    sql_lines.append("    AVG(base_defense) as avg_defense,")
    sql_lines.append("    MAX(base_damage) as max_damage,")
    sql_lines.append("    MAX(base_defense) as max_defense")
    sql_lines.append("FROM items")
    sql_lines.append("WHERE depth_new = 99 AND quality_new = 'ADMIN';")
    sql_lines.append("")
    sql_lines.append("-- Listar todos os itens de admin")
    sql_lines.append("SELECT id, name, slot_id, base_damage, base_defense, quality_new")
    sql_lines.append("FROM items")
    sql_lines.append("WHERE depth_new = 99 AND quality_new = 'ADMIN'")
    sql_lines.append("ORDER BY slot_id, name;")
    
    # Salvar arquivo SQL
    output_path = Path(__file__).parent.parent / "db" / "seeds" / "populate_admin_items.sql"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    
    print("=" * 60)
    print("▣ ADMIN ITEMS :: SQL GENERATION")
    print("=" * 60)
    print(f"✓ {item_count} itens de admin gerados")
    print(f"✓ Arquivo criado: {output_path}")
    print("")
    print("📋 ITENS CRIADOS:")
    print("")
    
    for tier_name, items in admin_data.items():
        for item_name, item_data in items.items():
            display_name = item_name.replace("_", " ").title()
            dmg = item_data.get("base_damage", 0)
            def_val = item_data.get("base_defense", 0)
            slot_name = SLOT_NAMES.get(item_data.get("slot_id", 0), "?")
            print(f"  • {display_name:30s} [{slot_name:10s}] DMG: {dmg:>8,} DEF: {def_val:>8,}")
    
    print("")
    print("=" * 60)
    print("⚠️  USE COM RESPONSABILIDADE!")
    print("=" * 60)
    print("")
    print("Para aplicar no banco de dados:")
    print(f"  psql $DATABASE_URL < {output_path}")
    print("")

if __name__ == "__main__":
    generate_admin_items_sql()
