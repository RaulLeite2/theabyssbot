# 📋 ANÁLISE DE RISCO LEGAL - THE ABYSS BOT
**Data da Análise:** 8 de Fevereiro de 2026  
**Status:** ⚠️ ATENÇÃO NECESSÁRIA ANTES DE MONETIZAR

---

## 🔴 RISCO CRÍTICO (ALTO) - AÇÃO LEGAL PROVÁVEL

### 1. Sistema de Tiers Idêntico ao Albion Online
**Localização:** Todo o código  
**Descrição:** Uso de sistema T1.0 até T8.4 com subtiers .0, .1, .2, .3, .4  
**Risco:** 🔴 **ALTÍSSIMO** - Esse é o sistema característico de Albion Online

**Evidências encontradas:**
```
data/starter_items.txt - Linhas 58-142
- Tier 1.0 (starter)
- Tier 2-3 (T2.0 até T3.4)
- Tier 4-5 (T4.0 até T5.4)
- Tier 6-8 (T6.0 até T8.4)

cogs/wiki/wiki.py - Linha 79
- return f"T{tier}.{subtier}"

data/crafts.json - Todo o arquivo
- tier_start, tier_end, subtier_start, subtier_end
```

**Recomendação:** 🚨 **MUDANÇA OBRIGATÓRIA**
- Trocar para sistema de níveis/raros diferente
- Opções seguras:
  - ⭐ Ranks: Rank F → E → D → C → B → A → S → SS → SSS
  - 🔢 Níveis: Nível 1-100 com qualidade (Comum, Raro, Épico, Lendário)
  - 💎 Camadas: Layer I-X com graus (α, β, γ, δ)
  - 🌑 The Abyss temático: Profundidade 1-10 (Superfície → Núcleo Abissal)

---

### 2. Nomenclatura de Skills/Attributes Similar
**Localização:** `data/itens_config.json`  
**Descrição:** Uso de scaling attributes (str, dex, int)

**Evidências:**
```json
"scaling": {
  "str": 1.5,  // Strength
  "dex": 0.8,  // Dexterity
  "int": 0.0   // Intelligence
}
```

**Risco:** 🟡 **MÉDIO** - Termos comuns, mas contexto pode agravar

**Recomendação:** 💡 **OPCIONAL MAS RECOMENDADO**
- Trocar para sistema único do Abyss:
  - `str` → `might` (Força → Poder)
  - `dex` → `agility` (Destreza → Agilidade)
  - `int` → `wisdom` ou `essence` (Inteligência → Sabedoria/Essência)

---

### 3. Uso de Termos "Albion" no Código (SE HOUVER)
**Status:** ✅ **NÃO ENCONTRADO** (bom sinal)  
**Busca realizada:** Nenhuma menção direta a "Albion" encontrada no código

---

## 🟡 RISCO MÉDIO - ZONA CINZA LEGAL

### 4. Sistema de Guild + Hideout + Territory
**Localização:** `cogs/guild/`, `HIDEOUT_QUICKSTART.md`  
**Descrição:** Mecânica de guildas com hideouts e territórios

**Risco:** 🟡 **MÉDIO** - Mecânica comum em MMOs, mas combinação pode ser problemática

**Elementos problemáticos:**
- `hideout` - Nome exato usado em Albion (Guild Island/Hideout)
- `Power Score` calculado como: `(weapon_damage × 2 + tier × 50) + (armor_defense × 2 + tier × 50)`
- Sistema de 7 hideouts máximo por guilda

**Recomendação:** 🔧 **MUDANÇA RECOMENDADA**
- Renomear `Hideout` → **Sanctuary** (Santuário)
- Renomear `Territory` → **Domain** (Domínio)
- Mudar fórmula de Power Score para algo único

---

### 5. Sistema de Crafting com Recursos
**Localização:** `data/crafts.json`, `cogs/rpg/rpg_craft.py`  
**Descrição:** Sistema de crafting com recursos (madeira, pedra, minério, fibra, pelego)

