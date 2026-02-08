# 🔧 PLANO DE REFATORAÇÃO LEGAL - GUIA PRÁTICO
**Objetivo:** Tornar The Abyss Bot legalmente seguro para monetização

---

## 📋 CHECKLIST RÁPIDO

### ✅ O que está SEGURO:
- [x] Nomes de itens em português
- [x] Lore "The Abyss"
- [x] NPCs originais (Lysandra, Gorak, Zahuv)
- [x] Sistema de slots (1-9)
- [x] Recursos básicos (madeira, pedra, minério)
- [x] Mecânicas de PvP/Arena genéricas

### ⚠️ O que precisa MUDAR:
- [ ] **CRÍTICO:** Sistema Tier T1.0-T8.4 (substituir)
- [ ] **IMPORTANTE:** Renomear "Hideout" → "Sanctuary"
- [ ] **RECOMENDADO:** Modificar fórmula Power Score
- [ ] **OPCIONAL:** Trocar str/dex/int → might/agility/essence

---

## 🚀 FASE 1: SISTEMA DE PROGRESSÃO (Prioridade Máxima)

### Opção A: Sistema de Profundidades (Recomendado - Temático)
**Conceito:** Níveis representam quão fundo no Abismo o item foi forjado

```
Tier atual → Novo sistema:
T1.0-T1.4  →  Depth 1  (⬛ Surface)
T2.0-T2.4  →  Depth 2  (⬛ Twilight Layer)
T3.0-T3.4  →  Depth 3  (🟦 Azure Depth)
T4.0-T4.4  →  Depth 4  (🟦 Sapphire Depth)
T5.0-T5.4  →  Depth 5  (🟪 Violet Abyss)
T6.0-T6.4  →  Depth 6  (🟪 Obsidian Void)
T7.0-T7.4  →  Depth 7  (🟥 Crimson Core)
T8.0-T8.4  →  Depth 8  (🟥 Infernal Heart)

Subtiers → Qualidade:
.0 → Common (Comum)
.1 → Uncommon (Incomum)
.2 → Rare (Raro)
.3 → Epic (Épico)
.4 → Legendary (Lendário)
```

**Exemplo final:**
- `T4.2` → `Depth 4 - Rare` ou `D4-R`
- `T8.4` → `Depth 8 - Legendary` ou `D8-L`

---

### Opção B: Sistema de Ranks (Alternativa - Anime-style)
**Conceito:** Ranks de poder como em animes/mangás

```
Tier atual → Novo sistema:
T1 → F-Rank
T2 → E-Rank
T3 → D-Rank
T4 → C-Rank
T5 → B-Rank
T6 → A-Rank
T7 → S-Rank
T8 → SS-Rank (ou Mythic Rank)

Subtiers → Estrelas:
.0 → ☆ (sem estrelas)
.1 → ★ (1 estrela)
.2 → ★★ (2 estrelas)
.3 → ★★★ (3 estrelas)
.4 → ★★★★ (4 estrelas)
```

**Exemplo final:**
- `T4.2` → `C-Rank ★★`
- `T8.4` → `SS-Rank ★★★★`

---

## 🔨 IMPLEMENTAÇÃO: SISTEMA DE PROFUNDIDADES

### Passo 1: Atualizar Schema do Banco de Dados

```sql
-- Adicionar colunas novas (manter tier/subtier temporariamente)
ALTER TABLE items ADD COLUMN IF NOT EXISTS depth INTEGER;
ALTER TABLE items ADD COLUMN IF NOT EXISTS quality VARCHAR(20);

-- Migrar dados existentes
UPDATE items 
SET 
  depth = tier,
  quality = CASE subtier
    WHEN 0 THEN 'Common'
    WHEN 1 THEN 'Uncommon'
    WHEN 2 THEN 'Rare'
    WHEN 3 THEN 'Epic'
    WHEN 4 THEN 'Legendary'
    ELSE 'Common'
  END;

-- Fazer o mesmo para outras tabelas
UPDATE recipes SET depth = tier;
UPDATE inventory SET depth = tier;
-- etc...

-- Após verificar tudo funciona, remover tier/subtier (opcional)
-- ALTER TABLE items DROP COLUMN tier;
-- ALTER TABLE items DROP COLUMN subtier;
```

### Passo 2: Criar Utilitário de Conversão

