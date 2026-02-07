# DB Query - Executor de Comandos SQL 🗄️

Ferramenta de linha de comando para executar queries SQL diretamente no banco de dados PostgreSQL.

## 🚀 Instalação

```bash
pip install tabulate
```

Ou:

```bash
pip install -r requirements.txt
```

## 📖 Uso Básico

### Executar uma Query
```bash
python db_query.py "SELECT * FROM users LIMIT 5"
```

### Executar um Arquivo SQL
```bash
python db_query.py -f db/migration_npc_system.sql
```

### Ver Ajuda
```bash
python db_query.py --help
```

## 📝 Exemplos Práticos

### SELECT - Consultas

**Ver todos os usuários:**
```bash
python db_query.py "SELECT discord_id, level, zona_id FROM users LIMIT 10"
```

**Ver hubs disponíveis:**
```bash
python db_query.py "SELECT nome, tier, is_hub FROM zone WHERE is_hub = TRUE"
```

**Ver reputação de um usuário:**
```bash
python db_query.py "SELECT npc_id, reputation, title FROM npc_reputation WHERE user_id = 123456789"
```

**Ver Mercador Viajante ativo:**
```bash
python db_query.py "SELECT * FROM traveling_merchant WHERE is_active = TRUE"
```

**Ver top 10 jogadores mais ricos:**
```bash
python db_query.py "SELECT user_id, gold FROM economy ORDER BY gold DESC LIMIT 10"
```

### UPDATE - Modificações

**Adicionar ouro a um usuário:**
```bash
python db_query.py "UPDATE economy SET gold = gold + 10000 WHERE user_id = 123456789"
```

**Alterar level de um usuário:**
```bash
python db_query.py "UPDATE users SET level = 50 WHERE discord_id = 123456789"
```

**Adicionar reputação com NPC:**
```bash
python db_query.py "UPDATE npc_reputation SET reputation = reputation + 500 WHERE user_id = 123456789 AND npc_id = 'npc_blacksmith_01'"
```

### INSERT - Criar Registros

**Criar reputação inicial com NPC:**
```bash
python db_query.py "INSERT INTO npc_reputation (user_id, npc_id, reputation) VALUES (123456789, 'npc_blacksmith_01', 500)"
```

**Adicionar ouro inicial:**
```bash
python db_query.py "INSERT INTO economy (user_id, gold) VALUES (123456789, 5000)"
```

**Criar um hub:**
```bash
python db_query.py "INSERT INTO zone (nome, tier, is_hub, is_hideout, permanent) VALUES ('Nova Capital', 1, TRUE, FALSE, TRUE)"
```

### DELETE - Remover Registros

**Remover reputação:**
```bash
python db_query.py "DELETE FROM npc_reputation WHERE user_id = 123456789 AND npc_id = 'npc_blacksmith_01'"
```

**Limpar Mercadores expirados:**
```bash
python db_query.py "DELETE FROM traveling_merchant WHERE is_active = FALSE"
```

### DDL - Criar/Modificar Estruturas

**Criar tabela de teste:**
```bash
python db_query.py "CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT, created_at TIMESTAMP DEFAULT NOW())"
```

**Adicionar coluna:**
```bash
python db_query.py "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP"
```

**Remover tabela:**
```bash
python db_query.py "DROP TABLE IF EXISTS test"
```

## 🔧 Recursos

### ✅ Tipos de Query Suportados
- **SELECT** - Exibe resultados em tabela formatada
- **INSERT** - Mostra resultado da inserção
- **UPDATE** - Mostra número de linhas afetadas
- **DELETE** - Mostra número de linhas removidas
- **CREATE/ALTER/DROP** - Executa comandos DDL
- **Arquivos SQL** - Executa arquivo completo

### 📊 Formatação de Resultados
- Queries SELECT mostram dados em formato de tabela
- Colunas alinhadas automaticamente
- Suporte para múltiplas linhas
- Contagem de resultados

### 🛡️ Segurança
- Carrega DATABASE_URL do .env automaticamente
- Tratamento de erros com mensagens claras
- Suporte a prepared statements (params)

## 📋 Comandos Úteis para The Abyss

### Verificar Sistema de NPCs
```bash
# Ver todos NPCs e reputações
python db_query.py "SELECT u.discord_id, nr.npc_id, nr.reputation, nr.title FROM npc_reputation nr JOIN users u ON u.discord_id = nr.user_id ORDER BY nr.reputation DESC LIMIT 20"

# Ver quem tem mais reputação com Gorak
python db_query.py "SELECT user_id, reputation, title FROM npc_reputation WHERE npc_id = 'npc_blacksmith_01' ORDER BY reputation DESC LIMIT 10"
```

### Verificar Mercador Viajante
```bash
# Ver se está ativo
python db_query.py "SELECT tm.spawn_id, z.nome, tm.spawned_at, tm.despawn_at FROM traveling_merchant tm JOIN zone z ON z.zone_id = tm.zone_id WHERE tm.is_active = TRUE"

# Ver inventário do mercador
python db_query.py "SELECT tmi.*, i.name FROM traveling_merchant_inventory tmi JOIN items i ON i.id = tmi.item_id WHERE spawn_id = 1"
```

