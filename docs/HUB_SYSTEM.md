# Sistema de Hubs 🏛️

## Visão Geral
Hubs são cidades seguras no mundo do The Abyss onde os jogadores podem descansar, comercializar e interagir com NPCs.

## Características dos Hubs

### Identificação
- **is_hub**: `TRUE` - Identifica uma zona como Hub
- **is_hideout**: `FALSE` - Hubs não são hideouts
- **permanent**: `TRUE` - Hubs são permanentes e não podem ser conquistados

### Diferenças entre Zonas

| Tipo | is_hub | is_hideout | permanent | Descrição |
|------|--------|-----------|-----------|-----------|
| **Hub** | `TRUE` | `FALSE` | `TRUE` | Cidade segura, mercado, NPCs |
| **Hideout** | `FALSE` | `TRUE` | `FALSE` | Base de guilda, pode ser conquistada |
| **Zona Normal** | `FALSE` | `FALSE` | Variável | Zona de exploração e combate |

## Comandos Disponíveis

### `/rpg hub`
Transporta o jogador diretamente para o Hub mais próximo (menor tier).

**Funcionalidade:**
- Busca o primeiro hub com `is_hub = TRUE`
- Ordena por tier ascendente (menor tier = mais próximo)
- Atualiza a localização do jogador (zona_id)
- Mostra informações sobre o hub

**Exemplo de uso:**
```
/rpg hub
```

**Resposta:**
```
🏛️ Chegada ao Hub
Você chegou ao Capital do Abismo!

📍 Localização
Tier: ⭐ T1
Tipo: 🏛️ Hub (Cidade Segura)

ℹ️ Sobre Hubs
Hubs são cidades seguras onde você pode:
• Comercializar itens no Mercado
• Descansar e recuperar HP
• Interagir com NPCs e comerciantes
• Aceitar missões especiais
```

### `/rpg goto <zone_name>`
Permite viajar para qualquer zona pelo nome (incluindo hubs).

**Exemplo:**
```
/rpg goto Capital
```

### `/rpg zoneinfo`
Mostra informações detalhadas da zona atual, incluindo se é um hub.

## Criando Hubs

### Via Script Python
Execute o script `setup_hubs.py` para criar hubs de exemplo:

```bash
python setup_hubs.py
```

Este script:
1. Executa a migration `migration_add_collectible.sql`
2. Cria 3 hubs de exemplo (se não existirem)
3. Lista todos os hubs disponíveis

### Via Comando Admin
Use o comando `/adminrpg zonecreate`:

```
/adminrpg zonecreate
  nome: "Capital do Abismo"
  tier: 1
  is_hub: True
  permanent: True
```

### Via SQL Direto
```sql
INSERT INTO zone (nome, tier, is_hub, is_hideout, permanent)
VALUES ('Capital do Abismo', 1, TRUE, FALSE, TRUE);
```

## Hubs de Exemplo

| Nome | Tier | Descrição |
|------|------|-----------|
| Capital do Abismo | 1 | Hub inicial para novos jogadores |
| Cidade de Ferro | 3 | Hub intermediário com melhores comerciantes |
| Citadela Celestial | 5 | Hub avançado para jogadores de alto nível |

## Schema do Banco de Dados

```sql
CREATE TABLE IF NOT EXISTS zone (
    zone_id BIGSERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tier INTEGER NOT NULL CHECK (tier > 0),
    
    is_hub BOOLEAN DEFAULT FALSE,          -- cidade / capital
    is_hideout BOOLEAN DEFAULT FALSE,      -- zona de hideout
    
    owner_guild INT REFERENCES guilds(id),     -- domínio de guild
    owner_alliance INT REFERENCES alliances(id), -- domínio de alliance
    
    permanent BOOLEAN DEFAULT TRUE,        -- se a zona pode mudar dono
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Queries Úteis

### Listar todos os Hubs
```sql
SELECT zone_id, nome, tier
FROM zone
WHERE is_hub = TRUE
ORDER BY tier ASC;
```

### Contar jogadores em cada Hub
```sql
SELECT z.nome, z.tier, COUNT(u.discord_id) as players
FROM zone z
LEFT JOIN users u ON u.zona_id = z.zone_id
WHERE z.is_hub = TRUE
GROUP BY z.zone_id, z.nome, z.tier
ORDER BY z.tier ASC;
```

### Verificar se uma zona é Hub
```sql
SELECT nome, 
       CASE 
           WHEN is_hub THEN '🏛️ Hub'
           WHEN is_hideout THEN '🏰 Hideout'
           ELSE '🌍 Zona Normal'
       END as tipo
FROM zone
WHERE zone_id = 123;
```

## Funcionalidades Futuras

- [ ] Sistema de NPCs específicos por hub
- [ ] Mercado global acessível apenas em hubs
- [ ] Sistema de teleporte entre hubs (fast travel)
- [ ] Eventos exclusivos de hubs (festivais, torneios)
- [ ] Sistema de reputação com hubs
- [ ] Upgrade de hubs baseado em contribuições dos jogadores

## Notas Técnicas

### Performance
- Índice em `is_hub` para queries rápidas
- Hubs são permanent = TRUE para evitar mudança de dono
- Zone_id usado como foreign key em users.zona_id

### Segurança
- Hubs não podem ser transformados em hideouts
- Permanent = TRUE previne conquista por guildas
- Sistema de validação no comando /hub para verificar existência

### Integração
O sistema de hubs está integrado com:
- ✅ Sistema de zonas (zone table)
- ✅ Sistema de viagem (/rpg goto, /rpg hub)
- ✅ Sistema de informações (/rpg zoneinfo)
- ⏳ Sistema de mercado (em desenvolvimento)
- ⏳ Sistema de NPCs (planejado)
