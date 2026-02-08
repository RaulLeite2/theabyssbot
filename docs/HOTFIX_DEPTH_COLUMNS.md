# 🔧 Correção Urgente: Erros de Coluna e Cog

## 🚨 Problemas Identificados

1. ❌ **Coluna `depth_new` não existe** - Causa erro no shop.py
2. ⚠️ **Cog sanctuary não carregou** - Provavelmente devido ao erro anterior

## ✅ Solução Rápida (3 Passos)

### Passo 1: Executar Migration

Execute a migration para criar as colunas necessárias:

```bash
python scripts/run_depth_quality_migration.py
```

**O que isso faz:**
- ✅ Adiciona colunas `depth_new` e `quality_new` à tabela `items`
- ✅ Migra dados antigos (tier/subtier → depth_new/quality_new)
- ✅ Cria índices para performance
- ✅ Mostra estatísticas de migração

**Saída esperada:**
```
✅ Migration executada com sucesso!
Total de itens: [número]
Itens com depth_new: [número]
Itens com quality_new: [número]
```

### Passo 2: Reiniciar o Bot

Após a migration, reinicie o bot:

```bash
# Se estiver usando Railway/Docker
railway up

# Ou se estiver rodando localmente
python main.py
```

### Passo 3: Verificar Logs

Confirme que não há mais erros:

```
✅ Deve aparecer: "Cog carregado: cogs.guild.sanctuary"
✅ Não deve aparecer: "UndefinedColumnError: column 'depth_new' does not exist"
```

## 📋 Checklist de Verificação

Após executar os passos acima, verifique:

- [ ] Migration executada sem erros
- [ ] Bot reiniciado
- [ ] Cog `sanctuary` carregado com sucesso
- [ ] Comandos `/sanc` funcionando
- [ ] Shop resetando sem erros
- [ ] Comandos `/wiki guildas` e `/wiki sanctuaries` funcionando

## 🔍 Diagnóstico Detalhado

### Erro 1: `column "depth_new" does not exist`

**Arquivo afetado:** `cogs/economy/shop.py` linha 289

**Causa:** 
O código foi atualizado para usar o novo sistema de depth/quality, mas as colunas não foram criadas no banco de dados.

**Query problemática:**
```sql
SELECT id, depth_new, quality_new
FROM items
WHERE depth_new <= 5
```

**Solução:**
Executar a migration que cria as colunas.

### Erro 2: Cog sanctuary não carregado

**Aviso no log:** 
```
[WARNING] theabyssbot: Alguns cogs nao foram carregados: ['cogs.guild.sanctuary']
```

**Causa provável:**
O bot falhou ao carregar o cog `sanctuary` porque outros cogs (como `shop`) falharam primeiro devido ao erro de coluna. Quando o shop falha, o bot pode marcar outros cogs como não carregados.

**Solução:**
Corrigir o erro do shop (Passo 1) e reiniciar (Passo 2).

## 🆘 Se Ainda Houver Problemas

### Problema: Migration falha com "relation 'items' does not exist"

**Solução:**
```bash
# Execute o schema principal primeiro
psql $DATABASE_URL < db/schema.sql
```

### Problema: Sanctuary ainda não carrega após migration

**Diagnóstico:**
```bash
# Verifique erros de sintaxe Python
python -m py_compile cogs/guild/sanctuary.py
```

**Verifique erros no log:**
```bash
# Procure por traceback específico do sanctuary
grep -A 20 "sanctuary" bot.log
```

### Problema: Comandos /ho não funcionam

**Causa:**
Os comandos `/ho` são aliases de `/sanc`. Se o cog sanctuary não carregar, nenhum dos dois funciona.

**Solução:**
Certifique-se que o cog sanctuary carregou vendo nos logs:
```
[INFO] theabyssbot: Cog carregado: cogs.guild.sanctuary
```

## 📝 Arquivos Criados/Modificados

- ✅ `db/migrations/add_depth_quality_columns.sql` - SQL da migration
- ✅ `scripts/run_depth_quality_migration.py` - Script Python de migration
- ✅ `db/migrations/README_DEPTH_QUALITY.md` - Documentação detalhada
- ✅ `cogs/guild/sanctuary.py` - Novo cog (substitui hideout.py)
- ✅ `cogs/wiki/wiki.py` - Novos comandos `/wiki guildas` e `/wiki sanctuaries`

## 🎯 Após Correção

Uma vez corrigido, você pode:

1. ✅ Testar comandos de sanctuary: `/sanc create`, `/sanc info`, `/sanc list`
2. ✅ Testar wiki: `/wiki guildas`, `/wiki sanctuaries`
3. ✅ Testar shop: Deve resetar automaticamente a cada hora
4. ✅ Testar busca de itens: `/wiki buscar <nome>`

## 💡 Prevenção Futura

Para evitar este tipo de problema:

1. **Sempre execute migrations antes de fazer deploy de código novo**
2. **Use CI/CD para rodar migrations automaticamente**
3. **Teste localmente antes de fazer deploy para produção**
4. **Mantenha um ambiente de staging para testar migrations**

## 📚 Documentação Adicional

- `db/migrations/README_DEPTH_QUALITY.md` - Guia completo de migration
- `docs/REFACTORING_VERIFICATION.md` - Status geral do refactoring
- `docs/MIGRATIONS.md` - Guia geral de migrations (se existir)

## 🆘 Suporte

Se os problemas persistirem após seguir este guia:

1. Verifique os logs completos do bot
2. Execute o script de verificação de tabelas: `python scripts/verify_tables.py`
3. Verifique se o DATABASE_URL está correto no .env
4. Confirme que o PostgreSQL está rodando e acessível
