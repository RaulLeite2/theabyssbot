# 🔧 ITENS DE ADMIN - THE ABYSS BOT

## ⚠️ ATENÇÃO
**Estes itens têm stats ABSURDAS e são APENAS para testes/debug/admin.**
**NÃO distribua para jogadores normais - quebra completamente o balanceamento do jogo!**

---

## 📋 Lista de Itens

### ⚔️ ARMAS

#### Espada do Desenvolvedor
- **Dano Base:** 100,000
- **Defesa Base:** 50,000
- **Buffs:**
  - 100% Crit Chance
  - 500% Crit Damage
  - 50% Lifesteal
  - +1000% EXP
  - +1000% Gold
- **Descrição:** A lendária espada dos criadores. Poder absoluto concentrado em uma lâmina.

#### Cajado do Refactor
- **Dano Base:** 250,000
- **Defesa Base:** 10,000
- **Buffs:**
  - +2000% Spell Power
  - +15,000 INT
  - +1,000,000 Mana
  - +50,000 Mana Regen
  - 90% Cooldown Reduction
  - +500% AoE Radius
- **Descrição:** Cajado que refatora a realidade ao seu redor. Caos reorganizado em harmonia.

---

### 🛡️ ARMADURAS

#### Armadura do Admin
- **Dano Base:** 5,000
- **Defesa Base:** 200,000
- **Buffs:**
  - 90% Damage Reduction
  - +5,000 HP/s Regen
  - +5,000 Mana/s Regen
  - +100,000 HP
  - 50% Reflect Damage
- **Descrição:** Armadura forjada nas chamas do código. Invulnerabilidade em forma tangível.

#### Elmo Omnisciente
- **Dano Base:** 10,000
- **Defesa Base:** 150,000
- **Buffs:**
  - +5,000 INT
  - +50,000 Mana
  - +2,000 Mana/s Regen
  - +500% Spell Power
  - 50% Cooldown Reduction
- **Descrição:** Elmo que concede conhecimento de todos os bugs e features do sistema.

#### Calças do Debugger
- **Dano Base:** 8,000
- **Defesa Base:** 120,000
- **Buffs:**
  - +5,000 DEX
  - 75% Dodge Chance
  - +500% Movement Speed
  - +300% Attack Speed
  - 50% Evasion
- **Descrição:** Calças que permitem esquivar de qualquer erro de runtime.

#### Botas do Hotfix
- **Dano Base:** 15,000
- **Defesa Base:** 80,000
- **Buffs:**
  - +1000% Movement Speed
  - +3,000 STR
  - +3,000 DEX
  - +50,000 Kick Damage
  - +10,000 Stamina
- **Descrição:** Botas que aplicam correções instantâneas em qualquer situação crítica.

---

### 💎 ACESSÓRIOS

#### Amuleto do Sysadmin
- **Dano Base:** 50,000
- **Defesa Base:** 50,000
- **Buffs:**
  - +10,000 ALL STATS
  - +500,000 HP
  - +500,000 Mana
  - +10,000 HP/s Regen
  - +10,000 Mana/s Regen
  - +10000% EXP
  - +10000% Gold
  - +1000 Luck
- **Descrição:** Amuleto que concede acesso root ao próprio universo do jogo.

#### Anel do Commit
- **Dano Base:** 25,000
- **Defesa Base:** 25,000
- **Buffs:**
  - 100% Crit Chance
  - +1000% Crit Damage
  - 100% Lifesteal
  - 100% Spell Vamp
  - 100% Penetration
- **Descrição:** Anel que faz commit direto na produção sem code review. Poder máximo, sem recuo.

#### Escudo do Rollback
- **Dano Base:** 0
- **Defesa Base:** 500,000
- **Buffs:**
  - 99% Damage Reduction
  - 90% Block Chance
  - 100% Reflect Damage
  - +20,000 HP/s Regen
  - 100% Revive Chance
- **Descrição:** Escudo capaz de desfazer qualquer ação hostil. Ctrl+Z físico perfeito.

---

### 🧪 CONSUMÍVEIS

#### Poção de Godmode
- **Efeito:** Heal instantâneo de 999,999,999 HP/Mana + Invulnerabilidade por 1 hora
- **Descrição:** Poção que concede literalmente poder divino. Use com responsabilidade... ou não.

#### Kit de Emergência
- **Efeito:** Heal instantâneo de 10,000,000 HP/Mana + Limpa debuffs + Shield de 1,000,000
- **Descrição:** Kit de emergência para quando tudo está pegando fogo. Literalmente salva vidas.

