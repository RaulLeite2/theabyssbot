# 🔧 Fix: Coluna EXP Ausente

## 🐛 Problema

O bot está crashando com o erro:
```
asyncpg.exceptions.UndefinedColumnError: column "exp" does not exist
```

Isso acontece quando um jogador vence uma batalha e o sistema tenta dar experiência (XP).

## ✅ Solução

A coluna `exp` precisa ser adicionada na tabela `users`.

### Opção 1: Via Railway Dashboard (RECOMENDADO)

1. Acesse o Railway Dashboard
2. Vá em seu projeto > PostgreSQL
3. Clique em "Query" ou "Data"
4. Execute o seguinte SQL:

```sql
ALTER TABLE users
ADD COLUMN IF NOT EXISTS exp INTEGER DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_users_exp ON users(exp);
```

### Opção 2: Via psql Local

Se tiver acesso local ao banco:

```bash
psql $DATABASE_URL
```

Depois execute:
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS exp INTEGER DEFAULT 0;
CREATE INDEX IF NOT EXISTS idx_users_exp ON users(exp);
```

### Opção 3: Via Script Python (no servidor)

Copie o arquivo `migration_add_exp.sql` para o servidor e rode:

```bash
python scripts/run_migration.py db/migration_add_exp.sql
```

## 📝 O que a migration faz?

1. **Adiciona coluna `exp`**: Armazena a experiência atual do jogador
2. **Define valor padrão**: 0 XP para todos os jogadores
3. **Cria índice**: Otimiza queries de experiência

## 🎮 Como funciona o sistema de XP?

### Ganho de Experiência
- 🗡️ **Batalhas**: Jogadores ganham XP ao derrotar inimigos
- 📊 **Fórmula**: XP necessário para subir = `level * 100`
  - Level 1→2: 100 XP
  - Level 2→3: 200 XP
  - Level 3→4: 300 XP

### Progressão de Nível
```python
# Exemplo: Jogador level 2 com 50 XP
# Ganha 180 XP de uma batalha
# Total: 50 + 180 = 230 XP

# Level 2 precisa de 200 XP para subir
# 230 - 200 = 30 XP sobram
# Jogador sobe para level 3 com 30 XP
```

## 🔍 Verificar se funcionou

Após executar a migration, teste:

1. Entre em uma batalha: `/battle`
2. Derrote o inimigo
3. Verifique seu perfil: `/profile`
4. Você deve ver seu XP aumentar

## 🗂️ Arquivos Relacionados

- `db/migration_add_exp.sql` - Migration criada
- `cogs/rpg/rpg.py` - Função `give_exp()` (linha 358)
- `cogs/rpg/rpg_ui.py` - `end_battle()` que chama give_exp (linha 279)
- `db/schema.sql` - Schema principal (precisa ser atualizado manualmente)

## 📋 Atualizar Schema Principal

Após executar a migration, atualize também o `schema.sql` para novos deploys:

Em `db/schema.sql`, na tabela `users`, adicione:
```sql
CREATE TABLE IF NOT EXISTS users (
    discord_id BIGINT PRIMARY KEY,
    level INTEGER DEFAULT 1,
    exp INTEGER DEFAULT 0,  -- ← ADICIONE ESTA LINHA
    base_hp INTEGER DEFAULT 100,
    current_hp INTEGER DEFAULT 100,
    zona_id BIGINT REFERENCES zone(zone_id)
);
```

## ✅ Checklist

- [ ] Executar migration no banco de dados
- [ ] Atualizar schema.sql
- [ ] Testar batalha no Discord
- [ ] Verificar logs para confirmar que não há mais erros
- [ ] Commit das mudanças no Git

## 🚀 Após o Fix

O sistema de batalha funcionará corretamente e jogadores poderão:
- ✅ Ganhar XP em batalhas
- ✅ Subir de nível
- ✅ Ver progressão no `/profile`
