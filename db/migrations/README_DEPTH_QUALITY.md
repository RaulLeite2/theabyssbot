# Migration: depth_new e quality_new

## 🎯 Objetivo

Adicionar as colunas `depth_new` e `quality_new` à tabela `items` para suportar o novo sistema de ranking:

- **depth_new**: Valores de 1 a 8 (equivalentes aos ranks F até SS)
- **quality_new**: COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHIC

## ⚠️ IMPORTANTE

Esta migration **DEVE ser executada antes de reiniciar o bot** após as atualizações de código. Sem estas colunas, o bot falhará ao iniciar com erro:

```
asyncpg.exceptions.UndefinedColumnError: column "depth_new" does not exist
```

## 📋 Pré-requisitos

1. Banco de dados PostgreSQL configurado
2. `DATABASE_URL` definida no arquivo `.env`
3. Python 3.11+ com asyncpg instalado

## 🚀 Como Executar

### Opção 1: Script Automatizado (Recomendado)

```bash
python scripts/run_depth_quality_migration.py
```

Este script:
- ✅ Lê o arquivo SQL de migration
- ✅ Executa no banco de dados
- ✅ Verifica se as colunas foram criadas
- ✅ Migra dados antigos automaticamente
- ✅ Mostra estatísticas de distribuição

### Opção 2: SQL Direto

Se preferir executar manualmente via psql:

```bash
psql $DATABASE_URL < db/migrations/add_depth_quality_columns.sql
```

## 🔍 O que a Migration Faz

### 1. Adiciona Colunas
```sql
ALTER TABLE items ADD COLUMN depth_new INTEGER;
ALTER TABLE items ADD COLUMN quality_new VARCHAR(20);
```

### 2. Cria Índices
```sql
CREATE INDEX idx_items_depth_new ON items(depth_new);
CREATE INDEX idx_items_quality_new ON items(quality_new);
CREATE INDEX idx_items_depth_quality ON items(depth_new, quality_new);
```

### 3. Migra Dados Antigos

**Conversão de tier → depth_new:**
- tier 1-8 → depth 1-8 (direto)
- tier > 8 → depth 8 (cap no máximo)

**Conversão de subtier → quality_new:**
- subtier 1-2 → COMMON
- subtier 3-4 → UNCOMMON
- subtier 5-6 → RARE
- subtier 7-8 → EPIC
- subtier 9 → LEGENDARY
- subtier 10+ → MYTHIC

### 4. Define Valores Padrão

Para itens sem tier/subtier:
- `depth_new` = 1
- `quality_new` = COMMON

## ✅ Verificação

Após executar, você deve ver:

```
✅ Migration concluída!
Total de itens: [número]
Itens com depth_new: [número]
Itens com quality_new: [número]

📊 Distribuição por Depth:
   - Depth 1: X itens
   - Depth 2: X itens
   ...

📊 Distribuição por Quality:
   - COMMON: X itens
   - UNCOMMON: X itens
   - RARE: X itens
   ...
```

## 🔄 Rollback (Se Necessário)

Se algo der errado e você precisar reverter:

```sql
-- Remove as colunas
ALTER TABLE items DROP COLUMN IF EXISTS depth_new;
ALTER TABLE items DROP COLUMN IF EXISTS quality_new;

-- Remove os índices
DROP INDEX IF EXISTS idx_items_depth_new;
DROP INDEX IF EXISTS idx_items_quality_new;
DROP INDEX IF EXISTS idx_items_depth_quality;
```

## 📊 Compatibilidade

- ✅ Mantém colunas antigas (`tier`, `subtier`) intactas
- ✅ Sistema é backward compatible
- ✅ Código faz fallback para tier/subtier se depth_new não existir
- ✅ Não quebra dados legados

## 🐛 Troubleshooting

### Erro: "column already exists"

Isso significa que a migration já foi executada. Você pode:

1. Verificar se as colunas existem:
   ```sql
   SELECT column_name FROM information_schema.columns 
   WHERE table_name='items' AND column_name LIKE '%new';
   ```

2. Se existirem, apenas pule esta migration

### Erro: "relation 'items' does not exist"

Você precisa executar o schema principal primeiro:
```bash
psql $DATABASE_URL < db/schema.sql
```

### Erro: "DATABASE_URL not found"

Certifique-se que o arquivo `.env` existe e contém:
```
DATABASE_URL=postgresql://user:pass@host:port/database
```

## 📝 Arquivos Relacionados

- **Migration SQL**: `db/migrations/add_depth_quality_columns.sql`
- **Script Python**: `scripts/run_depth_quality_migration.py`
- **Populate Items**: `db/seeds/populate_items_depth.sql` (1,248 itens novos)

## 🎯 Próximos Passos

Após executar esta migration:

1. ✅ Reinicie o bot
2. ✅ Verifique logs para confirmar carregamento correto
3. ✅ Teste comandos: `/wiki buscar`, `/shop`, `/genitem`
4. ✅ (Opcional) Execute populate_items_depth.sql para adicionar 1,248 itens novos

## 💡 Notas

- Esta migration é **idempotente** - pode ser executada múltiplas vezes sem problemas
- Os dados antigos (tier/subtier) são preservados
- A conversão é aproximada mas mantém a progressão de poder
- Itens novos devem usar apenas depth_new/quality_new