### Verificar Economia
```bash
# Top 10 mais ricos
python db_query.py "SELECT e.user_id, e.gold, u.level FROM economy e JOIN users u ON u.discord_id = e.user_id ORDER BY e.gold DESC LIMIT 10"

# Total de ouro no sistema
python db_query.py "SELECT SUM(gold) as total_gold, COUNT(*) as total_users FROM economy"
```

### Verificar Zonas e Hubs
```bash
# Listar todos hubs
python db_query.py "SELECT zone_id, nome, tier, is_hub FROM zone WHERE is_hub = TRUE ORDER BY tier"

# Contar jogadores por zona
python db_query.py "SELECT z.nome, COUNT(u.discord_id) as players FROM zone z LEFT JOIN users u ON u.zona_id = z.zone_id GROUP BY z.zone_id, z.nome ORDER BY players DESC LIMIT 10"
```

### Debug e Manutenção
```bash
# Ver últimas interações com NPCs
python db_query.py "SELECT * FROM npc_dialogues ORDER BY created_at DESC LIMIT 20"

# Limpar diálogos antigos (mais de 7 dias)
python db_query.py "DELETE FROM npc_dialogues WHERE created_at < NOW() - INTERVAL '7 days'"

# Ver tabelas do banco
python db_query.py "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
```

## ⚠️ Avisos Importantes

### Comandos Perigosos
```bash
# ❌ NÃO EXECUTE sem backup!
python db_query.py "DROP TABLE users"
python db_query.py "DELETE FROM economy"
python db_query.py "TRUNCATE users CASCADE"
```

### Antes de Modificações Grandes
1. **Faça backup do banco de dados**
2. **Teste em ambiente de desenvolvimento**
3. **Use transações quando possível**
4. **Verifique duas vezes antes de executar**

## 🐛 Tratamento de Erros

O script mostra erros de forma clara:

```bash
❌ Erro ao executar query:
   PostgresSyntaxError: syntax error at or near "SELCT"
```

Erros comuns:
- **DATABASE_URL não encontrada**: Verifique seu arquivo .env
- **Syntax error**: Verifique a sintaxe SQL
- **Permission denied**: Verifique permissões do usuário do banco
- **Connection error**: Verifique se o banco está acessível

## 💡 Dicas

1. **Aspas no Windows**: Use aspas duplas para a query
   ```bash
   python db_query.py "SELECT * FROM users"
   ```

2. **Strings dentro da query**: Use aspas simples
   ```bash
   python db_query.py "SELECT * FROM zone WHERE nome = 'Capital do Abismo'"
   ```

3. **Queries longas**: Use arquivos SQL
   ```bash
   python db_query.py -f minha_query.sql
   ```

4. **Visualizar estrutura**: Use DESCRIBE ou information_schema
   ```bash
   python db_query.py "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users'"
   ```

5. **Testar antes de modificar**: Use SELECT primeiro
   ```bash
   # Primeiro veja o que vai ser afetado
   python db_query.py "SELECT * FROM users WHERE level < 5"
   
   # Depois modifique
   python db_query.py "UPDATE users SET level = 5 WHERE level < 5"
   ```

## 🔗 Integração com Sistema de Migrations

Execute migrations manualmente:
```bash
python db_query.py -f db/migration_npc_system.sql
python db_query.py -f db/migration_add_collectible.sql
```

Verificar se migration foi aplicada:
```bash
python db_query.py "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'items' AND column_name = 'is_collectible')"
```

## 📚 Exemplos Avançados

### Queries Complexas com JOINs
```bash
python db_query.py "SELECT u.discord_id, u.level, e.gold, z.nome as zona FROM users u LEFT JOIN economy e ON e.user_id = u.discord_id LEFT JOIN zone z ON z.zone_id = u.zona_id WHERE u.level > 10 ORDER BY e.gold DESC LIMIT 20"
```

### Agregações
```bash
python db_query.py "SELECT npc_id, AVG(reputation) as avg_rep, MAX(reputation) as max_rep, COUNT(*) as total_users FROM npc_reputation GROUP BY npc_id ORDER BY avg_rep DESC"
```

### Subqueries
```bash
python db_query.py "SELECT * FROM users WHERE discord_id IN (SELECT user_id FROM npc_reputation WHERE reputation > 1000)"
```

## 🎯 Casos de Uso Específicos

### Dar recompensa a todos jogadores
```bash
python db_query.py "UPDATE economy SET gold = gold + 5000"
```

### Resetar reputações de um NPC
```bash
python db_query.py "UPDATE npc_reputation SET reputation = 0 WHERE npc_id = 'npc_blacksmith_01'"
```

### Spawnar Mercador Viajante manualmente
```bash
python db_query.py "INSERT INTO traveling_merchant (zone_id, despawn_at, is_active) VALUES (1, NOW() + INTERVAL '30 minutes', TRUE)"
```

### Ver estatísticas do servidor
```bash
python db_query.py "SELECT COUNT(DISTINCT discord_id) as total_users, AVG(level) as avg_level, MAX(level) as max_level FROM users"
```

## 🔄 Alternativa: psql

Se preferir usar psql nativo:
```bash
psql $DATABASE_URL -c "SELECT * FROM users LIMIT 5"
```

Mas o `db_query.py` oferece:
- ✅ Formatação automática de tabelas
- ✅ Tratamento de erros melhor
- ✅ Suporte a arquivos SQL
- ✅ Sintaxe mais simples
- ✅ Multiplataforma (Windows/Linux/Mac)