```python
# utils/depth_system.py
"""
Sistema de Profundidades do The Abyss
Substitui o sistema de Tiers para originalidade legal
"""

DEPTH_NAMES = {
    1: "Surface",
    2: "Twilight Layer",
    3: "Azure Depth",
    4: "Sapphire Depth",
    5: "Violet Abyss",
    6: "Obsidian Void",
    7: "Crimson Core",
    8: "Infernal Heart",
    9: "Void Nexus",  # Futuro
    10: "Absolute Zero"  # Futuro
}

QUALITY_NAMES = {
    0: "Common",
    1: "Uncommon",
    2: "Rare",
    3: "Epic",
    4: "Legendary"
}

QUALITY_EMOJIS = {
    "Common": "⬛",
    "Uncommon": "🟦",
    "Rare": "🟪",
    "Epic": "🟥",
    "Legendary": "🟨"
}

def format_item_level(depth: int, quality: str) -> str:
    """
    Formata nível do item no novo sistema
    Ex: format_item_level(4, "Rare") -> "D4-R (Sapphire Depth)"
    """
    quality_abbr = quality[0]  # C, U, R, E, L
    emoji = QUALITY_EMOJIS.get(quality, "⬛")
    depth_name = DEPTH_NAMES.get(depth, f"Depth {depth}")
    return f"{emoji} D{depth}-{quality_abbr} ({depth_name})"

def depth_from_tier(tier: int) -> int:
    """Converte tier antigo para depth"""
    return tier  # 1:1 mapping

def quality_from_subtier(subtier: int) -> str:
    """Converte subtier antigo para quality"""
    return QUALITY_NAMES.get(subtier, "Common")

# Backwards compatibility
def tier_from_depth(depth: int) -> int:
    """Para compatibilidade temporária"""
    return depth
```

### Passo 3: Atualizar Comandos Principais

```python
# Em genitem (exemplo)
# ANTES:
@app_commands.describe(
    start_tier="Tier inicial (1-8)",
    start_subtier="Subtier inicial (0-4)",
    end_tier="Tier final (1-8)",
    end_subtier="Subtier final (0-4)"
)

# DEPOIS:
from utils.depth_system import QUALITY_NAMES

@app_commands.describe(
    start_depth="Profundidade inicial (1-8)",
    start_quality="Qualidade inicial (Common, Uncommon, Rare, Epic, Legendary)",
    end_depth="Profundidade final (1-8)",
    end_quality="Qualidade final"
)
async def genitem(
    self,
    interaction: discord.Interaction,
    nome: str,
    slot_id: int,
    start_depth: int = 1,
    start_quality: str = "Common",
    end_depth: int = 1,
    end_quality: str = "Common",
    # ...
):
    # Loop de criação
    for d in range(start_depth, end_depth + 1):
        qualities = get_quality_range(start_quality, end_quality)
        for q in qualities:
            # Criar item com depth e quality
            await self.bot.db.execute("""
                INSERT INTO items (name, slot_id, depth, quality, ...)
                VALUES ($1, $2, $3, $4, ...)
            """, nome, slot_id, d, q, ...)
```

### Passo 4: Atualizar Exibições (Embeds)

```python
# Em qualquer embed que mostre tier/subtier
# ANTES:
embed.add_field(name="Tier", value=f"T{tier}.{subtier}", inline=True)

# DEPOIS:
from utils.depth_system import format_item_level

level_text = format_item_level(depth, quality)
embed.add_field(name="Level", value=level_text, inline=True)
```

---

## 🏰 FASE 2: RENOMEAR HIDEOUT → SANCTUARY

### Buscar e Substituir (Use VSCode Find & Replace)

**Importante:** Fazer backup antes!

```
Buscar: hideout
Substituir: sanctuary

Buscar: Hideout
Substituir: Sanctuary

Buscar: HIDEOUT
Substituir: SANCTUARY
```

### Arquivos Afetados (Estimativa):
- `cogs/guild/hideout.py` → renomear para `sanctuary.py`
- `HIDEOUT_QUICKSTART.md` → `SANCTUARY_QUICKSTART.md`
- Schema SQL: todas as tabelas `hideout_*` → `sanctuary_*`
- Comandos: `/ho` pode manter (Ho de "Home")

### Migração do Banco

