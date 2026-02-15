# 🎮 COMANDOS DO THE ABYSS

Guia completo de todos os comandos disponíveis no jogo.

---

## 📋 ÍNDICE

- [🎯 Básicos](#-básicos)
- [🗺️ Exploração](#️-exploração)
- [⚔️ Combate](#️-combate)
- [🎭 NPCs](#-npcs)
- [🛠️ Crafting](#️-crafting)
- [💰 Economia](#-economia)
- [🏰 Guilds & Sanctuary](#-guilds--sanctuary)
- [👥 Party](#-party)
- [🏟️ Arena](#️-arena)
- [📊 Progressão](#-progressão)
- [🎨 Depth System](#-depth-system)
- [📖 Wiki](#-wiki)
- [⚙️ Admin](#️-admin)

---

## 🎯 BÁSICOS

### `/help`
**Descrição:** Ajuda interativa do RPG com menu de categorias  
**Uso:** `/help`  
**Exemplo:** Abre menu com botões para cada sistema do jogo

### `/profile [@jogador]`
**Descrição:** Ver perfil completo de um jogador  
**Parâmetros:**
- `@jogador` (opcional) - Jogador para ver o perfil
**Uso:** 
- `/profile` - Seu próprio perfil
- `/profile @Usuario` - Perfil de outro jogador
**Mostra:** Level, HP, XP, gold, fame, equipamentos, localização

### `/stats`
**Descrição:** Ver suas estatísticas completas (kills, deaths, itens craftados, etc)  
**Uso:** `/stats`  
**Mostra:** Total de kills, mortes, gold ganho, itens craftados, zonas exploradas, trades, etc

---

## 🗺️ EXPLORAÇÃO

### `/rpg start`
**Descrição:** Inicia sua jornada no The Abyss (primeiro comando!)  
**Uso:** `/rpg start`  
**Efeito:** Cria seu personagem e spawna no Hub inicial

### `/rpg zones`
**Descrição:** Lista todas as zonas disponíveis e conectadas  
**Uso:** `/rpg zones`  
**Mostra:** Zonas adjacentes à sua posição, tier, tipo (hub/normal/sanctuary)

### `/rpg travel [zona]`
**Descrição:** Viajar para outra zona  
**Parâmetros:**
- `zona` - Nome da zona de destino
**Uso:** `/rpg travel Floresta Escura`  
**Custo:** Depende da distância

### `/explore`
**Descrição:** Explore a região atual em busca de segredos  
**Uso:** `/explore`  
**Recompensas:** Gold, recursos, itens, chance de portal para Zahuv

### `/explore_portal`
**Descrição:** Entre no portal de Zahuv descoberto (terras distantes)  
**Uso:** `/explore_portal`  
**Requerimento:** Ter descoberto portal com `/explore`

---

## ⚔️ COMBATE

### `/battle hunt [zona]`
**Descrição:** Caçar monstros em uma zona  
**Parâmetros:**
- `zona` (opcional) - Nome da zona para caçar
**Uso:** 
- `/battle hunt` - Caça na zona atual
- `/battle hunt Pântano Sombrio` - Caça em zona específica
**Recompensas:** XP, gold, itens (tier baseado na zona)

### `/battle flee [zona]`
**Descrição:** Fugir do combate e retornar a uma zona segura  
**Parâmetros:**
- `zona` - Nome da zona de fuga
**Uso:** `/battle flee Capital`  
**Efeito:** Teleporte de emergência (pode ter custo)

---

## 🎭 NPCs

### `/npcs`
**Descrição:** Lista todos os NPCs disponíveis nos hubs  
**Uso:** `/npcs`  
**Mostra:** Nome, localização, personalidade, função de cada NPC

### `/talk [npc_name]`
**Descrição:** Conversa com um NPC  
**Parâmetros:**
- `npc_name` - Nome do NPC (ex: Gorak, Lysandra, Martha)
**Uso:** `/talk Gorak`  
**Exemplos de NPCs:**
- **Gorak** - Ferreiro veterano (Hub 1)
- **Lysandra** - Maga estudiosa (Hub 2)
- **Martha** - Taberneira acolhedora (Hub 1)
- **Captain Thorne** - Comandante da guarda (Hub 2)
- **Elder Rowan** - Sábio ancião (Hub 3)
- **Zara** - Comerciante esperta (Hub 3)

**Sistema de Diálogo:**
- NPCs têm personalidades únicas
- Respostas contextuais (hora do dia, nível do jogador, quests completadas)
- Podem dar dicas, quests, ou vender itens especiais

### `/merchant`
**Descrição:** Verifica se o Mercador Viajante está em algum hub  
**Uso:** `/merchant`  
**Efeito:** Mostra localização atual do mercador e itens especiais

---

## 🛠️ CRAFTING

### `/craft [item_name]`
**Descrição:** Abrir interface de crafting  
**Parâmetros:**
- `item_name` (opcional com autocomplete) - Nome do item a craftar
**Uso:** 
- `/craft` - Abre menu geral
- `/craft Espada de Ferro` - Crafta item específico
**Recursos:** Madeira, Pedra, Minério, Fibra, Couro

### `/recipes`
**Descrição:** Ver todas as receitas disponíveis  
**Uso:** `/recipes`  
**Mostra:** Lista completa de receitas, materiais necessários, tier

### `/craftable`
**Descrição:** Ver apenas receitas que você pode craftar agora  
**Uso:** `/craftable`  
**Mostra:** Receitas com recursos suficientes no inventário

### `/myresources`
**Descrição:** Ver seus recursos de crafting  
**Uso:** `/myresources`  
**Mostra:** Quantidade de cada recurso (madeira, pedra, minério, etc)

---

## 💰 ECONOMIA

### `/balance`
**Descrição:** Ver seu saldo de gold  
**Uso:** `/balance`  
**Mostra:** Gold total disponível

### `/bank`
**Descrição:** Consulte seu saldo bancário e informações de juros  
**Uso:** `/bank`  
**Funções:** Depositar, sacar, ver juros acumulados

### `/pay [@jogador] [quantidade]`
**Descrição:** Transferir gold para outro jogador  
**Parâmetros:**
- `@jogador` - Jogador de destino
- `quantidade` - Quantidade de gold
**Uso:** `/pay @Amigo 1000`  
**Taxa:** 5% de taxa de transação

### `/shop`
**Descrição:** Mostra os itens à venda na capital  
**Uso:** `/shop`  
**Mostra:** Itens disponíveis, preços, tier

### `/leaderboard`
**Descrição:** Ver ranking de jogadores por gold, level, fame  
**Uso:** `/leaderboard`  
**Tipos:** Gold, Level, Fame Arena, Fame Combate, Fame Crafting

---

## 🏰 GUILDS & SANCTUARY

### `/guild create [nome]`
**Descrição:** Criar uma guild  
**Parâmetros:**
- `nome` - Nome da guild
**Uso:** `/guild create Cavaleiros do Abismo`  
**Custo:** 10,000 gold

### `/guild invite [@jogador]`
**Descrição:** Convidar jogador para sua guild  
**Uso:** `/guild invite @Jogador`

### `/guild info`
**Descrição:** Ver informações da sua guild  
**Mostra:** Membros, level, gold, território, liga

### `/sanc create [nome]`
**Descrição:** Criar sanctuary (zona da guild)  
**Parâmetros:**
- `nome` - Nome do sanctuary
**Uso:** `/sanc create Fortaleza das Sombras`  
**Requerimento:** Guild level 5+

### `/sanc upgrade [módulo]`
**Descrição:** Melhorar módulos do sanctuary  
**Módulos:**
- `crafting_station` - Estação de craft
- `dungeon_portal` - Portal de dungeon
- `energy` - Energia máxima
- `durability` - Durabilidade
**Uso:** `/sanc upgrade crafting_station`

### `/sanc info`
**Descrição:** Ver informações do sanctuary da guild  
**Mostra:** Level, energia, durabilidade, módulos, power score

---

## 👥 PARTY

### `/party create`
**Descrição:** Criar uma party  
**Uso:** `/party create`  
**Limite:** 5 membros

### `/party invite [@jogador]`
**Descrição:** Convidar jogador para party  
**Uso:** `/party invite @Jogador`

### `/party raid`
**Descrição:** Começar raid em dungeon (requer party completa)  
**Uso:** `/party raid`  
**Recompensas:** Loot compartilhado, XP bônus

---

## 🏟️ ARENA

### `/arena challenge [@oponente] [aposta]`
**Descrição:** Desafiar jogador para arena PvP  
**Parâmetros:**
- `@oponente` - Jogador desafiado
- `aposta` - Quantidade de gold apostado
**Uso:** `/arena challenge @Rival 5000`  
**Resultado:** Vencedor leva tudo

### `/arena leaderboard`
**Descrição:** Ver ranking da arena  
**Uso:** `/arena leaderboard`  
**Mostra:** Top jogadores por vitórias, fame arena

### `/party_arena_challenge [@líder_party]`
**Descrição:** Desafiar outra party para arena  
**Uso:** `/party_arena_challenge @LíderRival`  
**Formato:** 5v5 party battle

---

## 📊 PROGRESSÃO

### `/achievements`
**Descrição:** Veja suas conquistas e progresso  
**Uso:** `/achievements`  
**Categorias:**
- **Explorador:** Descobrir zonas, explorar
- **Guerreiro:** Vitórias em combate, kills
- **Comerciante:** Gold ganho, trades
- **Artesão:** Itens craftados
- **Social:** Guild, party activities

### `/daily`
**Descrição:** Veja suas missões diárias  
**Uso:** `/daily`  
**Recompensas:** Gold, XP, recursos  
**Reset:** Diário às 00:00 UTC

### `/fortune`
**Descrição:** Consulte a Vidente Mística (1x por dia)  
**Uso:** `/fortune`  
**Efeitos:** Buffs temporários (gold, XP, luck, etc) ou debuffs (raramente)  
**Cooldown:** 24 horas

---

## 🎨 DEPTH SYSTEM

O The Abyss usa sistema de **Depth (1-8)** + **Quality (6 níveis)** para itens:

### Depth (Profundidade)
- **D1:** Newbie Zone (15-35 dmg/def)
- **D2:** Beginner (40-80)
- **D3:** Advanced (90-150)
- **D4:** Expert (160-250)
- **D5:** Master (260-380)
- **D6:** Elite (390-550)
- **D7:** Legendary (560-780)
- **D8:** Mythical (790-1200)

### Quality (Qualidade)
- **COMMON** (Comum) - 1.0× multiplier - ⚪
- **UNCOMMON** (Incomum) - 1.2× multiplier - 🟢
- **RARE** (Raro) - 1.5× multiplier - 🔵
- **EPIC** (Épico) - 1.8× multiplier - 🟣
- **LEGENDARY** (Lendário) - 2.2× multiplier - 🟠
- **MYTHIC** (Mítico) - 2.8× multiplier - 🔴

### Rank Display
Itens são exibidos no estilo anime:
- **D1 Common:** F-Rank
- **D3 Rare:** C-Rank
- **D5 Epic:** A-Rank
- **D8 Legendary:** SS-Rank
- **D8 Mythic:** SSS-Rank

### Power Score
Fórmula original do The Abyss:
```
Weapon: (base_damage × 1.5 + depth × 100) × quality_multiplier
Armor: (base_defense × 1.5 + depth × 75) × quality_multiplier
Total: Sum of all equipped items
```

**Exemplo:**
- D8 Mythic Sword (100 dmg): (150 + 800) × 2.8 = **2,660 power**

---

## 📖 WIKI

### `/wiki search [nome]`
**Descrição:** Buscar item na enciclopédia  
**Parâmetros:**
- `nome` - Nome ou trecho do nome do item
**Uso:** `/wiki search espada`  
**Mostra:** Todos os itens que contêm "espada" no nome

### `/wiki item [slot_id] [item_id]`
**Descrição:** Ver detalhes de um item específico  
**Parâmetros:**
- `slot_id` - Slot do item (1-9)
- `item_id` - ID do item
**Uso:** `/wiki item 4 123`

### `/wiki list [slot_id]`
**Descrição:** Listar todos os itens de um slot  
**Parâmetros:**
- `slot_id` - Slot a listar (1=amulet, 2=head, 3=legs, 4=weapon, 5=torso, 6=offhand, 7=back, 8=feet, 9=ring)
**Uso:** `/wiki list 4`  
**Mostra:** Todas as armas disponíveis

### `/wiki browse [slot_id]`
**Descrição:** Navegar itens de um slot com páginas  
**Uso:** `/wiki browse 4`  
**Interface:** Botões < Prev | Next >

### `/wiki analyze [slot_id]`
**Descrição:** Análise estatística de itens (dmg médio, tier distribution)  
**Uso:** `/wiki analyze 4`

---

## 🗡️ ARMAS DISPONÍVEIS

O jogo possui **12 armas únicas** (slot 4):

### Armas Clássicas
1. **Espada Básica** - Balanced (Might 40%, Agility 20%)
2. **Espada de Aço** - Power Fighter (Might 50%, Agility 15%)
3. **Lâmina Sombria** - Crit/Stealth (Agility 50%, Might 30%)
4. **Cajado Arcano** - Pure Mage (Essence 60%)
5. **Machado de Ouro** - Heavy Bruiser (Might 65%)

### Novas Armas
6. **Lança Sombria** - Balanced DPS (Might 35%, Agility 35%) + Armor Pen
7. **Arco Longo** - Ranged Sniper (Agility 55%) + Crit Damage + Range
8. **Martelo de Guerra** - Ultimate Tank (Might 75%!) + HP + Stun
9. **Adaga Venenosa** - Fast Assassin (Agility 60%) + Attack Speed + Poison
10. **Grimório Ancestral** - Ultimate Mage (Essence 75%!) + Mana + CDR
11. **Foice Maldita** - Lifesteal Hybrid (Balanced) + Shadow Damage
12. **Katana Relâmpago** - Speed Fighter (Agility 55%) + Attack Speed + Lightning

Cada arma tem **48 variações** (8 depths × 6 qualities) = **576 armas totais**!

---

## 🎭 STATS DO PERSONAGEM

O The Abyss usa stats originais:

- **MIGHT** (antiga STR) - Força física, dano de armas pesadas
- **AGILITY** (antiga DEX) - Velocidade, crítico, esquiva
- **ESSENCE** (antiga INT) - Poder mágico, mana

**Buffs podem aumentar stats:**
- `might_boost` - +X Might
- `agility_boost` - +X Agility
- `essence_boost` - +X Essence

---

## ⚙️ ADMIN

### `/genitem [nome] [slot] [tier] [subtier]`
**Descrição:** Gera itens de 1.0 até 8.4  
**Requerimento:** Admin only

### `/giveitem [@jogador] [item_id] [quantidade]`
**Descrição:** Concede item ao inventário  
**Requerimento:** Admin only

### `/addgold [@jogador] [quantidade]`
**Descrição:** Adiciona gold  
**Requerimento:** Admin only

### `/teleport [zona_ou_@jogador]`
**Descrição:** Teleporta para uma zona ou jogador  
**Requerimento:** Admin only

### `/spawnevent [zona] [tipo]`
**Descrição:** Cria um evento em uma zona (dungeon, world boss)  
**Requerimento:** Admin only

### `/setlevel [@jogador] [level]`
**Descrição:** Define o level de um jogador  
**Requerimento:** Admin only

### `/giveadminitem [nome_item]`
**Descrição:** Dá um item de admin (stats absurdas para testes)  
**Itens:** Espada do Desenvolvedor, Armadura do Admin, Elmo Omnisciente, etc  
**Requerimento:** Admin only

### `/broadcast [mensagem]`
**Descrição:** Envia mensagem global para todos os jogadores  
**Requerimento:** Admin only

---

## 🎯 QUICK START GUIDE

### Primeiros Passos
1. `/rpg start` - Criar personagem
2. `/help` - Ver tutorial
3. `/explore` - Explorar e ganhar recursos
4. `/battle hunt` - Caçar monstros
5. `/shop` - Comprar equipamentos básicos

### Progredindo
1. `/craft` - Craftar equipamentos melhores
2. `/rpg travel` - Explorar novas zonas
3. `/guild create` - Criar/juntar guild
4. `/daily` - Completar missões diárias
5. `/achievements` - Desbloquear conquistas

### Endgame
1. `/sanc create` - Construir sanctuary
2. `/party raid` - Dungeons em grupo
3. `/arena challenge` - PvP competitivo
4. `/guild league` - Disputar ligas entre guilds
5. Farmear itens **D8 Mythic** (SSS-Rank)

---

## 💡 DICAS

### Economia
- Bank oferece juros passivos (deposite gold!)
- Mercador Viajante vende itens raros (use `/merchant`)
- Venda itens duplicados ou de baixo tier

### Combate
- Equipamentos com quality MYTHIC são 2.8× mais fortes
- Use `/fortune` diariamente para buffs
- Party raids dão XP bônus

### Crafting
- Recursos são obtidos com `/explore`
- Crafting dá Fame de Crafting
- Sanctuary com crafting_station tem bônus

### NPCs
- NPCs dão quests especiais
- Conversar com NPCs pode dar dicas de eventos
- Alguns NPCs vendem itens únicos

---

## 🔗 LINKS ÚTEIS

- **Documentação Completa:** [docs/](../docs/)
- **Sistema de NPC:** [NPC_SYSTEM.md](NPC_SYSTEM.md)
- **Depth System:** [REFACTORING_PLAN.md](REFACTORING_PLAN.md)
- **Migrations:** [MIGRATIONS.md](MIGRATIONS.md)

---

## 📝 CHANGELOG RECENTE

### Janeiro 2025 - Refatoração Completa
- ✅ **Fase 1:** Sistema Depth (1-8) + Quality (6 níveis)
- ✅ **Fase 2:** Hideout renomeado para Sanctuary
- ✅ **Fase 3:** Power Score original (fórmula customizada)
- ✅ **Fase 4:** Stats renomeados (str/dex/int → might/agility/essence)
- ✅ **Novas Armas:** 7 armas adicionadas (total: 12)

**Originalidade:** 100% compliance, zero similaridade com Albion Online

---

**The Abyss Discord RPG Bot**  
© 2025 - Todos os direitos reservados