#### Pergaminho do Fix
- **Efeito:** Revive + Full Restore + 60s de God Mode
- **Descrição:** Pergaminho que conserta literalmente qualquer problema. Até morte.

---

## 🚀 Como Usar

### 1. Gerar o SQL
```bash
python scripts/generate_admin_items_sql.py
```

### 2. Aplicar no Banco de Dados
```bash
# Railway (remote)
psql $DATABASE_URL < db/seeds/populate_admin_items.sql

# Local
psql -h localhost -U postgres -d theabyss < db/seeds/populate_admin_items.sql
```

### 3. Usar os Comandos no Discord

#### Dar um Item Específico
```
/giveadminitem item:espada_do_desenvolvedor user:@jogador quantity:1
```

#### Dar Kit Completo
```
/giveadminkit user:@jogador
```

O kit completo inclui:
- ⚔️ Espada do Desenvolvedor
- 🛡️ Armadura do Admin
- 👑 Elmo Omnisciente
- 👖 Calças do Debugger
- 👢 Botas do Hotfix
- 📿 Amuleto do Sysadmin
- 💍 Anel do Commit
- 🛡️ Escudo do Rollback
- 🧪 Poção de Godmode (x1)
- 🩹 Kit de Emergência (x1)
- 📜 Pergaminho do Fix (x1)

---

## 🔍 Verificar Itens no Banco

```sql
-- Ver todos os itens de admin
SELECT id, name, base_damage, base_defense, quality_new
FROM items
WHERE depth_new = 99 AND quality_new = 'ADMIN'
ORDER BY slot_id, name;

-- Estatísticas
SELECT 
    COUNT(*) as total_admin_items,
    AVG(base_damage) as avg_damage,
    AVG(base_defense) as avg_defense,
    MAX(base_damage) as max_damage,
    MAX(base_defense) as max_defense
FROM items
WHERE depth_new = 99 AND quality_new = 'ADMIN';
```

---

## 📊 Stats Comparativos

| Item | Dano | Defesa | Multiplier vs Normal |
|------|------|--------|---------------------|
| **Espada Admin** | 100,000 | 50,000 | ~1000x |
| **Item Normal T8** | ~100 | ~50 | 1x |
| **Item Lendário T8** | ~300 | ~150 | 3x |

**Os itens de admin são literalmente 1000x mais fortes que itens normais!**

---

## ⚙️ Sistema Técnico

### Identificação
- **Depth:** 99 (tier especial de admin)
- **Quality:** "ADMIN" (qualidade especial)
- **Flag:** `admin_only: true`

### Arquivos Relacionados
- `data/admin_items.json` - Definição dos itens
- `scripts/generate_admin_items_sql.py` - Gerador de SQL
- `db/seeds/populate_admin_items.sql` - SQL de inserção
- `cogs/admin/adminrpg.py` - Comandos de admin

---

## 🎯 Casos de Uso

✅ **USAR PARA:**
- Testes de balanceamento
- Debug de sistemas de combate
- Demonstrações para desenvolvedores
- Testes de stress do sistema
- Eventos especiais de admin

❌ **NÃO USAR PARA:**
- Dar para jogadores normais
- Economia do jogo
- Eventos públicos
- Recompensas normais
- Qualquer coisa que afete o balanceamento

---

## 🐛 Troubleshooting

### Item não aparece no comando
**Problema:** Item não existe no banco de dados
**Solução:** Execute o SQL: `psql $DATABASE_URL < db/seeds/populate_admin_items.sql`

### Comando retorna erro de permissão
**Problema:** Usuário não é o desenvolvedor (MY_ID)
**Solução:** Apenas o ID definido em `MY_ID` pode usar comandos de admin

### Item no inventário mas não equipável
**Problema:** Cog de RPG pode não reconhecer depth=99
**Solução:** Verifique se o sistema de equipamento aceita depth_new=99

---

## 📝 Changelog

**v1.0.0** - 08/02/2026
- ✨ Criação inicial de 12 itens de admin
- ⚔️ 2 armas (Espada, Cajado)
- 🛡️ 4 armaduras (Peito, Cabeça, Pernas, Pés)
- 💎 3 acessórios (Amuleto, Anel, Escudo)
- 🧪 3 consumíveis (Poção, Kit, Pergaminho)
- 🤖 Comandos `/giveadminitem` e `/giveadminkit`
- 📄 Documentação completa

---

**Criado por:** The Abyss Bot Development Team
**Última Atualização:** 08 de Fevereiro de 2026
