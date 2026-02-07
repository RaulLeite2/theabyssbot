# 🏆 Sistema de Ligas de Guildas

## Visão Geral
Sistema competitivo de ranking de guildas baseado em fama acumulada durante temporadas mensais (30 dias).

---

## 📊 Ligas e Requisitos

| Liga | Ícone | Fama Necessária | Recompensa de Temporada |
|------|-------|-----------------|-------------------------|
| **Bronze** | 🥉 | 0+ | 10,000 gold |
| **Prata** | 🥈 | 50,000+ | 50,000 gold |
| **Ouro** | 🥇 | 150,000+ | 150,000 gold |
| **Platina** | 💎 | 350,000+ | 350,000 gold |
| **Diamante** | 💠 | 750,000+ | 750,000 gold |
| **Mestre** | 🔷 | 1,500,000+ | 1,500,000 gold |
| **Cristal** | 🔮 | 3,000,000+ (Topo Mundial) | 3,000,000 gold |

---

## ⚙️ Como Funciona

### Ganho de Fama para Guilda
- **50% da fama pessoal** dos membros vai automaticamente para a guilda
- Todas as atividades que geram fama pessoal contribuem:
  - ⚔️ **Arena**: +25 por vitória → +12.5 para guilda
  - 💀 **Combate**: +50 dungeon, +200 world boss → +25/+100 para guilda
  - 🔨 **Crafting**: +10 base + tier × 5 → metade para guilda
  - 🗺️ **Exploração**: +5 base + tier × 2 → metade para guilda
  - 💎 **Comércio**: 1 ponto/50 gold → metade para guilda

### Temporadas
- **Duração**: 30 dias (1 mês)
- **Reset automático**: A cada fim de temporada
- **Histórico salvo**: Rankings finais são preservados
- **Recompensas**: Distribuídas automaticamente ao fim da temporada

### Progressão de Liga
- A liga da guilda é **atualizada automaticamente** quando a fama atinge os requisitos
- Sistema de promoção instantânea (não precisa esperar fim da temporada)
- Quanto mais membros ativos, mais rápido a guilda sobe

---

## 📋 Comandos

### `/league ranking [limit]`
Ver ranking atual de guildas da temporada
- **limit**: Número de guildas para mostrar (5-25, padrão: 10)
- Mostra: Posição, Liga, Nome, Fama, Número de membros
- Tempo restante da temporada

### `/league info`
Ver informações detalhadas da sua guilda
- Liga atual e ícone
- Fama da temporada e total
- Posição no ranking
- Tempo restante da temporada
- Recompensa da liga atual
- Fama necessária para próxima liga
- Top 5 contribuidores da temporada

### `/league history`
Ver histórico de temporadas da guilda
- Últimas 10 temporadas
- Posição final de cada temporada
- Liga alcançada
- Fama final

### `/league contribution`
Ver sua contribuição pessoal para a guilda
- Fama contribuída na temporada
- Porcentagem da fama total da guilda
- Posição no ranking de contribuidores
- Última vez que contribuiu

### `/guild info`
Informações da guilda (atualizado com liga)
- Agora mostra: Liga atual, Rank e Fama

---

## 🎯 Estratégias

### Para Guildas
1. **Recrute membros ativos** - Mais membros = mais fama
2. **Organize eventos** - World boss raids, arena tournaments
3. **Incentive crafting** - Itens de tier alto dão muita fama
4. **Explore zonas de tier alto** - Mais fama por exploração

### Para Membros
1. **Seja consistente** - Faça atividades diariamente
2. **Foque no que você é bom** - Especialize-se (PvP, PvE, Crafting, etc)
3. **Trabalhe em equipe** - Participe de raids e eventos da guilda
4. **Suba de nível** - Atividades de tier alto geram mais fama

---

## 🏅 Sistema de Contribuição

### Tracking Individual
- Cada membro tem sua contribuição rastreada
- Ranking interno de contribuidores
- Histórico de última contribuição
- Porcentagem de participação

### Top Contribuidores
- Exibido em `/league info`
- Top 5 membros da temporada
- Incentiva competição saudável dentro da guilda

---

## ⏰ Fim de Temporada

### Processo Automático
1. **Finalização**: Ranking final é salvo
2. **Recompensas**: Distribuídas baseado na liga final
3. **Reset**: Fama da temporada zerada
4. **Nova Temporada**: Todas as guildas voltam para Bronze

### Histórico Preservado
- Rankings finais salvos permanentemente
- Consulta através de `/league history`
- Estatísticas de performance ao longo do tempo

---

## 💡 Dicas

1. **Atividade constante é chave** - Membros inativos não contribuem
2. **Qualidade > Quantidade** - Membros muito ativos são mais valiosos
3. **Diversifique atividades** - Não foque apenas em uma categoria
4. **Planeje para fim de temporada** - Últimos dias são cruciais
5. **Comunique-se** - Coordene esforços com a guilda

---

## 🔧 Detalhes Técnicos

### Database
- **guild_seasons**: Tabela de temporadas
- **guild_season_rankings**: Histórico de rankings
- **guild_leagues**: Definições de ligas
- **guild_fame_contributions**: Contribuições individuais

### Funções PostgreSQL
- `start_new_guild_season()`: Inicia nova temporada
- `add_guild_fame()`: Adiciona fama à guilda
- `update_guild_league()`: Atualiza liga baseado na fama
- `finalize_guild_season()`: Finaliza temporada e salva rankings

### Task Automática
- Verificação a cada 1 hora se a temporada acabou
- Finalização e início automáticos
- Sem necessidade de intervenção manual

---

## 📈 Exemplos de Progressão

### Guilda Pequena (5 membros ativos)
- ~500 fama/dia por membro = 2,500/dia
- ~75,000 fama/mês → **Liga Prata/Ouro**

### Guilda Média (15 membros ativos)
- ~500 fama/dia por membro = 7,500/dia
- ~225,000 fama/mês → **Liga Ouro/Platina**

### Guilda Grande (30 membros muito ativos)
- ~1,000 fama/dia por membro = 30,000/dia
- ~900,000 fama/mês → **Liga Diamante/Mestre**

### Guilda Elite (50 membros extremamente ativos)
- ~2,000 fama/dia por membro = 100,000/dia
- ~3,000,000 fama/mês → **Liga Cristal (Topo Mundial)**

---

## 🎮 Integração com Sistemas Existentes

### Compatível com:
- ✅ Sistema de Fama Pessoal
- ✅ Sistema de NPCs e Reputação
- ✅ Sistema de Arena
- ✅ Sistema de Combate (Dungeons, World Boss)
- ✅ Sistema de Crafting
- ✅ Sistema de Exploração
- ✅ Sistema de Comércio (Shop, Auction)
- ✅ Sistema de Alianças

### Não Afeta:
- Gold pessoal
- XP e Level
- Inventário
- Equipment
- Hideouts

---

## 🚀 Futuras Expansões Possíveis

1. **Guerras de Liga**: Guildas da mesma liga podem batalhar
2. **Bônus de Liga**: Buffs baseados na liga (exp, gold, drop)
3. **Territórios**: Guildas de liga alta podem conquistar zonas
4. **Torneios Inter-Liga**: Eventos especiais entre ligas
5. **Títulos de Guilda**: Títulos cosméticos por liga alcançada
