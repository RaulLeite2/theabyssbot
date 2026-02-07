# 🚂 Deploy no Railway - Guia Completo

## 📋 Pré-requisitos
- Conta no [Railway.app](https://railway.app)
- Bot Discord criado no [Discord Developer Portal](https://discord.com/developers/applications)
- Este repositório pronto para deploy

## 🗄️ Passo 1: Configurar PostgreSQL no Railway

1. Acesse seu projeto no Railway
2. Clique em **"+ New"** → **"Database"** → **"Add PostgreSQL"**
3. O Railway criará automaticamente as variáveis:
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`

## 🤖 Passo 2: Deploy do Bot

1. No Railway, clique em **"+ New"** → **"GitHub Repo"**
2. Selecione este repositório
3. Railway detectará automaticamente o Python e fará o build

## ⚙️ Passo 3: Configurar Environment Variables

Vá em **Variables** no seu serviço do bot e adicione:

```
DISCORD_TOKEN=seu_token_aqui
DATABASE_URL=${{Postgres.DATABASE_URL}}
ADMIN_IDS=947849382278094880
```

**Importante:** 
- Substitua `seu_token_aqui` pelo token real do seu bot Discord
- `${{Postgres.DATABASE_URL}}` faz referência automática à URL completa do PostgreSQL
- `Postgres` é o nome do serviço do banco (pode ser diferente, verifique no Railway)
- O bot usará `DATABASE_URL` automaticamente no Railway

### 🔧 Para desenvolvimento local (.env):
```
DISCORD_TOKEN=seu_token_aqui
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=postgres
DB_HOST=localhost
ADMIN_IDS=947849382278094880
```

## 🔗 Conectando os Serviços

O Railway detecta automaticamente as conexões entre serviços. Certifique-se de que:
- O bot e o PostgreSQL estão no mesmo projeto
- As variáveis de ambiente estão corretamente referenciadas

## 🚀 Deploy

1. Após configurar as variáveis, o Railway fará o deploy automaticamente
2. Verifique os logs em **"Deployments"** → última build → **"View Logs"**
3. O bot deve aparecer online no Discord em alguns minutos

## 🔍 Verificação

Logs importantes para verificar:
```
✅ Conectado como: NomeDoBot#1234
✅ [DB] ✅ Pool conectado.
✅ ✅ Comandos sincronizados!
```

## ⚠️ Troubleshooting

### Bot não conecta ao banco
- Verifique se as variáveis `DB_*` estão corretas
- Confirme que o PostgreSQL está rodando (ícone verde no Railway)
- Veja os logs do Postgres para erros de conexão

### Bot não fica online
- Verifique o `DISCORD_TOKEN`
- Confirme que os **Intents** estão habilitados no Discord Developer Portal:
  - `PRESENCE INTENT`
  - `SERVER MEMBERS INTENT`
  - `MESSAGE CONTENT INTENT`

### Comandos não aparecem
- Os comandos slash podem levar até 1 hora para aparecerem globalmente
- Para teste imediato, use `guild_ids` no código

## 💰 Custos

- **Hobby Plan (Gratuito):**
  - $5 de crédito mensal
  - Suficiente para bots pequenos/médios
  - PostgreSQL incluído
  
- **Upgrades:** Considere upgrade se o bot crescer muito

## 🔄 Atualizações

Cada push no GitHub triggera um novo deploy automaticamente no Railway.

## 📞 Suporte

- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
