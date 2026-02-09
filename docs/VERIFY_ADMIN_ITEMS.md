# 🔍 Como Verificar se os Itens de Admin Foram Adicionados

## Verificação Rápida no Discord

Execute o comando:
```
/giveadminitem item:espada_do_desenvolvedor
```

Se funcionar = itens foram adicionados ✅  
Se der erro = migrations não foram executadas ❌

---

## Verificação no Banco de Dados

### Via psql (Railway):
```bash
psql $DATABASE_URL -c "SELECT COUNT(*) as total, MAX(basedamage) as max_dmg FROM items WHERE quality_new='ADMIN'"
```

### Resultado Esperado:
```
 total | max_dmg 
-------+---------
    12 |  250000
```

---

## Listar Todos os Itens de Admin

```sql
SELECT 
    id, 
    name, 
    basedamage, 
    basedefense,
    CASE slot_id
        WHEN 0 THEN 'consumable'
        WHEN 1 THEN 'amulet'
        WHEN 2 THEN 'head'
        WHEN 3 THEN 'legs'
        WHEN 4 THEN 'chest'
        WHEN 5 THEN 'feet'
        WHEN 6 THEN 'weapon'
        WHEN 7 THEN 'ring'
        WHEN 8 THEN 'shield'
    END as slot
FROM items 
WHERE quality_new = 'ADMIN' 
ORDER BY slot_id, basedamage DESC;
```

---

## Se Nada Foi Adicionado

### 1. Verificar se as Migrations Foram Executadas

Checar os logs do bot ao iniciar:
```
[MIG] ▶ Found 3 migration file(s)
[MIG] ▶ Running: 000_add_depth_quality_columns.sql
[MIG] ✔ Migration applied
[MIG] ▶ Running: 001_tier_to_depth_migration.sql
[MIG] ✔ Migration applied
[MIG] ▶ Running: 002_add_admin_items.sql
[MIG] ✔ Migration applied
```

### 2. Executar Manualmente

Se as migrations não rodaram automaticamente:

```bash
# Ordem correta:
psql $DATABASE_URL < db/migrations/000_add_depth_quality_columns.sql
psql $DATABASE_URL < db/migrations/001_tier_to_depth_migration.sql
psql $DATABASE_URL < db/migrations/002_add_admin_items.sql
```

### 3. Verificar Colunas Existem

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'items' 
AND column_name IN ('depth_new', 'quality_new');
```

Deve retornar:
```
  column_name  |     data_type      
---------------+-------------------
 depth_new     | integer
 quality_new   | character varying
```

### 4. Força Inserção Manual (Último Recurso)

Se nada funcionar, execute diretamente:
```bash
psql $DATABASE_URL < db/seeds/populate_admin_items.sql
```

---

## Ordem de Execução das Migrations

1. **000_add_depth_quality_columns.sql** ← Adiciona colunas depth_new/quality_new
2. **001_tier_to_depth_migration.sql** ← Migra dados tier→depth
3. **002_add_admin_items.sql** ← Insere 12 itens de admin

Se a ordem estiver errada, a #2 e #3 vão falhar!

---

## Troubleshooting

### Erro: "column depth_new does not exist"
**Causa:** Migration 000 não foi executada  
**Solução:** Execute manualmente:
```bash
psql $DATABASE_URL < db/migrations/000_add_depth_quality_columns.sql
```

### Erro: "duplicate key value violates unique constraint"
**Causa:** Itens de admin já existem  
**Solução:** Isso é normal! A migration é idempotente - não duplica itens.

### Comando /giveadminitem não aparece
**Causa:** Cog admin não carregou  
**Solução:** Verificar logs para erro ao carregar cog admin.adminrpg

### Items inseridos mas comando retorna vazio
**Causa:** Nome do item errado ou query incorreta  
**Solução:** Verificar lista de nomes exatos:
```sql
SELECT name FROM items WHERE quality_new = 'ADMIN' ORDER BY name;
```

---

## Scripts de Debug

### Ver todas as migrations executadas:
```sql
-- Se existir tabela de tracking (futuro):
SELECT * FROM migrations_log ORDER BY executed_at DESC;
```

### Ver status completo do schema:
```sql
SELECT 
    (SELECT COUNT(*) FROM items) as total_items,
    (SELECT COUNT(*) FROM items WHERE depth_new IS NOT NULL) as with_depth,
    (SELECT COUNT(*) FROM items WHERE quality_new IS NOT NULL) as with_quality,
    (SELECT COUNT(*) FROM items WHERE quality_new = 'ADMIN') as admin_items;
```

### Resultado esperado:
```
 total_items | with_depth | with_quality | admin_items 
-------------+------------+--------------+-------------
        1260 |       1260 |         1260 |          12
```

---

**Criado:** 08/02/2026  
**Última Atualização:** Sistema de migrations v2.0
