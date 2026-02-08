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

## 🎒 Sistema de Slots de Equipamento

O bot utiliza um sistema de **8 slots** para equipamentos:

| Slot ID | Nome | Emoji | Descrição |
|---------|------|-------|-----------|
| **1** | Amuleto | 🎒 | Amuleto mágico com buffs especiais |
| **2** | Cabeça | 🪖 | Capacetes, elmos e proteção craniana |
| **3** | Pernas | 👖 | Calças, grevas e proteção das pernas |
| **4** | Mão Principal | ⚔️ | Arma principal (espadas, machados, etc) |
| **5** | Torso | 🛡️ | Armadura de peito, couraças e proteção do torso |
| **6** | Mão Secundária | 🗡️ | Arma secundária ou escudo |
| **7** | Costas | 🧥 | Capas, mantos e proteção das costas |
| **8** | Pés | 👢 | Botas, sapatilhas e proteção dos pés |
| **9** | Especial | 📦 | Itens especiais e consumíveis |

### Itens Iniciais

Ao iniciar com `/rpg start`, o jogador recebe automaticamente itens equipáveis de **Tier 1** para os seguintes slots (na ordem de equipamento):
1. ⚔️ Mão Principal (Slot 4)
2. 🛡️ Torso (Slot 5)
3. 🪖 Cabeça (Slot 2)
4. 👖 Pernas (Slot 3)
5. 👢 Pés (Slot 8)
6. 🗡️ Mão Secundária (Slot 6)

### Uso no Sistema

- **Equipamentos (Equipment)**: Armas e armaduras são equipadas nos slots 1-8
- **Crafting**: O sistema de craft organiza itens por slot
- **Inventário**: Itens são categorizados por seu `slot_id`
- **Combate**: Power score é calculado baseado nos itens equipados

## � Arquitetura de Geração de Itens (Desacoplamento Total)

### Filosofia: Autorização vs Definição

O sistema de itens opera sob um princípio fundamental de **desacoplamento total** entre comando público e dados reais.

### Como Funciona o `/genitem`

O comando `/genitem` aceita **apenas informações mínimas e simbólicas**:

```
/genitem nome:"Capacete da Persistência Suprema" 
         slot_id:2 
         start_tier:6 
         start_subtier:3 
         end_tier:6 
         end_subtier:3 
         is_collectible:False
```

**Nenhum valor de dano, defesa, buff, scaling ou efeito especial definido no comando é considerado fonte de verdade.**

O comando `/genitem` **nunca define poder**. Ele apenas **autoriza a existência** do item.

### A Fonte de Verdade: Arquivo `Itens`

Durante a inicialização do sistema, o código procura um arquivo de configuração chamado **`data/Itens.enc`**, armazenado em formato **criptografado com Fernet**.

#### Arquivos Implementados ✅

- **`data/itens_config.json`**: Template JSON com estrutura de items (exemplo)
- **`data/Itens.enc`**: Arquivo criptografado produzido por `scripts/encrypt_items.py`
- **`utils/item_integrity.py`**: Módulo de criptografia/descriptografia (fail-safe)
- **`services/item_resolver.py`**: Serviço de resolução de atributos em runtime
- **`scripts/encrypt_items.py`**: Script para gerar `Itens.enc` a partir do JSON

#### Estrutura do JSON (antes de criptografar)

```json
{
  "slot_id": {
    "item_identifier": {
      "base_damage": 2500,
      "base_defense": 0,
      "scaling": {
        "str": 3.5,
        "dex": 2.0,
        "int": 1.5
      },
      "buffs": [
        {"type": "lifesteal", "value": 12},
        {"type": "crit_damage", "value": 50}
      ],
      "flags": {
        "legendary": true,
        "tradeable": false,
        "quest_item": true
      }
    }
  }
}
```

**Organização:**
1. **Primeiro nível**: `slot_id` (1-9, ex: "4" para Mão Principal)
2. **Segundo nível**: Identificador único (ex: "lamina_abissal")
3. **Terceiro nível**: Atributos e regras (nunca expostos ao usuário)