**Risco:** 🟢 **BAIXO** - Recursos são genéricos em 99% dos jogos de crafting

**Recursos usados:**
```json
"materials": [
  "madeira",   // Wood - genérico ✅
  "pedra",     // Stone - genérico ✅
  "minerio",   // Ore - genérico ✅
  "fibra",     // Fiber - similar a Albion ⚠️
  "pelego",    // Hide - similar a Albion ⚠️
  "cristal",   // Crystal - genérico ✅
  "ervas"      // Herbs - genérico ✅
]
```

**Recomendação:** 💡 **OPCIONAL**
- `pelego` → **couro** (leather) ou **scales** (escamas) - mais genérico
- `fibra` → **tecido** (cloth) - menos específico

---

### 6. Slot System (Equipment Slots)
**Localização:** `data/starter_items.txt` linhas 42-49  
**Descrição:** Sistema de 9 slots de equipamento

```
1 = Amuleto (Amulet)
2 = Cabeça (Head)
3 = Pernas (Legs)
4 = Mão Principal (Main Hand)
5 = Torso (Chest)
6 = Mão Secundária (Off Hand)
7 = Costas (Back/Cape)
8 = Pés (Feet)
9 = [Slot especial para recursos]
```

**Risco:** 🟢 **BAIXO** - Sistema de slots é padrão em RPGs

---

## 🟢 RISCO BAIXO - ELEMENTOS SEGUROS

### 7. Nomes de Itens em Português
**Status:** ✅ **SEGURO**  
**Exemplos:** "Espada Enferrujada", "Lâmina do Abismo", "Cajado das Eras"

Nomes originais em português são seguros desde que não sejam traduções literais de itens do Albion.

---

### 8. Lore Própria: "The Abyss"
**Status:** ✅ **SEGURO**  
**Elementos temáticos únicos:**
- Abismo (The Abyss)
- Temas de trevas/sombras
- NPCs próprios (Lysandra, Gorak)
- Mapa Zahuv (portal dimensional)

---

### 9. Sistema de Arena/PvP Genérico
**Localização:** `cogs/arena/`  
**Status:** 🟢 **BAIXO RISCO** - Mecânica comum em 90% dos RPG bots

---

## 🛡️ ANÁLISE DE PATENTES (Limitada)

### ⚠️ Aviso Importante
Não é possível consultar bases de patentes completas (USPTO, EPO, WIPO) sem acesso a ferramentas especializadas. As áreas abaixo são **conhecidas por ter patentes de software em jogos:**

### Áreas de Risco de Patentes:
1. **Sistemas de progressão dinâmica de tier** - Patentes existem
2. **Algoritmos de matchmaking PvP** - Patentes conhecidas (EA, Activision)
3. **Sistemas de loot com raridade dinâmica** - Patentes existem
4. **Mecânicas de crafting multipassos** - Zona cinza

### ✅ Áreas Sem Patente Conhecida:
- Sistema básico de slots de equipamento
- Sistema de guild/clan genérico
- Sistema de recursos de crafting
- Sistema turn-based de combate

---

## 📊 RESUMO DE RISCOS

| Elemento | Risco | Ação Necessária |
|----------|-------|-----------------|
| Sistema Tier T1.0-T8.4 | 🔴 CRÍTICO | **MUDANÇA OBRIGATÓRIA** |
| Hideout/Territory | 🟡 MÉDIO | Renomear antes de monetizar |
| Power Score formula | 🟡 MÉDIO | Modificar fórmula |
| Scaling (str/dex/int) | 🟡 BAIXO-MÉDIO | Opcional mas recomendado |
| Recursos (fibra/pelego) | 🟢 BAIXO | Opcional |
| Lore "The Abyss" | ✅ SEGURO | Manter |
| Nomes em português | ✅ SEGURO | Manter |
| Sistema de slots | ✅ SEGURO | Manter |

---

## 🚀 PLANO DE AÇÃO RECOMENDADO

