# The Abyss - Discord RPG Bot 🕳️

Bot de RPG para Discord com sistema complexo de exploração, combate, economia e NPCs.

## 📁 Estrutura do Projeto

```
The Abyss/
├── main.py                 # Arquivo principal do bot
├── requirements.txt        # Dependências Python
├── runtime.txt            # Versão do Python para Railway
├── Procfile              # Configuração Railway
├── railway.json          # Configuração Railway
├── .env                  # Variáveis de ambiente (não commitado)
│
├── cogs/                 # Módulos do bot (comandos)
│   ├── admin/           # Comandos administrativos
│   ├── arena/           # Sistema de arena PvP
│   ├── economy/         # Shop, auction, economia
│   ├── guild/           # Guilds e hideouts
│   ├── party/           # Sistema de party/raid
│   ├── rpg/             # Comandos principais RPG
│   └── special/         # Eventos especiais (Zahuv)
│
├── db/                   # Banco de dados
│   ├── schema.sql       # Schema principal
│   ├── migration.sql    # Migration atual
│   ├── db.py           # Gerenciador de database
│   └── queries/        # Queries SQL reutilizáveis
│
├── data/                 # Arquivos de dados
│   ├── npcs.json        # NPCs e suas personalidades
│   ├── maps_zahuv.json  # Mapas de Zahuv
│   ├── names.json       # Nomes gerados
│   └── starter_items.txt # Lista de itens iniciais
│
├── scripts/              # Scripts utilitários
│   ├── upload.py        # Executor de SQL
│   ├── setup_hubs.py    # Cria hubs no banco
│   └── run_migration.py # Executa migrations
│
├── config/               # Configurações
│   └── .env.example     # Exemplo de variáveis de ambiente
│
└── docs/                 # Documentação
    ├── COLLECTIBLE_SYSTEM.md
    ├── HUB_SYSTEM.md
    ├── MIGRATIONS.md
    ├── NPC_SYSTEM.md
    ├── DB_QUERY_GUIDE.md
    └── RAILWAY_DEPLOY.md
```

## 🚀 Início Rápido

### 1. Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd "The Abyss"

# Crie ambiente virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt
```

### 2. Configuração

```bash
# Copie o arquivo de configuração
copy config\.env.example .env

# Edite .env e adicione:
# - DATABASE_URL (PostgreSQL público do Railway)
# - DISCORD_TOKEN (token do bot)
```

### 3. Setup do Banco de Dados

```bash
# Execute a migration
python scripts/upload.py db/migration.sql

# Crie hubs iniciais
python scripts/setup_hubs.py
```

### 4. Executar o Bot

```bash
python main.py
```

## 📖 Sistemas Implementados

### 🎮 Core RPG
- **Sistema de Níveis e EXP**
- **Sistema de Equipamentos** (6 slots)
- **Sistema de Inventário**
- **Sistema de Combate**
- **Sistema de Exploração**

### 🌍 Mundo
- **Zonas e Tiers** (1-8)
- **Hubs (Cidades)** com is_hub=TRUE
- **Hideouts** (bases de guild)
- **Mapas de Zahuv** (350 zonas especiais)

### 👥 NPCs e Reputação
- **7 NPCs únicos** com personalidades
- **Sistema de Reputação** (0-10000+)
- **Diálogos interativos**
- **Benefícios por reputação** (descontos, buffs)
- **🌪️ Mercador Viajante** (aparece aleatoriamente!)

### 💰 Economia
- **Sistema de Gold**
- **Shop com NPCs**
- **Sistema de Leilão**
- **Crafting de Itens**
- **Recursos Coletáveis**

### 🏰 Guilds
- **Sistema de Guildas**
- **Alianças entre guilds**
- **Hideouts personalizáveis**
- **Controle de zonas**

### ⚔️ Combate
- **Arena PvP**
- **Party Raids**
- **World Bosses**
- **Dungeons**

## 🔧 Scripts Úteis

### Executar SQL no Banco
```bash
# Query direta
python scripts/upload.py "SELECT * FROM users LIMIT 5"

# Arquivo SQL
python scripts/upload.py db/migration.sql

# Ver ajuda
python scripts/upload.py --help
```

### Criar Hubs
```bash
python scripts/setup_hubs.py
```

### Executar Migration
```bash
python scripts/run_migration.py
```

## 📚 Documentação

Toda documentação está na pasta [`docs/`](docs/):

- **[NPC_SYSTEM.md](docs/NPC_SYSTEM.md)** - Sistema de NPCs e reputação
- **[HUB_SYSTEM.md](docs/HUB_SYSTEM.md)** - Sistema de hubs (cidades)
- **[MIGRATIONS.md](docs/MIGRATIONS.md)** - Sistema de migrations
- **[COLLECTIBLE_SYSTEM.md](docs/COLLECTIBLE_SYSTEM.md)** - Recursos coletáveis
- **[DB_QUERY_GUIDE.md](docs/DB_QUERY_GUIDE.md)** - Guia de queries SQL
- **[RAILWAY_DEPLOY.md](docs/RAILWAY_DEPLOY.md)** - Deploy no Railway

## 🎯 Comandos Principais

### RPG Básico
```
/rpg start          - Inicia sua jornada
/rpg stats          - Ver status
/rpg inventory      - Ver inventário
/rpg equipment      - Ver equipamentos
/rpg goto <zona>    - Viajar para zona
/rpg hub            - Ir para o hub mais próximo
```

### NPCs
```
/npcs               - Lista todos NPCs
/talk <npc>         - Conversar com NPC
/merchant           - Localizar Mercador Viajante
```

### Economia
```
/shop               - Loja
/auction            - Leilão
/craft              - Craftar item
```

### Guild
```
/guild create       - Criar guild
/guild invite       - Convidar membro
/hideout create     - Criar hideout
```

## 🌟 Destaques Únicos

### 🌪️ Mercador Viajante (Zephyr)
- Aparece **aleatoriamente** em hubs (5% chance/15min)
- Fica apenas **30 minutos**
- Vende **itens lendários** exclusivos
- Use `/merchant` para encontrá-lo!

### 🎭 NPCs com Personalidade
Cada NPC tem diálogos únicos:
- **Gorak** (Ferreiro): Ranzinza mas habilidoso
- **Lysandra** (Mercadora): Charmosa e astuta
- **Thaddeus** (Alquimista): Louco genial
- **Morgath** (Encantador): Misterioso
- **Martha** (Estalajadeira): Maternal
- **Raven** (Mercado Negro): Sorrateiro

### 🏆 Sistema de Reputação
- Ganhe pontos interagindo com NPCs
- Desbloquie benefícios incríveis
- Martha pode te **adotar** como filho!
- Morgath ensina **ritual permanente**
- Raven revela **dungeons secretas**

## 🔐 Variáveis de Ambiente

```env
DATABASE_URL=postgresql://user:pass@host:port/db
DISCORD_TOKEN=seu_token_do_discord
```

## 🚂 Deploy no Railway

1. Conecte o repositório GitHub ao Railway
2. Adicione serviço PostgreSQL
3. Configure variáveis de ambiente
4. Deploy automático!

Ver [RAILWAY_DEPLOY.md](docs/RAILWAY_DEPLOY.md) para detalhes.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é privado e proprietário.

## 👨‍💻 Autor

Desenvolvido com ❤️ para criar uma experiência de RPG única no Discord!

---

**Status do Projeto:** 🟢 Ativo e em desenvolvimento

**Última Atualização:** 09/01/2026
