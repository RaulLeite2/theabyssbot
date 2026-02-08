#!/usr/bin/env python3
"""
Gerador de SQL para items - Para usar com migrate_to_depth.py após migração completa
Este script gera um arquivo SQL com INSERT commands para todos os items
"""

import json
from pathlib import Path
from enum import Enum

# Enum Quality com multiplicadores
class Quality(Enum):
    COMMON = "COMMON"
    UNCOMMON = "UNCOMMON"
    RARE = "RARE"
    EPIC = "EPIC"
    LEGENDARY = "LEGENDARY"
    MYTHIC = "MYTHIC"
    
    def multiplier(self) -> float:
        mapping = {
            Quality.COMMON: 1.0,
            Quality.UNCOMMON: 1.2,
            Quality.RARE: 1.5,
            Quality.EPIC: 1.8,
            Quality.LEGENDARY: 2.2,
            Quality.MYTHIC: 2.8,
        }
        return mapping[self]

# Dados de exemplo para itens
ITEM_TEMPLATES = [
    # SLOT 2 - HEAD (Cabeça)
    {
        "name": "Elmo Básico",
        "slot_id": 2,
        "base_damage": 0,
        "base_defense": 15,
        "scaling": {"str": 0.1, "dex": 0.05, "int": 0.05},
        "buffs": [],
    },
    {
        "name": "Coroa de Ferro",
        "slot_id": 2,
        "base_damage": 5,
        "base_defense": 25,
        "scaling": {"str": 0.2, "dex": 0.1, "int": 0.1},
        "buffs": [{"type": "hp_boost", "value": 20}],
    },
    {
        "name": "Capacete Mágico",
        "slot_id": 2,
        "base_damage": 0,
        "base_defense": 20,
        "scaling": {"str": 0.05, "dex": 0.1, "int": 0.3},
        "buffs": [{"type": "mana_boost", "value": 50}, {"type": "int_boost", "value": 3}],
    },
    {
        "name": "Diadema Arcana",
        "slot_id": 2,
        "base_damage": 0,
        "base_defense": 10,
        "scaling": {"str": 0.0, "dex": 0.05, "int": 0.5},
        "buffs": [{"type": "mana_regen", "value": 2}, {"type": "int_boost", "value": 5}],
    },

    # SLOT 3 - LEGS (Pernas)
    {
        "name": "Calças de Couro",
        "slot_id": 3,
        "base_damage": 0,
        "base_defense": 20,
        "scaling": {"str": 0.15, "dex": 0.2, "int": 0.0},
        "buffs": [{"type": "dodge_chance", "value": 5}],
    },
    {
        "name": "Calças de Aço",
        "slot_id": 3,
        "base_damage": 0,
        "base_defense": 35,
        "scaling": {"str": 0.3, "dex": 0.1, "int": 0.05},
        "buffs": [{"type": "hp_boost", "value": 30}],
    },
    {
        "name": "Saia Mística",
        "slot_id": 3,
        "base_damage": 0,
        "base_defense": 15,
        "scaling": {"str": 0.05, "dex": 0.15, "int": 0.25},
        "buffs": [{"type": "mana_boost", "value": 40}],
    },

    # SLOT 4 - MAIN HAND (Mão Principal)
    {
        "name": "Espada Básica",
        "slot_id": 4,
        "base_damage": 15,
        "base_defense": 5,
        "scaling": {"str": 0.4, "dex": 0.2, "int": 0.0},
        "buffs": [],
    },
    {
        "name": "Espada de Aço",
        "slot_id": 4,
        "base_damage": 25,
        "base_defense": 10,
        "scaling": {"str": 0.5, "dex": 0.15, "int": 0.0},
        "buffs": [{"type": "damage_boost", "value": 10}],
    },
    {
        "name": "Lâmina Sombria",
        "slot_id": 4,
        "base_damage": 20,
        "base_defense": 0,
        "scaling": {"str": 0.3, "dex": 0.5, "int": 0.1},
        "buffs": [{"type": "crit_chance", "value": 15}],
    },
    {
        "name": "Cajado Arcano",
        "slot_id": 4,
        "base_damage": 10,
        "base_defense": 0,
        "scaling": {"str": 0.05, "dex": 0.1, "int": 0.6},
        "buffs": [{"type": "mana_boost", "value": 60}, {"type": "spell_power", "value": 20}],
    },
    {
        "name": "Machado de Ouro",
        "slot_id": 4,
        "base_damage": 35,
        "base_defense": 5,
        "scaling": {"str": 0.65, "dex": 0.1, "int": 0.0},
        "buffs": [{"type": "damage_boost", "value": 15}, {"type": "hp_boost", "value": 25}],
    },

    # SLOT 5 - TORSO (Peito)
    {
        "name": "Armadura de Couro",
        "slot_id": 5,
        "base_damage": 0,
        "base_defense": 40,
        "scaling": {"str": 0.2, "dex": 0.15, "int": 0.0},
        "buffs": [{"type": "hp_boost", "value": 40}],
    },
    {
        "name": "Armadura Completa",
        "slot_id": 5,
        "base_damage": 0,
        "base_defense": 60,
        "scaling": {"str": 0.3, "dex": 0.05, "int": 0.05},
        "buffs": [{"type": "hp_boost", "value": 60}, {"type": "def_boost", "value": 15}],
    },
    {
        "name": "Manto Mágico",
        "slot_id": 5,
        "base_damage": 5,
        "base_defense": 20,
        "scaling": {"str": 0.1, "dex": 0.15, "int": 0.4},
        "buffs": [{"type": "mana_boost", "value": 80}, {"type": "spell_power", "value": 25}],
    },
    {
        "name": "Peitoral Espectral",
        "slot_id": 5,
        "base_damage": 10,
        "base_defense": 30,
        "scaling": {"str": 0.2, "dex": 0.25, "int": 0.3},
        "buffs": [{"type": "hp_regen", "value": 3}, {"type": "mana_regen", "value": 2}],
    },

    # SLOT 6 - OFF HAND (Mão Secundária)
    {
        "name": "Escudo de Madeira",
        "slot_id": 6,
        "base_damage": 0,
        "base_defense": 25,
        "scaling": {"str": 0.2, "dex": 0.05, "int": 0.0},
        "buffs": [{"type": "block_chance", "value": 10}],
    },
    {
        "name": "Escudo de Aço",
        "slot_id": 6,
        "base_damage": 0,
        "base_defense": 40,
        "scaling": {"str": 0.3, "dex": 0.0, "int": 0.05},
        "buffs": [{"type": "block_chance", "value": 20}, {"type": "hp_boost", "value": 30}],
    },
    {
        "name": "Adaga Envenenada",
        "slot_id": 6,
        "base_damage": 12,
        "base_defense": 5,
        "scaling": {"str": 0.1, "dex": 0.4, "int": 0.1},
        "buffs": [{"type": "crit_damage", "value": 30}],
    },
    {
        "name": "Orbe Mística",
        "slot_id": 6,
        "base_damage": 5,
        "base_defense": 10,
        "scaling": {"str": 0.0, "dex": 0.05, "int": 0.5},
        "buffs": [{"type": "mana_boost", "value": 50}, {"type": "spell_power", "value": 15}],
    },

    # SLOT 8 - FEET (Pés)
    {
        "name": "Botas de Couro",
        "slot_id": 8,
        "base_damage": 0,
        "base_defense": 10,
        "scaling": {"str": 0.0, "dex": 0.2, "int": 0.0},
        "buffs": [{"type": "dodge_chance", "value": 8}],
    },
    {
        "name": "Botas de Aço",
        "slot_id": 8,
        "base_damage": 0,
        "base_defense": 15,
        "scaling": {"str": 0.1, "dex": 0.1, "int": 0.0},
        "buffs": [{"type": "hp_boost", "value": 15}],
    },
    {
        "name": "Sapatos Alados",
        "slot_id": 8,
        "base_damage": 0,
        "base_defense": 8,
        "scaling": {"str": 0.05, "dex": 0.3, "int": 0.1},
        "buffs": [{"type": "dodge_chance", "value": 15}, {"type": "speed_boost", "value": 20}],
    },

    # SLOT 1 - ACCESSORY/RING (Acessório)
    {
        "name": "Anel Básico",
        "slot_id": 1,
        "base_damage": 0,
        "base_defense": 0,
        "scaling": {"str": 0.05, "dex": 0.05, "int": 0.05},
        "buffs": [{"type": "hp_boost", "value": 10}],
    },
    {
        "name": "Anel de Ouro",
        "slot_id": 1,
        "base_damage": 5,
        "base_defense": 5,
        "scaling": {"str": 0.1, "dex": 0.1, "int": 0.1},
        "buffs": [{"type": "hp_boost", "value": 20}, {"type": "damage_boost", "value": 5}],
    },
    {
        "name": "Anel Mágico",
        "slot_id": 1,
        "base_damage": 0,
        "base_defense": 0,
        "scaling": {"str": 0.0, "dex": 0.05, "int": 0.3},
        "buffs": [{"type": "mana_boost", "value": 60}, {"type": "spell_power", "value": 20}],
    },
]


