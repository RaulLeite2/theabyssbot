# 🏠 Hideout System 2.0 - Quick Start

## ✨ O que foi implementado?

### 1️⃣ Sistema de Notificação
- Players são notificados quando entram em zonas com Hideout da guilda/aliança
- Funciona automaticamente em `/explore` e `/explore_portal`

### 2️⃣ Entrada/Saída de Hideouts
- `/ho entrar` - Entra no Hideout (se houver na zona)
- `/ho sair` - Sai do Hideout e retorna à zona anterior

### 3️⃣ Power Score System
- Calculado automaticamente: **(weapon_damage × 2 + tier × 50) + (armor_defense × 2 + tier × 50)**
- Necessário para dungeons do Hideout

### 4️⃣ Sistema de Crafting
- `/ho recipes` - Lista receitas disponíveis
- `/ho craft <id>` - Inicia crafting de um item
- Requer Estação de Crafting no Hideout (500k gold)

### 5️⃣ Dungeon Especial
- `/ho dungeon` - Inicia dungeon de 5 jogadores
- Requisitos:
  - ✅ 5 pessoas na party
  - ✅ Todos dentro do Hideout
  - ✅ 1500+ Power Score total
- Recompensas em gold proporcionais ao poder
- Cooldown de 1 hora por Hideout

### 6️⃣ Upgrades do Hideout
- `/ho facility crafting` - Compra Estação de Crafting (500k)
- `/ho facility dungeon` - Compra Portal da Dungeon (500k)

---

## 🚀 Como Começar

### 1. Aplicar Migration
```bash
# No PostgreSQL
psql -U seu_usuario -d the_abyss -f db/migration_hideout_update.sql
```

### 2. (Opcional) Popular Receitas
```bash
# Edite db/populate_hideout_recipes.sql primeiro para ajustar item_ids
psql -U seu_usuario -d the_abyss -f db/populate_hideout_recipes.sql
```

### 3. Reiniciar o Bot
```bash
python main.py
```

---

## 🎮 Testando

```discord
# 1. Explore uma zona com Hideout da sua guilda
/explore

# 2. Entre no Hideout
/ho entrar

# 3. Verifique receitas
/ho recipes

# 4. Compre melhorias (líder da guilda)
/ho facility crafting
/ho facility dungeon

# 5. Crie uma party de 5 pessoas
/party_create
/party_invite @player2 @player3 @player4 @player5

# 6. Todos entram no HO
/ho entrar

# 7. Inicie a dungeon
/ho dungeon

# 8. Saia do HO
/ho sair
```

---

## 📊 Novas Tabelas

- `hideout_recipes` - Receitas de crafting
- `hideout_recipe_materials` - Materiais das receitas
- `hideout_crafting_queue` - Fila de crafting
- `hideout_dungeon_runs` - Histórico de dungeons
- `hideout_dungeon_party` - Membros nas dungeons
- `hideout_dungeon_rewards` - Recompensas distribuídas

## 📝 Novas Colunas

**users:**
- `in_hideout_id` - ID do Hideout atual (NULL se não estiver)
- `previous_zone_id` - Zona antes de entrar no HO
- `equipped_weapon` - Arma equipada (para Power Score)
- `equipped_armor` - Armadura equipada (para Power Score)

**hideouts:**
- `has_crafting_station` - Se tem estação de crafting
- `has_dungeon_portal` - Se tem portal de dungeon
- `dungeon_cooldown` - Timestamp do cooldown

---

## 📖 Documentação Completa

Veja [HIDEOUT_UPDATE.md](docs/HIDEOUT_UPDATE.md) para documentação detalhada com:
- Fluxos completos
- Fórmulas de cálculo
- Exemplos de queries SQL
- Planos futuros

---

## ⚙️ Configuração de Equipamentos

Para que o Power Score funcione, você precisará adicionar comandos para equipar armas e armaduras:

```sql
-- Exemplo: equipar arma
UPDATE users 
SET equipped_weapon = <item_id> 
WHERE discord_id = <user_id>;

-- Exemplo: equipar armadura
UPDATE users 
SET equipped_armor = <item_id> 
WHERE discord_id = <user_id>;
```

Ou criar comandos `/equip weapon <item>` e `/equip armor <item>` no futuro.

---

## 🐛 Troubleshooting

### "Nenhuma receita disponível"
→ Execute `db/populate_hideout_recipes.sql` (ajuste os item_ids primeiro)

### "Não há Hideout na zona"
→ Certifique-se que sua guilda tem um HO criado com `/ho create`

### "Power Score insuficiente"
→ Equipe itens melhores (atualize `equipped_weapon` e `equipped_armor`)

### "Portal da Dungeon não disponível"
→ Líder precisa usar `/ho facility dungeon` (500k gold)

---

**Pronto para usar! 🎉**
