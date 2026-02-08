# 🧪 GUIA DE TESTES - Depth System & Items

## 🎯 Ordem Recomendada de Testes

### 1️⃣ **Testar Bot Básico**

```bash
# No Railway ou local
python main.py
```

**Verificar:**
- ✅ Bot conecta sem erros
- ✅ Não aparece mais warning: `Alguns cogs nao foram carregados: ['cogs.rpg.rpg_refactored']`
- ✅ Comando `/rpg` aparece disponível

---

### 2️⃣ **Testar Depth System (Importação)**

```python
# No Railway, execute um teste rápido
python -c "
from utils.depth_system import DepthTier, Quality, TierMigrator

# Teste 1: Criar DepthTier
depth = DepthTier(depth=5, quality=Quality.EPIC, plus_level=3)
print(f'✅ DepthTier criado: {depth}')
print(f'   Power: {depth.calculate_power()}')

# Teste 2: Converter Tier antigo
migrator = TierMigrator()
converted = migrator.tier_to_depth('T7.3')
print(f'✅ Conversão T7.3 → Depth {converted.depth} {converted.quality.value}')
"
```

**Esperado:**
```
✅ DepthTier criado: DepthTier(depth=5, quality=<Quality.EPIC: 'EPIC'>, plus_level=3)
   Power: 150
✅ Conversão T7.3 → Depth 7 EPIC
```

---

### 3️⃣ **Testar Items no Banco (Verificar se foram populados)**

```sql
-- No psql ou DBeaver conectado ao Railway
-- (use a DATABASE_URL fornecida)

-- Teste 1: Contar items por profundidade
SELECT depth_new, quality_new, COUNT(*) as total
FROM items
WHERE depth_new IS NOT NULL
GROUP BY depth_new, quality_new
ORDER BY depth_new, quality_new;

-- Esperado: 26 linhas (8 depths x 6 qualities cada, exceto alguns slots)
```

**Resultados Esperados:**
```
depth_new | quality_new | total
----------+-------------+-------
    1     | COMMON      |   26
    1     | UNCOMMON    |   26
    1     | RARE        |   26
    ...   | ...         |  ...
    8     | MYTHIC      |   26
-- Total: ~1248 items
```

```sql
-- Teste 2: Verificar Cristal de Fundação
SELECT name, quality_new, depth_new, flags
FROM items
WHERE name LIKE '%Cristal de Fundação%';

-- Esperado: 1 linha com o cristal
```

```sql
-- Teste 3: Verificar materiais do cristal
SELECT name, tier, quality_new
FROM items
WHERE name IN (
    'Fragmento de Fogo Primordial',
    'Essência do Abismo',
    'Coração de Dragão Ancião',
    'Grimório Ancestral'
);

-- Esperado: 4+ linhas com os materiais
```

---

### 4️⃣ **Testar Comandos RPG no Discord**

#### A) Criar Personagem
```
/rpg start
```

**Verificar:**
- ✅ Cria personagem com itens Depth 1 Common
- ✅ Mostra embed com stats corretas
- ✅ Nenhum erro no console

#### B) Ver Perfil
```
/rpg profile
```

**Verificar:**
- ✅ Exibe items equipados
- ✅ Mostra profundidade e qualidade dos items
- ✅ Power calculado corretamente

#### C) Testar Auto-Conversão (se tiver items antigos)
```sql
-- Inserir um item T5.2 antigo manualmente
INSERT INTO equipment (user_id, slot_id, item_id)
VALUES (123456789, 4, (SELECT id FROM items WHERE tier = 'T5.2' LIMIT 1));
```

Depois no Discord:
```
/rpg profile
```

**Verificar:**
- ✅ Sistema auto-converte T5.2 → Depth 5 RARE
- ✅ Não quebra o comando

---

### 5️⃣ **Testar Receita do Cristal (Se Hideout estiver implementado)**

```sql
-- Teste 1: Verificar se a receita existe
SELECT id, name, min_hideout_level, craft_time_seconds
FROM hideout_recipes
WHERE name = 'Cristal de Fundação do Santuário';

-- Esperado: 1 linha (se você já executou populate_hideout_recipes.sql)
```

**Se a receita não estiver configurada ainda:**

1. Execute os SQLs na ordem:
```bash
psql $DATABASE_URL -f db/seeds/populate_sanctuary_crystal.sql
psql $DATABASE_URL -f db/seeds/populate_hideout_recipes.sql
```

2. Depois, ajuste os IDs na receita:
```sql
-- Pegar IDs dos materiais
SELECT id, name FROM items WHERE name LIKE '%Fragmento%' OR name LIKE '%Essência%' LIMIT 10;

-- Atualizar result_item_id da receita
UPDATE hideout_recipes 
SET result_item_id = (SELECT id FROM items WHERE name = 'Cristal de Fundação do Santuário')
WHERE name = 'Cristal de Fundação do Santuário';
```

3. Testar craft (se tiver comando):
```
/hideout craft Cristal de Fundação do Santuário
```

---

### 6️⃣ **Testes de Integração (Completos)**

#### Cenário 1: Jogador Novo
```
1. /rpg start
2. /rpg profile
3. /rpg explore (se existir)
4. Verificar se items dropados têm depth_new e quality_new
```

