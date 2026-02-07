# Estrutura do Banco de Dados

Esta pasta contém todos os arquivos relacionados ao banco de dados do projeto.

## 📁 Estrutura de Pastas

```
db/
├── migrations/          # Arquivos de migração SQL
├── seeds/              # Scripts de população de dados
├── queries/            # Queries SQL reutilizáveis
├── schema.sql          # Schema principal do banco
└── db.py              # Módulo Python para conexão com DB
```

## 📂 Descrição das Pastas

### `migrations/`
Contém todos os arquivos de migração do banco de dados. As migrações são executadas automaticamente pelo bot na inicialização.

- **Padrão de nomenclatura**: `migration_*.sql`
- **Execução**: Automática através do `main.py`
- **Remoção**: Arquivos são removidos após execução bem-sucedida

**Arquivos:**
- `migration.sql` - Migração base (NPCs e recursos coletáveis)
- `migration_achievements_dailies.sql` - Sistema de conquistas e missões diárias
- `migration_add_exp.sql` - Adiciona sistema de experiência
- `migration_add_fame.sql` - Adiciona sistema de fama
- `migration_guild_league.sql` - Sistema de ligas de guildas
- `migration_hideout_items.sql` - Sistema de items do hideout
- `migration_hideout_update.sql` - Atualizações do hideout
- `migration_resources_tier.sql` - Sistema de tiers de recursos

### `seeds/`
Scripts para popular o banco de dados com dados iniciais.

**Arquivos:**
- `populate_hideout_recipes.sql` - Receitas de crafting do hideout

### `queries/`
Queries SQL reutilizáveis organizadas por módulo.

**Arquivos:**
- `users.sql` - Queries relacionadas a usuários

### `schema.sql`
Schema principal do banco de dados contendo todas as definições de tabelas.

**Tabelas principais:**
- `guilds` - Guildas
- `guild_members` - Membros de guildas
- `alliances` - Alianças entre guildas
- `zone` - Zonas do jogo
- `users` - Usuários/jogadores
- `items` - Items do jogo
- E muitas outras...

### `db.py`
Módulo Python para gerenciamento de conexão com o banco de dados.

**Variáveis de ambiente necessárias:**
- `DATABASE_URL` - URL completa de conexão
- `DB_USER` - Usuário do banco
- `DB_PASSWORD` - Senha do banco
- `DB_NAME` - Nome do banco de dados
- `DB_HOST` - Host do banco de dados

## 🚀 Como Usar

### Executar Schema Inicial
O schema é executado automaticamente na inicialização do bot através do método `pools()`.

### Executar Migration Manual
```python
python scripts/run_migration.py
```

### Executar Script de População
```bash
psql -U username -d database_name -f db/seeds/populate_hideout_recipes.sql
```

## ⚠️ Observações

- As migrações são executadas automaticamente e removidas após sucesso
- Sempre teste migrações em ambiente de desenvolvimento primeiro
- Faça backup do banco de dados antes de executar migrações em produção
- Use transações quando possível para permitir rollback em caso de erro
