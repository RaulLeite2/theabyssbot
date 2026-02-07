# Sistema de Migrations 🔄

## Visão Geral
O bot agora possui um sistema automático de migrations que executa e remove arquivos SQL de migration durante a inicialização.

## Como Funciona

### 1. Detecção Automática
Durante a inicialização do bot (`setup_hook`), o sistema:
- Procura por arquivos `db/migration_*.sql`
- Ordena alfabeticamente para execução determinística
- Executa cada migration em sequência

### 2. Verificação de Execução
Antes de executar uma migration, o sistema verifica:
- ✅ Se o arquivo está vazio → remove imediatamente
- ✅ Se a migration já foi aplicada → remove o arquivo
- ✅ Se precisa ser executada → executa e depois remove

### 3. Remoção Automática
Após execução bem-sucedida, o arquivo de migration é **automaticamente removido** do disco.

## Criando uma Nova Migration

### Passo 1: Criar o arquivo
Crie um arquivo SQL em `db/` com o prefixo `migration_`:

```
db/migration_add_nova_coluna.sql
db/migration_create_new_table.sql
db/migration_20260109_exemplo.sql
```

### Passo 2: Escrever o SQL
```sql
-- ═══════════════════════════════════════════════════════════
-- MIGRATION: Descrição da mudança
-- Data: 2026-01-09
-- ═══════════════════════════════════════════════════════════

-- Seu código SQL aqui
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS new_field TEXT DEFAULT NULL;

-- ═══════════════════════════════════════════════════════════
-- FIM DA MIGRATION
-- ═══════════════════════════════════════════════════════════
```

### Passo 3: Reiniciar o bot
O bot executará automaticamente a migration na próxima inicialização.

## Exemplo de Migration

### Arquivo: `db/migration_add_collectible.sql`
```sql
-- Adicionar coluna is_collectible à tabela items
ALTER TABLE items 
ADD COLUMN IF NOT EXISTS is_collectible BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN items.is_collectible IS 'Indica se o item é um recurso coletável';

CREATE INDEX IF NOT EXISTS idx_items_collectible 
ON items(is_collectible) 
WHERE is_collectible = TRUE;
```

## Logs do Sistema

### Migration Pendente
```
🔄 Encontradas 1 migration(s) pendente(s)
⚙️  Executando migration: migration_add_collectible.sql
✅ Migration migration_add_collectible.sql executada com sucesso
🗑️  Arquivo migration_add_collectible.sql removido
```

### Migration Já Aplicada
```
🔄 Encontradas 1 migration(s) pendente(s)
⚙️  Executando migration: migration_add_collectible.sql
✅ Migration migration_add_collectible.sql já foi aplicada anteriormente
🗑️  Removendo arquivo de migration...
```

### Nenhuma Migration
```
✅ Nenhuma migration pendente
```

### Erro na Migration
```
🔄 Encontradas 1 migration(s) pendente(s)
⚙️  Executando migration: migration_erro.sql
❌ Erro ao executar migration migration_erro.sql: column "invalid" does not exist
```
**Nota:** Se houver erro, o arquivo **NÃO** é removido para permitir correção.

## Boas Práticas

### ✅ Fazer
- Usar `IF NOT EXISTS` ou `ADD COLUMN IF NOT EXISTS` para idempotência
- Incluir comentários explicativos
- Testar a migration localmente antes de fazer push
- Usar nomes descritivos: `migration_add_collectible.sql`

### ❌ Evitar
- Migrations sem `IF NOT EXISTS` (podem falhar se executadas 2x)
- Migrations muito grandes (quebrar em partes menores)
- Remover migrations manualmente (deixe o sistema fazer isso)
- Migrations com `DROP TABLE` sem verificação

## Estrutura do Código

### main.py
```python
async def run_migrations(self):
    """Executa migrations pendentes e remove arquivos após execução"""
    import glob
    
    migration_files = glob.glob("db/migration_*.sql")
    
    if not migration_files:
        print("✅ Nenhuma migration pendente")
        return
    
    for migration_file in sorted(migration_files):
        # Verifica se já foi executada
        # Executa se necessário
        # Remove o arquivo após sucesso
```

### Verificação de Execução
O sistema verifica se uma migration já foi aplicada checando se a coluna existe:

```python
column_exists = await conn.fetchval("""
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'items' 
        AND column_name = 'is_collectible'
    )
""")
```

## Ordem de Execução no Bot

1. **Conecta ao banco de dados** (`await self.db.connect()`)
2. **Executa schema.sql** (`await self.pools()`)
3. **Executa migrations pendentes** (`await self.run_migrations()`) ⭐ **NOVO**
4. **Carrega cogs**
5. **Sincroniza slash commands**

## FAQ

### P: E se eu quiser manter o arquivo de migration?
**R:** O sistema foi projetado para remover automaticamente. Se quiser manter um histórico, versione no Git antes de rodar o bot.

### P: Posso executar migrations manualmente?
**R:** Sim! Use o script `setup_hubs.py` ou execute diretamente no banco:
```bash
psql $DATABASE_URL < db/migration_add_collectible.sql
```

### P: O que acontece se uma migration falhar?
**R:** O arquivo NÃO é removido e o erro é logado. Corrija o SQL e reinicie o bot.

### P: Posso ter múltiplas migrations ao mesmo tempo?
**R:** Sim! O sistema executa em ordem alfabética:
```
migration_01_add_column.sql
migration_02_create_table.sql
migration_03_add_index.sql
```

### P: Como reverter uma migration?
**R:** Crie uma nova migration que desfaz as mudanças:
```sql
-- migration_revert_collectible.sql
ALTER TABLE items DROP COLUMN IF EXISTS is_collectible;
```

## Migrations Atuais

### ✅ Aplicadas e Removidas
- `migration_add_collectible.sql` - Adiciona coluna is_collectible em items

### 📝 Planejadas
- Nenhuma migration pendente no momento

## Integração com Deploy

### Railway/Heroku
Quando fizer push para produção:
1. Git push inclui os arquivos `migration_*.sql`
2. Bot reinicia automaticamente
3. Migrations são executadas
4. Arquivos são removidos
5. Bot fica operacional

### Backup de Segurança
Antes de executar migrations importantes, faça backup do banco:
```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

## Vantagens do Sistema

✅ **Automático** - Sem necessidade de executar scripts manualmente  
✅ **Seguro** - Verifica se já foi executado antes de aplicar  
✅ **Limpo** - Remove arquivos após execução  
✅ **Rastreável** - Logs completos de cada execução  
✅ **Idempotente** - Pode ser executado múltiplas vezes com segurança  
✅ **Determinístico** - Ordem alfabética garantida