def escape_json(obj):
    """Escapa string JSON para SQL"""
    return json.dumps(obj, ensure_ascii=False).replace("'", "''")


def generate_sql():
    """Gera SQL para inserir todos os items"""
    
    depths = [1, 2, 3, 4, 5, 6, 7, 8]
    qualities = [Quality.COMMON, Quality.UNCOMMON, Quality.RARE, Quality.EPIC, Quality.LEGENDARY, Quality.MYTHIC]
    
    sqls = []
    
    # Header
    sqls.append("-- Auto-generated SQL: Insert items with Depth System")
    sqls.append("-- Generated for TheAbyssBot")
    sqls.append("-- Date: 2026-02-08")
    sqls.append("")
    sqls.append("BEGIN TRANSACTION;")
    sqls.append("")
    
    total_items = 0
    
    for template in ITEM_TEMPLATES:
        for depth in depths:
            for quality in qualities:
                # Nomes
                base_name = template["name"]
                quality_name = quality.name.capitalize()
                suffix = f"(Depth {depth} {quality_name})"
                full_name = f"{base_name} {suffix}"
                
                # Multiplicadores
                depth_multiplier = 1 + (depth - 1) * 0.15
                quality_multiplier = quality.multiplier()
                
                # Stats
                damage = int(template["base_damage"] * depth_multiplier * quality_multiplier)
                defense = int(template["base_defense"] * depth_multiplier * quality_multiplier)
                
                # Buffs ajustados
                adjusted_buffs = []
                for buff in template["buffs"]:
                    adjusted_buff = buff.copy()
                    adjusted_buff["value"] = int(buff["value"] * depth_multiplier * quality_multiplier)
                    adjusted_buffs.append(adjusted_buff)
                
                # Flags
                flags = {
                    "legendary": quality in [Quality.LEGENDARY, Quality.MYTHIC],
                    "tradeable": True,
                    "quest_item": False
                }
                
                # Montar INSERT
                insert = f"""INSERT INTO items (
    name, slot_id, tier, depth_new, quality_new, plus_level,
    base_damage, base_defense, scaling, buffs, flags
) VALUES (
    '{full_name.replace("'", "''")}',
    {template['slot_id']},
    'T{depth}.0',
    {depth},
    '{quality.value}',
    0,
    {damage},
    {defense},
    '{escape_json(template['scaling'])}',
    '{escape_json(adjusted_buffs)}',
    '{escape_json(flags)}'
);"""
                
                sqls.append(insert)
                total_items += 1
    
    # Footer
    sqls.append("")
    sqls.append("COMMIT;")
    sqls.append("")
    sqls.append(f"-- Total items inserted: {total_items}")
    
    return "\n".join(sqls), total_items


def main():
    print("="*70)
    print("🔧 GERADOR SQL - ITEMS COM DEPTH SYSTEM")
    print("="*70)
    print()
    
    sql_content, total = generate_sql()
    
    # Salvar arquivo
    output_path = Path("db/seeds/populate_items_depth.sql")
    output_path.write_text(sql_content, encoding="utf-8")
    
    print(f"✅ Arquivo SQL gerado: {output_path}")
    print(f"   Total de items: {total}")
    print()
    print("📋 Como usar:")
    print("   1. Aguarde a migração Tier→Depth estar completa")
    print("   2. Execute: psql -U postgres -d theabyssbot -f db/seeds/populate_items_depth.sql")
    print("   3. Ou copie/cole o SQL no pgAdmin ou DBeaver")
    print()
    print("="*70)
    print()


if __name__ == "__main__":
    main()
