#!/usr/bin/env python3
"""
Script para gerar itens de exemplo no banco de dados
Com Depth System (1-8) e múltiplas qualidades
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar parent directory ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Usar DATABASE_URL do Railway
os.environ['DATABASE_URL'] = "postgresql://postgres:LcCxXyxgEXrjjTgcFSKVHZBruskiUeeT@postgres.railway.internal:5432/railway"

from db.db import Database
from utils.depth_system import Quality

# Dados de exemplo para itens
ITEM_TEMPLATES = [
    # SLOT 2 - HEAD (Cabeça)
    {
        "name": "Elmo Básico",
        "slot_id": 2,
        "base_damage": 0,
        "base_defense": 15,
        "scaling": {"might": 0.1, "agility": 0.05, "essence": 0.05},
        "buffs": [],
    },
    {
        "name": "Coroa de Ferro",
        "slot_id": 2,
        "base_damage": 5,
        "base_defense": 25,
        "scaling": {"might": 0.2, "agility": 0.1, "essence": 0.1},
        "buffs": [{"type": "hp_boost", "value": 20}],
    },
    {
        "name": "Capacete Mágico",
        "slot_id": 2,
        "base_damage": 0,
        "base_defense": 20,
        "scaling": {"might": 0.05, "agility": 0.1, "essence": 0.3},
        "buffs": [{"type": "mana_boost", "value": 50}, {"type": "essence_boost", "value": 3}],
    },
    {
        "name": "Diadema Arcana",
        "slot_id": 2,
        "base_damage": 0,
        "base_defense": 10,
        "scaling": {"might": 0.0, "agility": 0.05, "essence": 0.5},
        "buffs": [{"type": "mana_regen", "value": 2}, {"type": "essence_boost", "value": 5}],
    },

    # SLOT 3 - LEGS (Pernas)
    {
        "name": "Calças de Couro",
        "slot_id": 3,
        "base_damage": 0,
        "base_defense": 20,
        "scaling": {"might": 0.15, "agility": 0.2, "essence": 0.0},
        "buffs": [{"type": "dodge_chance", "value": 5}],
    },
    {
        "name": "Calças de Aço",
        "slot_id": 3,
        "base_damage": 0,
        "base_defense": 35,
        "scaling": {"might": 0.3, "agility": 0.1, "essence": 0.05},
        "buffs": [{"type": "hp_boost", "value": 30}],
    },
    {
        "name": "Saia Mística",
        "slot_id": 3,
        "base_damage": 0,
        "base_defense": 15,
        "scaling": {"might": 0.05, "agility": 0.15, "essence": 0.25},
        "buffs": [{"type": "mana_boost", "value": 40}],
    },

    # SLOT 4 - MAIN HAND (Mão Principal)
    {
        "name": "Espada Básica",
        "slot_id": 4,
        "base_damage": 15,
        "base_defense": 5,
        "scaling": {"might": 0.4, "agility": 0.2, "essence": 0.0},
        "buffs": [],
    },
    {
        "name": "Espada de Aço",
        "slot_id": 4,
        "base_damage": 25,
        "base_defense": 10,
        "scaling": {"might": 0.5, "agility": 0.15, "essence": 0.0},
        "buffs": [{"type": "damage_boost", "value": 10}],
    },
    {
        "name": "Lâmina Sombria",
        "slot_id": 4,
        "base_damage": 20,
        "base_defense": 0,
        "scaling": {"might": 0.3, "agility": 0.5, "essence": 0.1},
        "buffs": [{"type": "crit_chance", "value": 15}],
    },
    {
        "name": "Cajado Arcano",
        "slot_id": 4,
        "base_damage": 10,
        "base_defense": 0,
        "scaling": {"might": 0.05, "agility": 0.1, "essence": 0.6},
        "buffs": [{"type": "mana_boost", "value": 60}, {"type": "spell_power", "value": 20}],
    },
    {
        "name": "Machado de Ouro",
        "slot_id": 4,
        "base_damage": 35,
        "base_defense": 5,
        "scaling": {"might": 0.65, "agility": 0.1, "essence": 0.0},
        "buffs": [{"type": "damage_boost", "value": 15}, {"type": "hp_boost", "value": 25}],
    },
    
    # NEW WEAPONS - Fase Adicional
    {
        "name": "Lança Sombria",
        "slot_id": 4,
        "base_damage": 28,
        "base_defense": 8,
        "scaling": {"might": 0.35, "agility": 0.35, "essence": 0.1},
        "buffs": [{"type": "armor_pen", "value": 12}, {"type": "crit_chance", "value": 8}],
    },
    {
        "name": "Arco Longo",
        "slot_id": 4,
        "base_damage": 22,
        "base_defense": 2,
        "scaling": {"might": 0.15, "agility": 0.55, "essence": 0.05},
        "buffs": [{"type": "crit_damage", "value": 35}, {"type": "range_bonus", "value": 50}],
    },
    {
        "name": "Martelo de Guerra",
        "slot_id": 4,
        "base_damage": 42,
        "base_defense": 12,
        "scaling": {"might": 0.75, "agility": 0.0, "essence": 0.0},
        "buffs": [{"type": "hp_boost", "value": 50}, {"type": "stun_chance", "value": 20}],
    },
    {
        "name": "Adaga Venenosa",
        "slot_id": 4,
        "base_damage": 18,
        "base_defense": 0,
        "scaling": {"might": 0.2, "agility": 0.6, "essence": 0.15},
        "buffs": [{"type": "attack_speed", "value": 25}, {"type": "poison_damage", "value": 15}],
    },
    {
        "name": "Grimório Ancestral",
        "slot_id": 4,
        "base_damage": 8,
        "base_defense": 5,
        "scaling": {"might": 0.0, "agility": 0.05, "essence": 0.75},
        "buffs": [{"type": "mana_boost", "value": 100}, {"type": "spell_power", "value": 40}, {"type": "cooldown_reduction", "value": 15}],
    },
    {
        "name": "Foice Maldita",
        "slot_id": 4,
        "base_damage": 30,
        "base_defense": 3,
        "scaling": {"might": 0.45, "agility": 0.25, "essence": 0.25},
        "buffs": [{"type": "lifesteal", "value": 18}, {"type": "shadow_damage", "value": 20}],
    },
    {
        "name": "Katana Relâmpago",
        "slot_id": 4,
        "base_damage": 24,
        "base_defense": 4,
        "scaling": {"might": 0.3, "agility": 0.55, "essence": 0.1},
        "buffs": [{"type": "attack_speed", "value": 35}, {"type": "lightning_damage", "value": 18}, {"type": "dodge_chance", "value": 10}],
    },

    # SLOT 5 - TORSO (Peito)
    {
        "name": "Armadura de Couro",
        "slot_id": 5,
        "base_damage": 0,
        "base_defense": 40,
        "scaling": {"might": 0.2, "agility": 0.15, "essence": 0.0},
        "buffs": [{"type": "hp_boost", "value": 40}],
    },
    {
        "name": "Armadura Completa",
        "slot_id": 5,
        "base_damage": 0,
        "base_defense": 60,
        "scaling": {"might": 0.3, "agility": 0.05, "essence": 0.05},
        "buffs": [{"type": "hp_boost", "value": 60}, {"type": "def_boost", "value": 15}],
    },
    {
        "name": "Manto Mágico",
        "slot_id": 5,
        "base_damage": 5,
        "base_defense": 20,
        "scaling": {"might": 0.1, "agility": 0.15, "essence": 0.4},
        "buffs": [{"type": "mana_boost", "value": 80}, {"type": "spell_power", "value": 25}],
    },
    {
        "name": "Peitoral Espectral",
        "slot_id": 5,
        "base_damage": 10,
        "base_defense": 30,
        "scaling": {"might": 0.2, "agility": 0.25, "essence": 0.3},
        "buffs": [{"type": "hp_regen", "value": 3}, {"type": "mana_regen", "value": 2}],
    },

    # SLOT 6 - OFF HAND (Mão Secundária)
    {
        "name": "Escudo de Madeira",
        "slot_id": 6,
        "base_damage": 0,
        "base_defense": 25,
        "scaling": {"might": 0.2, "agility": 0.05, "essence": 0.0},
        "buffs": [{"type": "block_chance", "value": 10}],
    },
    {
        "name": "Escudo de Aço",
        "slot_id": 6,
        "base_damage": 0,
        "base_defense": 40,
        "scaling": {"might": 0.3, "agility": 0.0, "essence": 0.05},
        "buffs": [{"type": "block_chance", "value": 20}, {"type": "hp_boost", "value": 30}],
    },
    {
        "name": "Adaga Envenenada",
        "slot_id": 6,
        "base_damage": 12,
        "base_defense": 5,
        "scaling": {"might": 0.1, "agility": 0.4, "essence": 0.1},
        "buffs": [{"type": "crit_damage", "value": 30}],
    },
    {
        "name": "Orbe Mística",
        "slot_id": 6,
        "base_damage": 5,
        "base_defense": 10,
        "scaling": {"might": 0.0, "agility": 0.05, "essence": 0.5},
        "buffs": [{"type": "mana_boost", "value": 50}, {"type": "spell_power", "value": 15}],
    },

    # SLOT 8 - FEET (Pés)
    {
        "name": "Botas de Couro",
        "slot_id": 8,
        "base_damage": 0,
        "base_defense": 10,
        "scaling": {"might": 0.0, "agility": 0.2, "essence": 0.0},
        "buffs": [{"type": "dodge_chance", "value": 8}],
    },
    {
        "name": "Botas de Aço",
        "slot_id": 8,
        "base_damage": 0,
        "base_defense": 15,
        "scaling": {"might": 0.1, "agility": 0.1, "essence": 0.0},
        "buffs": [{"type": "hp_boost", "value": 15}],
    },
    {
        "name": "Sapatos Alados",
        "slot_id": 8,
        "base_damage": 0,
        "base_defense": 8,
        "scaling": {"might": 0.05, "agility": 0.3, "essence": 0.1},
        "buffs": [{"type": "dodge_chance", "value": 15}, {"type": "speed_boost", "value": 20}],
    },

    # SLOT 1 - ACCESSORY/RING (Acessório)
    {
        "name": "Anel Básico",
        "slot_id": 1,
        "base_damage": 0,
        "base_defense": 0,
        "scaling": {"might": 0.05, "agility": 0.05, "essence": 0.05},
        "buffs": [{"type": "hp_boost", "value": 10}],
    },
    {
        "name": "Anel de Ouro",
        "slot_id": 1,
        "base_damage": 5,
        "base_defense": 5,
        "scaling": {"might": 0.1, "agility": 0.1, "essence": 0.1},
        "buffs": [{"type": "hp_boost", "value": 20}, {"type": "damage_boost", "value": 5}],
    },
    {
        "name": "Anel Mágico",
        "slot_id": 1,
        "base_damage": 0,
        "base_defense": 0,
        "scaling": {"might": 0.0, "agility": 0.05, "essence": 0.3},
        "buffs": [{"type": "mana_boost", "value": 60}, {"type": "spell_power", "value": 20}],
    },
]


async def generate_items(db: Database):
    """Gera múltiplos itens em diferentes profundidades e qualidades"""
    
    print("="*70)
    print("🎯 GERADOR DE ITENS - DEPTH SYSTEM")
    print("="*70)
    
    try:
        # Profundidades e qualidades a gerar
        depths = [1, 2, 3, 4, 5, 6, 7, 8]
        qualities = [Quality.COMMON, Quality.UNCOMMON, Quality.RARE, Quality.EPIC, Quality.LEGENDARY, Quality.MYTHIC]
        
        total_items = 0
        
        for template in ITEM_TEMPLATES:
            for depth in depths[:3]:  # Gerar apenas até Depth 3 para teste (menos de 100 itens)
                for quality in qualities:
                    # Variar nomes por profundidade e qualidade
                    base_name = template["name"]
                    quality_name = quality.name.capitalize()
                    suffix = f"(Depth {depth} {quality_name})"
                    full_name = f"{base_name} {suffix}"
                    
                    # Aumentar stats baseado em profundidade e qualidade
                    depth_multiplier = 1 + (depth - 1) * 0.15
                    quality_multiplier = quality.multiplier()
                    
                    # Calcular stats
                    damage = int(template["base_damage"] * depth_multiplier * quality_multiplier)
                    defense = int(template["base_defense"] * depth_multiplier * quality_multiplier)
                    
                    # Escalar atributos de buff
                    adjusted_buffs = []
                    for buff in template["buffs"]:
                        adjusted_buff = buff.copy()
                        adjusted_buff["value"] = int(buff["value"] * depth_multiplier * quality_multiplier)
                        adjusted_buffs.append(adjusted_buff)
                    
                    # Inserir item no BD
                    await db.execute(
                        """
                        INSERT INTO items (
                            name, slot_id, tier, depth_new, quality_new, plus_level,
                            base_damage, base_defense, scaling, buffs, flags
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        """,
                        full_name,
                        template["slot_id"],
                        f"T{depth}.0",  # Backward compat com tier antigo
                        depth,
                        quality.value,
                        0,
                        damage,
                        defense,
                        template["scaling"],  # dict → JSON
                        adjusted_buffs,  # list → JSON
                        {"legendary": quality in [Quality.LEGENDARY, Quality.MYTHIC], "tradeable": True, "quest_item": False},
                    )
                    
                    total_items += 1
                    print(f"✅ Criado: {full_name}")
        
        print("\n" + "="*70)
        print(f"📊 SUCESSO! {total_items} items criados")
        print(f"   Slots cobertos: 1 (ring), 2 (head), 3 (legs), 4 (main), 5 (torso), 6 (off), 8 (feet)")
        print(f"   Profundidades: Depth 1-3 (para teste)")
        print(f"   Qualidades: Common → Mythic")
        print("="*70 + "\n")
        
        return total_items
        
    except Exception as e:
        print(f"❌ ERRO ao gerar items: {e}")
        import traceback
        traceback.print_exc()
        return 0


async def main():
    """Entry point"""
    print("\n📦 Conectando ao banco de dados...\n")
    
    db = Database()
    await db.connect()
    
    try:
        count = await generate_items(db)
        print(f"✅ Geração concluída: {count} items criados\n")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