#### Cenário 2: Jogador com Items Antigos
```sql
-- Criar um jogador com items Tier antigo
INSERT INTO equipment (user_id, slot_id, item_id)
VALUES 
    (999999, 2, (SELECT id FROM items WHERE tier = 'T3.1' LIMIT 1)),
    (999999, 4, (SELECT id FROM items WHERE tier = 'T6.4' LIMIT 1));
```

```
/rpg profile @jogador_teste
```

**Verificar:**
- ✅ Sistema converte automaticamente
- ✅ Nenhum crash
- ✅ Display correto

#### Cenário 3: Crafting de Cristal (Simulado)
```sql
-- Dar todos os materiais pra um jogador
-- (ajuste user_id)
INSERT INTO inventory (user_id, item_id, quantity)
SELECT 123456789, id, 999
FROM items
WHERE name IN (
    'Fragmento de Fogo Primordial',
    'Fragmento de Gelo Eterno',
    'Núcleo de Mana Concentrado'
    -- ... etc
);
```

Depois tentar craftar (se comando existir).

---

### 7️⃣ **Testes de Performance**

```sql
-- Teste 1: Query de items por profundidade (deve ser rápida)
EXPLAIN ANALYZE
SELECT * FROM items
WHERE depth_new = 5 AND quality_new = 'EPIC'
LIMIT 10;

-- Esperado: < 50ms
```

```sql
-- Teste 2: Conversão em massa (deve ser rápida)
SELECT 
    tier,
    CASE 
        WHEN tier ~ '^T[1-8]\.[0-4]$' THEN 
            substring(tier from 2 for 1)::int
        ELSE NULL
    END as depth
FROM items
WHERE tier IS NOT NULL
LIMIT 1000;

-- Esperado: < 100ms
```

---

## 🐛 Checklist de Bugs Comuns

### ❌ Bug 1: "Alguns cogs nao foram carregados"
**Sintoma:** Warning no console ao iniciar bot
**Causa:** `await bot.add_cog()` em vez de `bot.add_cog()`
**Status:** ✅ CORRIGIDO (commit d2a61ba)

### ❌ Bug 2: Items com depth_new NULL
**Sintoma:** Items antigos não convertidos
**Causa:** Falta executar populate_items_depth.sql
**Solução:** 
```bash
psql $DATABASE_URL -f db/seeds/populate_items_depth.sql
```

### ❌ Bug 3: Receita sem materiais
**Sintoma:** Receita aparece mas não tem materials
**Causa:** IDs não configurados em hideout_recipe_materials
**Solução:** Seguir passo 5️⃣ acima

### ❌ Bug 4: Quality multiplier incorreto
**Sintoma:** Stats muito altos ou baixos
**Causa:** Erro no enum Quality
**Verificar:**
```python
from utils.depth_system import Quality
print(Quality.MYTHIC.multiplier())  # Deve ser 2.8
```

---

## 📊 Métricas de Sucesso

| Teste | Status | Métrica |
|-------|--------|---------|
| Bot inicia sem erros | ⬜ | 0 warnings no console |
| Items populados | ⬜ | 1264 items (1248 equip + 16 materiais) |
| Depth System funciona | ⬜ | Conversões corretas |
| RPG commands OK | ⬜ | `/rpg start` e `/rpg profile` funcionam |
| Cristal populado | ⬜ | 1 cristal + 15 materiais no BD |
| Receita configurada | ⬜ | 1 receita com 1812 materiais total |

---

## 🚀 Quick Test (Rápido 5 min)

Execute este script de teste completo:

```bash
# 1. Testar imports
python -c "from utils.depth_system import DepthTier, Quality; print('✅ Depth System OK')"

# 2. Testar bot start
timeout 10 python main.py || echo "✅ Bot iniciou (killed after 10s)"

# 3. Testar SQL count
psql $DATABASE_URL -c "SELECT COUNT(*) as items FROM items WHERE depth_new IS NOT NULL;"
```

**Resultado Esperado:**
```
✅ Depth System OK
✅ Bot iniciou (killed after 10s)
 items 
-------
  1248
```

---

## 🔍 Logs Importantes

**Procure por:**
```bash
# Sucesso
[INFO] ✅ Cog loaded: cogs.rpg.rpg_refactored
[INFO] ✅ Depth System: Auto-converted T5.3 → Depth 5 EPIC

# Erros (não devem aparecer)
[WARNING] Alguns cogs nao foram carregados
[ERROR] AttributeError: 'NoneType' object has no attribute 'depth_new'
```

---

## 📞 Troubleshooting Rápido

### Problema: "Module depth_system not found"
```bash
# Solução: Adicionar ao PYTHONPATH
export PYTHONPATH=/app:$PYTHONPATH
python main.py
```

### Problema: "Items table is empty"
```bash
# Solução: Popular items
psql $DATABASE_URL -f db/seeds/populate_items_depth.sql
psql $DATABASE_URL -f db/seeds/populate_sanctuary_crystal.sql
```

### Problema: "Recipe result_item_id is NULL"
```sql
-- Solução: Atualizar ID do resultado
UPDATE hideout_recipes 
SET result_item_id = (SELECT id FROM items WHERE name = 'Cristal de Fundação do Santuário')
WHERE result_item_id IS NULL;
```

---

## ✅ Aprovação Final

Quando TODOS os testes acima passarem:
- ✅ Bot funciona sem warnings
- ✅ Commands RPG respondem
- ✅ Items aparecem no banco
- ✅ Depth System converte corretamente
- ✅ Cristal e materiais existem

**→ PRONTO PARA DEPLOY EM PRODUÇÃO! 🚀**