#### Novo Comando `/genitem` (v2.0) ⚔️

**Antes (Inseguro)**:
```bash
/genitem nome:"Espada" base_damage:500 base_defense:0 slot_id:4
         # ↑ Admin definia poder aqui (fórmula exposta!)
```

**Agora (Seguro - Desacoplado)**:
```bash
/genitem nome:"Lâmina Abissal" item_identifier:"lamina_abissal" slot_id:4 start_tier:1 end_tier:8
                                ↑ Busca atributos em Itens.enc (criptografado)
```

#### Fluxo de Geração

```
┌─────────────────────────────────────────────────────────┐
│ Admin executa: /genitem nome:"X" item_identifier:"id"   │
│ → Apenas AUTORIZA (sem definir poder)                   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Sistema busca item_identifier em data/Itens.enc         │
│ → Descriptografa com key de Fernet                      │
│ → Valida schema JSON                                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Carrega atributos reais em memória:                     │
│  • base_damage: 2500 (do arquivo, não do comando!)      │
│  • base_defense: 0                                      │
│  • scaling, buffs, flags secretas                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Cria items no BD com atributos reais (tier 1.0 → 8.4)   │
│ ✅ Usuário recebe: "Lâmina Abissal T1.0"                │
│ ❌ Usuário NÃO vê: valores, fórmulas, flags ocultas     │
└─────────────────────────────────────────────────────────┘
```

### Segurança Implementada

#### Proteção do Arquivo
- ✅ **Criptografia Fernet**: Padrão da biblioteca `cryptography`
- ✅ **Armazenado em `data/Itens.enc`**: Formato binário, não legível
- ✅ **Schema validado**: Rejeita JSON inválido silenciosamente
- ✅ **Versionado**: Regenerado via `scripts/encrypt_items.py`

#### Proteção do Runtime
- ✅ **Fail-safe**: Arquivo corrompido → retorna `None`, sistema não quebra
- ✅ **Sem logs expostos**: Erros não revelam estrutura interna
- ✅ **Cache em memória**: Sem acesso direto ao arquivo pela aplicação
- ✅ **Validação em dois níveis**: Schema JSON + integridade Fernet

#### Proteção do Comando
- ✅ **Sem parâmetros de poder**: Admin não define `base_damage` ou `base_defense`
- ✅ **Apenas `item_identifier`**: Referência ao arquivo criptografado
- ✅ **Confirmação visual**: Mostra atributos resolvidos antes de confirmar

### Fail-Safe

Se o arquivo `data/Itens.enc` **não existir, estiver corrompido ou inválido**:

✅ Sistema continua funcionando  
❌ Comando `/genitem` retorna erro: "Item 'X' não encontrado"  
📝 Logs registram falha sem expor valores  
🔐 Nenhum dado sensível é revelado

### Setup Rápido

1. **Editar** `data/itens_config.json` com seus items
2. **Gerar arquivo criptografado**:
   ```bash
   python scripts/encrypt_items.py
   ```
3. **Usar o comando**:
   ```bash
   /genitem nome:"Lâmina Abissal" item_identifier:"lamina_abissal" slot_id:4
   ```

### Vantagens do Sistema

| Aspecto | Antes | Agora |
|---------|-------|-------|
| **Definição de Poder** | Comando Discord | Arquivo criptografado |
| **Exposição de Fórmula** | ❌ Visível | ✅ Protegida |
| **Anti-Cheat** | ❌ Fraco | ✅ Forte |
| **Atualização de Balanceamento** | ⚠️ Requer redeploy | ✅ Rápida (novo Itens.enc) |
| **Auditoria** | ❌ Expõe valores | ✅ Protegida |
| **Performance** | ⚠️ Cálculos repetidos | ✅ Cache em memória |

### Documentação Completa

Veja [docs/ITEM_GENERATION_SYSTEM.md](docs/ITEM_GENERATION_SYSTEM.md) para:
- API Reference detalhada
- Exemplos de configuração
- Troubleshooting
- Segurança da chave de criptografia
- Próximas melhorias

## �🔧 Scripts Úteis

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