### Prioridade 1: ANTES DE MONETIZAR (Obrigatório)
1. ✅ **Eliminar sistema Tier/Subtier T1.0-T8.4**
   - Implementar sistema de Profundidades (Depth 1-10) ou Ranks (F-SSS)
   - Atualizar TODO o código (banco, cogs, configs)

2. ✅ **Renomear conceitos chave**
   - `Hideout` → `Sanctuary`
   - `Territory` → `Domain`
   - `Guild League` → `Alliance Covenant` (se aplicável)

### Prioridade 2: RECOMENDADO
3. 🔧 **Modificar fórmula de Power Score**
   - Criar fórmula única do The Abyss
   - Ex: `(damage × 1.5 + depth × 100) + (defense × 1.5 + depth × 75) + bonuses`

4. 🔧 **Trocar nomenclatura de stats**
   - `str/dex/int` → `might/agility/essence`

### Prioridade 3: OPCIONAL (Mas seguro)
5. 💡 **Revisar nomes de recursos**
   - `pelego` → `couro` ou `scales`
   - `fibra` → `tecido`

---

## 📝 DISCLAIMER LEGAL

### Para Uso Público/Comercial:
```
⚠️ TERMOS DE USO RECOMENDADO:

"The Abyss Bot é um RPG original de Discord desenvolvido 
independentemente. Não é afiliado, associado, ou endossado 
por qualquer jogo comercial existente. Todas as mecânicas 
são originais ou baseadas em conceitos genéricos de RPG."
```

### Para README.md:
```markdown
## Aviso Legal
The Abyss Bot é um projeto independente de RPG para Discord. 
Este bot NÃO é associado, afiliado, ou endossado por nenhum 
jogo comercial. Todas as mecânicas de jogo são originais ou 
baseadas em conceitos genéricos comuns em jogos de RPG.
```

---

## 🧑‍⚖️ QUANDO CONSULTAR ADVOGADO

Consulte um advogado especializado em propriedade intelectual SE:
- ❌ Receber **cease & desist** de qualquer empresa
- 💰 Monetização ultrapassar **$10.000 USD/ano**
- 📈 Base de usuários ultrapassar **50.000 usuários ativos**
- 📢 Quiser fazer marketing público pesado

---

## 🔍 VERIFICAÇÃO DE CONFORMIDADE

### Checklist Pré-Monetização:
- [ ] Sistema de Tier T1-T8 removido/substituído
- [ ] Termos "Hideout" renomeados para algo original
- [ ] Power Score formula modificada
- [ ] Disclaimer legal adicionado ao README
- [ ] Consulta com advogado (se receita > $5k/ano)
- [ ] Seguro de responsabilidade civil (se receita > $20k/ano)

---

## 📚 REFERÊNCIAS E RECURSOS

### Precedentes Legais Importantes:
1. **Tetris Holding vs. Xio Interactive** (2012)
   - Mecânicas similares OK, trade dress NÃO
   
2. **Spry Fox vs. LOLApps** (2012)
   - Cópia de mecânicas únicas é processável

3. **Oracle vs. Google** (2021)
   - APIs podem ter copyright, mas uso transformativo é defensável

### Consulta de Patentes (Se quiser fazer):
- USPTO: https://patents.google.com/
- WIPO: https://patentscope.wipo.int/
- Search terms: "tier system", "equipment progression", "guild mechanics"

---

## ✅ CONCLUSÃO

**Status Atual:** ⚠️ **RISCO MÉDIO-ALTO**

**Principal Problema:** Sistema de Tier T1.0-T8.4 é característica registrada de Albion Online.

**Solução Simples:** Substituir por sistema de Profundidades/Ranks + renomear termos chave = **Projeto Seguro** ✅

**Tempo Estimado de Refatoração:** 4-6 horas de trabalho

**Custo vs Benefício:** Vale MUITO a pena fazer antes de investir em marketing/monetização.

---

**Última atualização:** 2026-02-08  
**Próxima revisão recomendada:** Após implementar mudanças Prioridade 1
