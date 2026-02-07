# Variáveis de Ambiente para Railway

Este documento lista todas as variáveis de ambiente necessárias para executar o bot no Railway.

## 🔑 Variáveis Obrigatórias

### 1. DISCORD_TOKEN
- **Descrição**: Token de autenticação do bot do Discord
- **Onde obter**: [Discord Developer Portal](https://discord.com/developers/applications)
- **Exemplo**: `SEU_TOKEN_AQUI_NAO_COMMITE`
- **Usado em**: `main.py`

### 2. DATABASE_URL
- **Descrição**: URL completa de conexão com o banco de dados PostgreSQL
- **Formato**: `postgresql://username:password@host:port/database`
- **Exemplo**: `postgresql://user:senha123@db.railway.app:5432/abyssbot`
- **Usado em**: `db/db.py`, scripts de migração
- **Nota no Railway**: Se você adicionar um PostgreSQL Plugin, o Railway cria essa variável automaticamente

### 3. DB_USER
- **Descrição**: Nome de usuário do banco de dados
- **Exemplo**: `postgres`
- **Usado em**: `db/db.py`
- **Nota**: Pode ser extraído do DATABASE_URL se necessário

### 4. DB_PASSWORD
- **Descrição**: Senha do banco de dados
- **Exemplo**: `senha_super_segura_123`
- **Usado em**: `db/db.py`
- **Nota**: Pode ser extraído do DATABASE_URL se necessário

### 5. DB_NAME
- **Descrição**: Nome do banco de dados
- **Exemplo**: `abyssbot`
- **Usado em**: `db/db.py`
- **Nota**: Pode ser extraído do DATABASE_URL se necessário

### 6. DB_HOST
- **Descrição**: Host/endereço do servidor do banco de dados
- **Exemplo**: `db.railway.app`
- **Usado em**: `db/db.py`
- **Nota**: Pode ser extraído do DATABASE_URL se necessário

## 📝 Como Configurar no Railway

### Método 1: Interface Web (Recomendado)

1. Acesse seu projeto no [Railway Dashboard](https://railway.app/dashboard)
2. Clique no seu serviço
3. Vá para a aba **Variables**
4. Clique em **+ New Variable**
5. Adicione cada variável com seu respectivo valor

### Método 2: Railway CLI

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Adicionar variáveis
railway variables set DISCORD_TOKEN=seu_token_aqui
railway variables set DATABASE_URL=postgresql://user:pass@host:port/db
railway variables set DB_USER=postgres
railway variables set DB_PASSWORD=senha
railway variables set DB_NAME=abyssbot
railway variables set DB_HOST=db.railway.app
```

### Método 3: Arquivo railway.json

O projeto já possui um arquivo `railway.json` que pode conter configurações adicionais.

## 🗄️ Configuração do Banco de Dados no Railway

### Opção 1: PostgreSQL Plugin (Recomendado)

1. No Railway Dashboard, clique em **+ New**
2. Selecione **Database**
3. Escolha **PostgreSQL**
4. O Railway criará automaticamente a variável `DATABASE_URL`
5. Você pode usar referência de variável: `${{Postgres.DATABASE_URL}}`

### Opção 2: Banco Externo

Se você já tem um banco PostgreSQL em outro lugar:

1. Configure todas as variáveis manualmente
2. Use a `DATABASE_URL` do seu provedor externo

## ✅ Checklist de Deploy

Antes de fazer deploy no Railway, verifique:

- [ ] `DISCORD_TOKEN` configurado
- [ ] `DATABASE_URL` configurado
- [ ] PostgreSQL plugin adicionado (ou banco externo configurado)
- [ ] Todas as outras variáveis de DB configuradas (se necessário)
- [ ] Schema do banco foi executado (`db/schema.sql`)
- [ ] Build rodando sem erros

## 🔍 Verificação das Variáveis

Você pode verificar se as variáveis estão configuradas corretamente:

```python
# Em qualquer arquivo Python
import os

print("DISCORD_TOKEN:", "✅" if os.getenv("DISCORD_TOKEN") else "❌")
print("DATABASE_URL:", "✅" if os.getenv("DATABASE_URL") else "❌")
print("DB_USER:", "✅" if os.getenv("DB_USER") else "❌")
print("DB_PASSWORD:", "✅" if os.getenv("DB_PASSWORD") else "❌")
print("DB_NAME:", "✅" if os.getenv("DB_NAME") else "❌")
print("DB_HOST:", "✅" if os.getenv("DB_HOST") else "❌")
```

Ou use o script de verificação:

```bash
python scripts/verify_tables.py
```

## 🚨 Segurança

⚠️ **NUNCA comite suas variáveis de ambiente no Git!**

- Use o arquivo `.env` apenas para desenvolvimento local
- Adicione `.env` no `.gitignore`
- Use variáveis de ambiente do Railway para produção
- Rotacione tokens regularmente
- Use senhas fortes para o banco de dados

## 📚 Referências

- [Documentação Railway - Variables](https://docs.railway.app/develop/variables)
- [Discord.py - Bot Token](https://discordpy.readthedocs.io/en/stable/discord.html)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)

## 🆘 Troubleshooting

### Bot não inicia
- Verifique se o `DISCORD_TOKEN` está correto
- Confirme que o token não foi regenerado no Discord Developer Portal

### Erro de conexão com banco
- Verifique se o `DATABASE_URL` está correto
- Confirme que o PostgreSQL plugin está rodando
- Verifique as credenciais de acesso

### Tabelas não existem
- Execute o schema primeiro: a aplicação faz isso automaticamente na inicialização
- Verifique os logs de migração

### Migrações falhando
- Veja os logs completos no Railway
- Execute migrações manualmente se necessário
- Verifique se o schema base foi executado

---

**Última atualização**: 06/02/2026