```sql
-- Renomear tabelas
ALTER TABLE hideouts RENAME TO sanctuaries;
ALTER TABLE hideout_recipes RENAME TO sanctuary_recipes;
ALTER TABLE hideout_recipe_materials RENAME TO sanctuary_recipe_materials;
ALTER TABLE hideout_crafting_queue RENAME TO sanctuary_crafting_queue;
-- etc...

-- Atualizar colunas
ALTER TABLE sanctuaries RENAME COLUMN hideout_id TO sanctuary_id;
ALTER TABLE guild_logs RENAME COLUMN hideout_id TO sanctuary_id;
-- etc...
```

---

## 📊 FASE 3: MODIFICAR POWER SCORE

### Fórmula Atual (Albion-like):
```python
power_score = (weapon_damage × 2 + tier × 50) + (armor_defense × 2 + tier × 50)
```

### Nova Fórmula (The Abyss Original):
```python
# Sistema baseado em Profundidades do Abismo
def calculate_power_score(depth: int, quality: str, weapon_dmg: int, armor_def: int) -> int:
    """
    Power Score único do The Abyss
    Fórmula: (dmg × 1.5 + depth × 100) + (def × 1.5 + depth × 75) + quality_bonus
    """
    quality_multiplier = {
        "Common": 1.0,
        "Uncommon": 1.1,
        "Rare": 1.25,
        "Epic": 1.4,
        "Legendary": 1.6
    }
    
    multiplier = quality_multiplier.get(quality, 1.0)
    
    weapon_score = (weapon_dmg * 1.5 + depth * 100) * multiplier
    armor_score = (armor_def * 1.5 + depth * 75) * multiplier
    
    return int(weapon_score + armor_score)
```

**Exemplo:**
- D4 Common com 100 dmg, 50 def: `(150 + 400) + (75 + 300) = 925`
- D4 Legendary mesmo stats: `925 × 1.6 = 1480`

---

## 🎨 FASE 4: STATS RENAMING (Opcional)

### Buscar e Substituir:
```python
# Em itens_config.json e código Python
"str" → "might"
"dex" → "agility"  
"int" → "essence"
```

### Atualizar Schema:
```sql
-- Se tiver colunas específicas
ALTER TABLE users RENAME COLUMN str TO might;
ALTER TABLE users RENAME COLUMN dex TO agility;
ALTER TABLE users RENAME COLUMN int TO essence;
```

---

## ✅ VERIFICAÇÃO FINAL

### Teste Completo:
1. [ ] Criar item com novo sistema (depth + quality)
2. [ ] Ver item no inventário (exibição correta)
3. [ ] Equipar item (stats funcionam)
4. [ ] Crafting com novo sistema
5. [ ] Arena/PvP com power score novo
6. [ ] Sanctuary criado e funcional
7. [ ] Migração de dados antigos OK

### Checklist Legal:
- [ ] Nenhuma menção a "Tier T1-T8" no código
- [ ] Nenhuma menção a "Hideout" visível ao usuário
- [ ] Power Score fórmula diferente
- [ ] README atualizado com disclaimer
- [ ] Documentação antiga removida/atualizada

---

## 📦 SCRIPT DE MIGRAÇÃO AUTOMÁTICA

Posso criar um script Python que:
1. Lê todo o banco de dados
2. Converte tier/subtier → depth/quality
3. Atualiza todos os registros
4. Gera relatório de mudanças

**Quer que eu crie esse script?**

---

## ⏱️ ESTIMATIVAS DE TEMPO

| Fase | Complexidade | Tempo Estimado |
|------|-------------|----------------|
| Fase 1 (Depth System) | Alta | 3-4 horas |
| Fase 2 (Hideout → Sanctuary) | Média | 1-2 horas |
| Fase 3 (Power Score) | Baixa | 30 minutos |
| Fase 4 (Stats Rename) | Baixa | 30 minutos |
| Testes | Média | 1-2 horas |
| **TOTAL** | - | **6-9 horas** |

---

## 💡 DICA PROFISSIONAL

**Fazer em etapas:**
1. Semana 1: Implementar Depth System (backend)
2. Semana 2: Atualizar UI/Embeds
3. Semana 3: Renomear Hideout → Sanctuary
4. Semana 4: Testes e ajustes finais

**Não precisa fazer tudo de uma vez!**

---

## 🆘 PRECISA DE AJUDA?

Posso ajudar com:
- ✅ Criar scripts de migração SQL
- ✅ Implementar utils/depth_system.py completo
- ✅ Atualizar cogs específicos
- ✅ Gerar lista completa de arquivos para modificar
- ✅ Criar testes automatizados

**Qual fase quer começar primeiro?**
