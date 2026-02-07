-- =========================
-- GUILDS (criar primeiro, pois zone depende)
-- =========================
CREATE TABLE IF NOT EXISTS guilds (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    leader_id BIGINT NOT NULL,
    level INT DEFAULT 1,
    gold BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- GUILD MEMBERS
-- =========================
CREATE TABLE IF NOT EXISTS guild_members (
    user_id BIGINT PRIMARY KEY,
    guild_id INT REFERENCES guilds(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member' -- leader, officer, member
);

-- =========================
-- ALLIANCES
-- =========================
CREATE TABLE IF NOT EXISTS alliances (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    tag TEXT UNIQUE NOT NULL CHECK (LENGTH(tag) = 3),  -- 3-letter alliance tag like [VME] or [WRK]
    founder_guild_id INT REFERENCES guilds(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- GUILD ALLIANCES
-- =========================
CREATE TABLE IF NOT EXISTS guild_alliances (
    guild_id INT REFERENCES guilds(id) ON DELETE CASCADE,
    alliance_id INT REFERENCES alliances(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (guild_id, alliance_id)
);

-- =========================
-- ZONAS
-- =========================
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

-- =========================
-- ITENS (criar ANTES de users)
-- =========================
CREATE TABLE IF NOT EXISTS items (
	id BIGSERIAL PRIMARY KEY,
	name TEXT NOT NULL,

	basedamage INT,
	basedefense INT,

	tier INT NOT NULL,
	subtier INT NOT NULL,

	slot_id INT NOT NULL,
	is_collectible BOOLEAN DEFAULT FALSE,

	created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- HIDEOUTS (criar ANTES de users)
-- =========================
CREATE TABLE IF NOT EXISTS hideouts (
    id SERIAL PRIMARY KEY,
    guild_id INT NOT NULL REFERENCES guilds(id) ON DELETE CASCADE,
    alliance_id INT REFERENCES alliances(id) ON DELETE SET NULL,
    zone_id BIGINT NOT NULL REFERENCES zone(zone_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    energy INT DEFAULT 100,
    max_energy INT DEFAULT 100,
    durability INT DEFAULT 100,
    max_durability INT DEFAULT 100,
    "level" INT DEFAULT 1,
    last_recharge TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- USUÁRIOS
-- =========================
CREATE TABLE IF NOT EXISTS users (
    discord_id BIGINT PRIMARY KEY,
    level INTEGER DEFAULT 1,
    exp INTEGER DEFAULT 0,
    base_hp INTEGER DEFAULT 100,
    current_hp INTEGER DEFAULT 100,
    zona_id BIGINT REFERENCES zone(zone_id),
    in_hideout_id INT REFERENCES hideouts(id) ON DELETE SET NULL,
    previous_zone_id BIGINT REFERENCES zone(zone_id) ON DELETE SET NULL,
    equipped_weapon BIGINT REFERENCES items(id) ON DELETE SET NULL,
    equipped_armor BIGINT REFERENCES items(id) ON DELETE SET NULL,
    fame_arena BIGINT DEFAULT 0,
    fame_combat BIGINT DEFAULT 0,
    fame_crafting BIGINT DEFAULT 0,
    fame_exploration BIGINT DEFAULT 0,
    fame_trading BIGINT DEFAULT 0
);

-- =========================
-- BUFF DOS ITENS
-- =========================
CREATE TABLE IF NOT EXISTS item_buffs (
    id SERIAL PRIMARY KEY,
    item_id INT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL,       -- exemplo: "healing", "crit", "defense"
    valor INT NOT NULL,       -- valor do buff (ex: 50 de cura, 10% de crítico = 10)
    duracao INT DEFAULT 0     -- duração em segundos (0 = permanente)
);

-- =========================
-- INVENTÁRIO
-- =========================
CREATE TABLE IF NOT EXISTS inventory (
    user_id BIGINT REFERENCES users(discord_id) ON DELETE CASCADE,
    item_id BIGINT REFERENCES items(id),
    tier INT NOT NULL,
    exp INT NOT NULL DEFAULT 0,
    quantity INT DEFAULT 1,
    PRIMARY KEY(user_id, item_id, tier)
);

-- =========================
-- EVENTOS
-- =========================
CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    type SMALLINT NOT NULL, -- 1 = Dungeon | 2 = WorldBoss
    zone_id BIGINT NOT NULL REFERENCES zone(zone_id) ON DELETE CASCADE,
    reward JSONB NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- =========================
-- EQUIPAMENTOS
-- =========================
CREATE TABLE IF NOT EXISTS equipment (
    user_id BIGINT REFERENCES users(discord_id) ON DELETE CASCADE,
    slot_id INTEGER NOT NULL,
    item_id BIGINT REFERENCES items(id),
    tier INTEGER NOT NULL,
    PRIMARY KEY (user_id, slot_id)
);

-- =========================
-- CITY SHOP
-- =========================
CREATE TABLE IF NOT EXISTS city_shop (
    item_id INT NOT NULL REFERENCES items(id),
    price INT NOT NULL,
    PRIMARY KEY (item_id)
);

-- =========================
-- GUILD LOGS
-- =========================
CREATE TABLE IF NOT EXISTS guild_logs (
    id SERIAL PRIMARY KEY,

    guild_id INT NOT NULL
        REFERENCES guilds(id)
        ON DELETE CASCADE,

    user_id BIGINT,              -- quem causou a ação (pode ser NULL)
    action TEXT NOT NULL,         -- descrição do evento

    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- UPDATES PARA TABELA GUILDS (via migrations)
-- =========================
ALTER TABLE guilds 
ADD COLUMN IF NOT EXISTS season_fame BIGINT DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_fame BIGINT DEFAULT 0,
ADD COLUMN IF NOT EXISTS current_league VARCHAR(20) DEFAULT 'Bronze',
ADD COLUMN IF NOT EXISTS league_icon VARCHAR(10) DEFAULT '🥉';

-- =========================
-- UPDATES PARA TABELA HIDEOUTS (via migrations)
-- =========================
ALTER TABLE hideouts
ADD COLUMN IF NOT EXISTS has_crafting_station BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_dungeon_portal BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS dungeon_cooldown TIMESTAMP;

-- =========================
-- SHOP
-- =========================
CREATE TABLE IF NOT EXISTS shop (
    id BIGSERIAL PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    price BIGINT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- LEILÃO
-- =========================
CREATE TABLE IF NOT EXISTS auction (
    auction_id BIGSERIAL PRIMARY KEY,
    seller_id BIGINT NOT NULL REFERENCES users(discord_id),
    item_id BIGINT NOT NULL REFERENCES items(id),
    amount INT NOT NULL,
    price BIGINT NOT NULL,  -- current highest bid
    highest_bidder_id BIGINT REFERENCES users(discord_id),
    ends_at TIMESTAMP NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'ended', 'cancelled')),
    created_at TIMESTAMP DEFAULT NOW()
);,
    tier INT DEFAULT 1

-- =========================
-- ECONOMY
-- =========================
CREATE TABLE IF NOT EXISTS economy (
    user_id BIGINT PRIMARY KEY REFERENCES users(discord_id) ON DELETE CASCADE,
    gold BIGINT NOT NULL DEFAULT 0
);

-- =========================
-- RECURSOS DE CRAFTING
-- =========================
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,  -- madeira, pedra, minério, fibra, pelego
    emoji TEXT NOT NULL,
    description TEXT
);

-- =========================
-- INVENTÁRIO DE RECURSOS
-- =========================
CREATE TABLE IF NOT EXISTS user_resources (
    user_id BIGINT REFERENCES users(discord_id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources(id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, resource_id)
);

-- =========================
-- RECEITAS DE CRAFT
-- =========================
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    item_id BIGINT REFERENCES items(id) ON DELETE CASCADE,
    tier INT NOT NULL,
    subtier INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- INGREDIENTES DAS RECEITAS
-- =========================
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INT REFERENCES recipes(id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources(id) ON DELETE CASCADE,
    quantity INT NOT NULL,
    PRIMARY KEY (recipe_id, resource_id)
);

-- =========================
-- INSERIR RECURSOS BÁSICOS
-- =========================
INSERT INTO resources (name, emoji, description) VALUES
    ('Madeira', '🪵', 'Madeira rústica coletada de árvores'),
    ('Pedra', '🪨', 'Pedra bruta extraída de rochas'),
    ('Minério', '⛏️', 'Minério de ferro para forjar armas'),
    ('Fibra', '🧵', 'Fibras vegetais para tecer armaduras'),
    ('Pelego', '🦌', 'Pele de animais para proteção')
ON CONFLICT (name) DO NOTHING;

-- =========================
-- TABELAS DE ACHIEVEMENTS E DAILY QUESTS
-- =========================
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL,
    category TEXT NOT NULL,
    requirement_type TEXT NOT NULL,
    requirement_amount INT NOT NULL,
    reward_gold INT DEFAULT 0,
    reward_item_id BIGINT REFERENCES items(id) ON DELETE SET NULL,
    reward_fame INT DEFAULT 0,
    is_hidden BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_achievements (
    user_id BIGINT REFERENCES users(discord_id) ON DELETE CASCADE,
    achievement_id INT REFERENCES achievements(id) ON DELETE CASCADE,
    progress INT DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    PRIMARY KEY (user_id, achievement_id)
);

CREATE TABLE IF NOT EXISTS daily_quests (
    id SERIAL PRIMARY KEY,
    quest_type TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL,
    requirement_amount INT NOT NULL,
    reward_gold INT DEFAULT 0,
    reward_exp INT DEFAULT 0,
    reward_fame INT DEFAULT 0,
    difficulty TEXT DEFAULT 'medium'
);

CREATE TABLE IF NOT EXISTS user_daily_quests (
    user_id BIGINT REFERENCES users(discord_id) ON DELETE CASCADE,
    quest_id INT REFERENCES daily_quests(id) ON DELETE CASCADE,
    progress INT DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, quest_id)
);

CREATE TABLE IF NOT EXISTS user_fortune (
    user_id BIGINT PRIMARY KEY REFERENCES users(discord_id) ON DELETE CASCADE,
    fortune_type TEXT,
    buff_type TEXT,
    buff_amount NUMERIC(5,2) DEFAULT 1.0,
    expires_at TIMESTAMP,
    last_fortune_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_stats (
    user_id BIGINT PRIMARY KEY REFERENCES users(discord_id) ON DELETE CASCADE,
    total_kills INT DEFAULT 0,
    total_deaths INT DEFAULT 0,
    total_gold_earned BIGINT DEFAULT 0,
    total_items_crafted INT DEFAULT 0,
    total_zones_explored INT DEFAULT 0,
    total_trades INT DEFAULT 0,
    total_resources_collected INT DEFAULT 0,
    total_distance_traveled INT DEFAULT 0,
    strongest_enemy_defeated TEXT,
    rarest_item_found TEXT,
    longest_survival_time INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- TABELAS DE FAMA E TÍTULOS
-- =========================
CREATE TABLE IF NOT EXISTS fame_history (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    fame_type VARCHAR(20) NOT NULL,
    amount INT NOT NULL,
    reason TEXT,
    gained_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fame_titles (
    title_id SERIAL PRIMARY KEY,
    title_name VARCHAR(100) NOT NULL UNIQUE,
    fame_type VARCHAR(20) NOT NULL,
    required_fame BIGINT NOT NULL,
    icon VARCHAR(10),
    description TEXT
);

-- Inserir títulos de fama por categoria
INSERT INTO fame_titles (title_name, fame_type, required_fame, icon, description) VALUES
('Novato da Arena', 'arena', 0, '⚔️', 'Iniciante nas batalhas de arena'),
('Gladiador', 'arena', 10000, '🗡️', 'Lutador experiente da arena'),
('Campeão', 'arena', 100000, '🏆', 'Campeão reconhecido da arena'),
('Lenda Viva', 'arena', 1000000, '👑', 'Lenda imortal das arenas'),
('Aprendiz de Batalha', 'combat', 0, '⚔️', 'Começando a jornada de combate'),
('Caçador Veterano', 'combat', 50000, '🎯', 'Caçador experiente de monstros'),
('Massacre Vivo', 'combat', 500000, '💀', 'Terror dos monstros'),
('Dizimador', 'combat', 5000000, '☠️', 'Destruidor de legiões'),
('Aprendiz Artesão', 'crafting', 0, '🔨', 'Iniciante nas artes da criação'),
('Artesão Habilidoso', 'crafting', 25000, '⚒️', 'Criador de itens de qualidade'),
('Mestre Forjador', 'crafting', 250000, '🛠️', 'Mestre nas artes da forja'),
('Artífice Lendário', 'crafting', 2500000, '✨', 'Criador de obras-primas'),
('Explorador Curioso', 'exploration', 0, '🗺️', 'Descobrindo o mundo'),
('Desbravador', 'exploration', 30000, '🧭', 'Desbravador de terras desconhecidas'),
('Cartógrafo Mestre', 'exploration', 300000, '📍', 'Mapeador de regiões perdidas'),
('Pioneiro Eterno', 'exploration', 3000000, '🌟', 'Descobridor de segredos ancestrais'),
('Comerciante Novato', 'trading', 0, '💰', 'Começando nos negócios'),
('Mercador Astuto', 'trading', 20000, '💎', 'Negociante habilidoso'),
('Magnata', 'trading', 200000, '👑', 'Mestre do comércio'),
('Imperador Mercantil', 'trading', 2000000, '💸', 'Domínio absoluto do mercado')
ON CONFLICT (title_name) DO NOTHING;

-- =========================
-- TABELAS DE LIGA DE GUILDAS
-- =========================
CREATE TABLE IF NOT EXISTS guild_seasons (
    season_id SERIAL PRIMARY KEY,
    season_number INT NOT NULL,
    start_date TIMESTAMP NOT NULL DEFAULT NOW(),
    end_date TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'ended')),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(season_number)
);

CREATE TABLE IF NOT EXISTS guild_season_rankings (
    id SERIAL PRIMARY KEY,
    season_id INT NOT NULL REFERENCES guild_seasons(season_id),
    guild_id INT NOT NULL REFERENCES guilds(id),
    final_fame BIGINT NOT NULL,
    final_league VARCHAR(20) NOT NULL,
    final_rank INT NOT NULL,
    rewards_claimed BOOLEAN DEFAULT FALSE,
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS guild_leagues (
    league_name VARCHAR(20) PRIMARY KEY,
    min_fame BIGINT NOT NULL,
    icon VARCHAR(10) NOT NULL,
    color VARCHAR(7) NOT NULL,
    rank_order INT NOT NULL,
    season_reward_gold BIGINT DEFAULT 0,
    description TEXT
);

-- Inserir ligas
INSERT INTO guild_leagues (league_name, min_fame, icon, color, rank_order, season_reward_gold, description) VALUES
('Bronze', 0, '🥉', '#CD7F32', 1, 10000, 'Liga inicial - todas as guildas começam aqui'),
('Prata', 50000, '🥈', '#C0C0C0', 2, 50000, 'Liga intermediária para guildas ativas'),
('Ouro', 150000, '🥇', '#FFD700', 3, 150000, 'Liga avançada para guildas dedicadas'),
('Platina', 350000, '💎', '#E5E4E2', 4, 350000, 'Liga de elite para guildas poderosas'),
('Diamante', 750000, '💠', '#B9F2FF', 5, 750000, 'Liga superior para as melhores guildas'),
('Mestre', 1500000, '🔷', '#4169E1', 6, 1500000, 'Liga dos mestres - apenas os mais dedicados'),
('Cristal', 3000000, '🔮', '#9D00FF', 7, 3000000, 'Liga suprema - o topo mundial!')
ON CONFLICT (league_name) DO UPDATE 
SET min_fame = EXCLUDED.min_fame, 
    icon = EXCLUDED.icon,
    season_reward_gold = EXCLUDED.season_reward_gold;

CREATE TABLE IF NOT EXISTS guild_fame_contributions (
    id SERIAL PRIMARY KEY,
    guild_id INT NOT NULL REFERENCES guilds(id),
    user_id BIGINT NOT NULL,
    season_id INT NOT NULL REFERENCES guild_seasons(season_id),
    fame_contributed BIGINT DEFAULT 0,
    last_contribution TIMESTAMP DEFAULT NOW()
);

-- =========================
-- TABELAS DE NPC E REPUTAÇÃO
-- =========================
CREATE TABLE IF NOT EXISTS npc_reputation (
    user_id BIGINT NOT NULL,
    npc_id VARCHAR(50) NOT NULL,
    reputation INT DEFAULT 0,
    title VARCHAR(100) DEFAULT 'Desconhecido',
    total_purchases INT DEFAULT 0,
    total_gold_spent BIGINT DEFAULT 0,
    last_interaction TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, npc_id)
);

CREATE TABLE IF NOT EXISTS traveling_merchant (
    spawn_id SERIAL PRIMARY KEY,
    zone_id BIGINT REFERENCES zone(zone_id),
    spawned_at TIMESTAMP DEFAULT NOW(),
    despawn_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    visitors_count INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS traveling_merchant_inventory (
    spawn_id INT REFERENCES traveling_merchant(spawn_id) ON DELETE CASCADE,
    item_id INT REFERENCES items(id),
    tier INT NOT NULL,
    price BIGINT NOT NULL,
    quantity INT DEFAULT 1,
    is_sold BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (spawn_id, item_id, tier)
);

CREATE TABLE IF NOT EXISTS npc_dialogues (
    dialogue_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    npc_id VARCHAR(50) NOT NULL,
    dialogue_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS npc_daily_quests (
    quest_id SERIAL PRIMARY KEY,
    npc_id VARCHAR(50) NOT NULL,
    user_id BIGINT NOT NULL,
    quest_type VARCHAR(50) NOT NULL,
    target_id INT,
    target_amount INT NOT NULL,
    current_progress INT DEFAULT 0,
    reward_reputation INT NOT NULL,
    reward_gold BIGINT DEFAULT 0,
    reward_item_id INT,
    expires_at TIMESTAMP NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    claimed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- TABELAS DE HIDEOUT CRAFTING E DUNGEON
-- =========================
CREATE TABLE IF NOT EXISTS hideout_recipes (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    result_item_id BIGINT REFERENCES items(id) ON DELETE CASCADE,
    result_quantity INT DEFAULT 1,
    min_hideout_level INT DEFAULT 1,
    craft_time_seconds INT DEFAULT 300,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hideout_recipe_materials (
    recipe_id INT REFERENCES hideout_recipes(id) ON DELETE CASCADE,
    item_id BIGINT REFERENCES items(id) ON DELETE CASCADE,
    quantity INT NOT NULL,
    PRIMARY KEY (recipe_id, item_id)
);

CREATE TABLE IF NOT EXISTS hideout_crafting_queue (
    id SERIAL PRIMARY KEY,
    hideout_id INT REFERENCES hideouts(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    recipe_id INT REFERENCES hideout_recipes(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT NOW(),
    finishes_at TIMESTAMP NOT NULL,
    completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS hideout_dungeon_runs (
    id SERIAL PRIMARY KEY,
    hideout_id INT REFERENCES hideouts(id) ON DELETE CASCADE,
    party_leader_id BIGINT NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    success BOOLEAN DEFAULT FALSE,
    total_power_score INT NOT NULL,
    difficulty_tier INT NOT NULL,
    rewards_claimed BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS hideout_dungeon_party (
    run_id INT REFERENCES hideout_dungeon_runs(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    power_score INT NOT NULL,
    damage_dealt BIGINT DEFAULT 0,
    PRIMARY KEY (run_id, user_id)
);

CREATE TABLE IF NOT EXISTS hideout_dungeon_rewards (
    run_id INT REFERENCES hideout_dungeon_runs(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    item_id BIGINT REFERENCES items(id) ON DELETE SET NULL,
    quantity INT DEFAULT 1,
    gold_reward BIGINT DEFAULT 0,
    claimed BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (run_id, user_id, item_id)
);

-- =========================
-- ÍNDICES PARA PERFORMANCE
-- =========================
CREATE INDEX IF NOT EXISTS idx_users_exp ON users(exp);
CREATE INDEX IF NOT EXISTS idx_users_fame_total ON users ((fame_arena + fame_combat + fame_crafting + fame_exploration + fame_trading));
CREATE INDEX IF NOT EXISTS idx_users_in_hideout ON users(in_hideout_id);
CREATE INDEX IF NOT EXISTS idx_users_equipped_items ON users(equipped_weapon, equipped_armor);
CREATE INDEX IF NOT EXISTS idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_completed ON user_achievements(user_id, completed);
CREATE INDEX IF NOT EXISTS idx_user_daily_quests_user ON user_daily_quests(user_id);
CREATE INDEX IF NOT EXISTS idx_user_daily_quests_expires ON user_daily_quests(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_fortune_expires ON user_fortune(expires_at);
CREATE INDEX IF NOT EXISTS idx_fame_history_user ON fame_history(user_id);
CREATE INDEX IF NOT EXISTS idx_fame_history_type ON fame_history(fame_type);
CREATE INDEX IF NOT EXISTS idx_guild_seasons_status ON guild_seasons(status);
CREATE INDEX IF NOT EXISTS idx_guild_seasons_end_date ON guild_seasons(end_date);
CREATE INDEX IF NOT EXISTS idx_guild_season_rankings_season ON guild_season_rankings(season_id);
CREATE INDEX IF NOT EXISTS idx_guild_season_rankings_guild ON guild_season_rankings(guild_id);
CREATE INDEX IF NOT EXISTS idx_guild_fame_contributions_guild ON guild_fame_contributions(guild_id);
CREATE INDEX IF NOT EXISTS idx_guild_fame_contributions_season ON guild_fame_contributions(season_id);
CREATE INDEX IF NOT EXISTS idx_guild_fame_contributions_user ON guild_fame_contributions(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_guild_fame_contributions_unique ON guild_fame_contributions(guild_id, user_id, season_id);
CREATE INDEX IF NOT EXISTS idx_npc_reputation_user ON npc_reputation(user_id);
CREATE INDEX IF NOT EXISTS idx_npc_reputation_score ON npc_reputation(npc_id, reputation DESC);
CREATE INDEX IF NOT EXISTS idx_traveling_merchant_active ON traveling_merchant(is_active, despawn_at);
CREATE INDEX IF NOT EXISTS idx_npc_dialogues_user ON npc_dialogues(user_id, created_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_npc_quests_daily_unique ON npc_daily_quests(user_id, npc_id, DATE(created_at));
CREATE INDEX IF NOT EXISTS idx_npc_quests_active ON npc_daily_quests(user_id, completed, claimed);
CREATE INDEX IF NOT EXISTS idx_items_collectible ON items(is_collectible) WHERE is_collectible = TRUE;
CREATE INDEX IF NOT EXISTS idx_hideout_crafting_user ON hideout_crafting_queue(user_id, completed);
CREATE INDEX IF NOT EXISTS idx_hideout_dungeon_runs ON hideout_dungeon_runs(hideout_id, started_at);

-- =========================
-- COMENTÁRIOS PARA DOCUMENTAÇÃO
-- =========================
COMMENT ON TABLE achievements IS 'Conquistas desbloqueáveis no jogo';
COMMENT ON TABLE user_achievements IS 'Progresso das conquistas por usuário';
COMMENT ON TABLE daily_quests IS 'Pool de missões diárias disponíveis';
COMMENT ON TABLE user_daily_quests IS 'Daily quests ativas de cada usuário';
COMMENT ON TABLE user_fortune IS 'Buffs temporários de sorte do jogador';
COMMENT ON TABLE user_stats IS 'Estatísticas e recordes dos jogadores';
COMMENT ON TABLE fame_history IS 'Histórico de alterações de fama';
COMMENT ON TABLE fame_titles IS 'Títulos desbloqueáveis por fama';
COMMENT ON TABLE npc_reputation IS 'Sistema de reputação dos jogadores com cada NPC';
COMMENT ON TABLE traveling_merchant IS 'Spawns do Mercador Viajante nos hubs';
COMMENT ON TABLE traveling_merchant_inventory IS 'Inventário temporário do Mercador Viajante';
COMMENT ON TABLE npc_dialogues IS 'Histórico de interações com NPCs';
COMMENT ON TABLE npc_daily_quests IS 'Missões diárias oferecidas pelos NPCs';
COMMENT ON TABLE hideout_recipes IS 'Receitas de crafting disponíveis nos hideouts';
COMMENT ON TABLE hideout_dungeon_runs IS 'Dungeons especiais dos hideouts';
COMMENT ON COLUMN users.exp IS 'Experiência atual do jogador dentro do nível (reseta ao subir de nível)';
COMMENT ON COLUMN users.in_hideout_id IS 'ID do hideout onde o player está atualmente (NULL se não estiver em nenhum)';
COMMENT ON COLUMN users.previous_zone_id IS 'Zona onde o player estava antes de entrar no hideout';
COMMENT ON COLUMN users.equipped_weapon IS 'Item de arma equipado (usado para calcular power score)';
COMMENT ON COLUMN users.equipped_armor IS 'Item de armadura equipado (usado para calcular power score)';
COMMENT ON COLUMN items.is_collectible IS 'Indica se o item é um recurso coletável (madeira, pedra, etc)';
COMMENT ON COLUMN resources.tier IS 'Tier do recurso (1-10), indica raridade e poder';
COMMENT ON COLUMN npc_reputation.reputation IS 'Pontos de reputação (0-10000+)';
COMMENT ON COLUMN npc_reputation.title IS 'Título atual com o NPC baseado na reputação';
COMMENT ON COLUMN traveling_merchant.despawn_at IS 'Quando o mercador vai desaparecer';
COMMENT ON COLUMN npc_daily_quests.expires_at IS 'Quando a missão expira (geralmente 24h)';

-- =========================
-- FUNÇÕES PL/PGSQL
-- =========================

-- Função para calcular fama total
CREATE OR REPLACE FUNCTION get_total_fame(user_id_param BIGINT)
RETURNS BIGINT AS $$
BEGIN
    RETURN (
        SELECT COALESCE(fame_arena, 0) + COALESCE(fame_combat, 0) + 
               COALESCE(fame_crafting, 0) + COALESCE(fame_exploration, 0) + 
               COALESCE(fame_trading, 0)
        FROM users
        WHERE discord_id = user_id_param
    );
END;
$$ LANGUAGE plpgsql;

-- Função para adicionar fama
CREATE OR REPLACE FUNCTION add_fame(
    user_id_param BIGINT,
    fame_type_param VARCHAR(20),
    amount_param INT,
    reason_param TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    CASE fame_type_param
        WHEN 'arena' THEN
            UPDATE users SET fame_arena = fame_arena + amount_param WHERE discord_id = user_id_param;
        WHEN 'combat' THEN
            UPDATE users SET fame_combat = fame_combat + amount_param WHERE discord_id = user_id_param;
        WHEN 'crafting' THEN
            UPDATE users SET fame_crafting = fame_crafting + amount_param WHERE discord_id = user_id_param;
        WHEN 'exploration' THEN
            UPDATE users SET fame_exploration = fame_exploration + amount_param WHERE discord_id = user_id_param;
        WHEN 'trading' THEN
            UPDATE users SET fame_trading = fame_trading + amount_param WHERE discord_id = user_id_param;
    END CASE;
    
    INSERT INTO fame_history (user_id, fame_type, amount, reason)
    VALUES (user_id_param, fame_type_param, amount_param, reason_param);
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar título de reputação
CREATE OR REPLACE FUNCTION update_reputation_title()
RETURNS TRIGGER AS $$
BEGIN
    NEW.title := CASE
        WHEN NEW.reputation >= 10000 THEN 'Campeão Eterno'
        WHEN NEW.reputation >= 5000 THEN 'Lenda Viva'
        WHEN NEW.reputation >= 2500 THEN 'Herói Local'
        WHEN NEW.reputation >= 1000 THEN 'Parceiro Leal'
        WHEN NEW.reputation >= 500 THEN 'Aliado de Confiança'
        WHEN NEW.reputation >= 250 THEN 'Amigo'
        WHEN NEW.reputation >= 100 THEN 'Conhecido'
        ELSE 'Desconhecido'
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_npc_reputation_title ON npc_reputation;
CREATE TRIGGER update_npc_reputation_title
    BEFORE INSERT OR UPDATE OF reputation ON npc_reputation
    FOR EACH ROW
    EXECUTE FUNCTION update_reputation_title();

-- Função para desativar mercador expirado
CREATE OR REPLACE FUNCTION check_merchant_expiration()
RETURNS void AS $$
BEGIN
    UPDATE traveling_merchant
    SET is_active = FALSE
    WHERE is_active = TRUE AND despawn_at <= NOW();
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar liga da guilda
CREATE OR REPLACE FUNCTION update_guild_league(guild_id_param INT)
RETURNS VOID AS $$
DECLARE
    current_fame BIGINT;
    new_league VARCHAR(20);
    new_icon VARCHAR(10);
BEGIN
    SELECT season_fame INTO current_fame FROM guilds WHERE id = guild_id_param;
    
    SELECT league_name, icon INTO new_league, new_icon
    FROM guild_leagues
    WHERE min_fame <= current_fame
    ORDER BY min_fame DESC
    LIMIT 1;
    
    UPDATE guilds 
    SET current_league = new_league,
        league_icon = new_icon
    WHERE id = guild_id_param;
END;
$$ LANGUAGE plpgsql;

-- Função para adicionar fama à guilda
CREATE OR REPLACE FUNCTION add_guild_fame(
    guild_id_param INT,
    user_id_param BIGINT,
    fame_amount_param BIGINT
)
RETURNS VOID AS $$
DECLARE
    active_season_id INT;
BEGIN
    SELECT season_id INTO active_season_id
    FROM guild_seasons
    WHERE status = 'active'
    LIMIT 1;
    
    IF active_season_id IS NULL THEN
        active_season_id := start_new_guild_season();
    END IF;
    
    UPDATE guilds
    SET season_fame = season_fame + fame_amount_param,
        total_fame = total_fame + fame_amount_param
    WHERE id = guild_id_param;
    
    INSERT INTO guild_fame_contributions (guild_id, user_id, season_id, fame_contributed, last_contribution)
    VALUES (guild_id_param, user_id_param, active_season_id, fame_amount_param, NOW())
    ON CONFLICT (guild_id, user_id, season_id)
    DO UPDATE SET 
        fame_contributed = guild_fame_contributions.fame_contributed + fame_amount_param,
        last_contribution = NOW();
    
    PERFORM update_guild_league(guild_id_param);
END;
$$ LANGUAGE plpgsql;

-- Função para finalizar temporada e salvar rankings
CREATE OR REPLACE FUNCTION finalize_guild_season()
RETURNS VOID AS $$
DECLARE
    active_season_id INT;
    guild_record RECORD;
    current_rank INT := 1;
BEGIN
    SELECT season_id INTO active_season_id
    FROM guild_seasons
    WHERE status = 'active'
    LIMIT 1;
    
    IF active_season_id IS NULL THEN
        RAISE EXCEPTION 'Nenhuma temporada ativa encontrada';
    END IF;
    
    FOR guild_record IN 
        SELECT id, season_fame, current_league
        FROM guilds
        ORDER BY season_fame DESC
    LOOP
        INSERT INTO guild_season_rankings (season_id, guild_id, final_fame, final_league, final_rank)
        VALUES (active_season_id, guild_record.id, guild_record.season_fame, guild_record.current_league, current_rank);
        
        current_rank := current_rank + 1;
    END LOOP;
    
    UPDATE guild_seasons
    SET status = 'ended'
    WHERE season_id = active_season_id;
END;
$$ LANGUAGE plpgsql;

-- Função para iniciar nova temporada
CREATE OR REPLACE FUNCTION start_new_guild_season()
RETURNS INT AS $$
DECLARE
    new_season_id INT;
    new_season_number INT;
BEGIN
    UPDATE guild_seasons 
    SET status = 'ended' 
    WHERE status = 'active';
    
    SELECT COALESCE(MAX(season_number), 0) + 1 INTO new_season_number
    FROM guild_seasons;
    
    INSERT INTO guild_seasons (season_number, start_date, end_date, status)
    VALUES (
        new_season_number,
        NOW(),
        NOW() + INTERVAL '1 month',
        'active'
    )
    RETURNING season_id INTO new_season_id;
    
    RETURN new_season_id;
END;
$$ LANGUAGE plpgsql;

-- Iniciar primeira temporada
SELECT start_new_guild_season();

-- =========================
-- CONQUISTAS E MISSÕES INICIAIS DE EXEMPLO
-- =========================
INSERT INTO achievements (name, description, icon, category, requirement_type, requirement_amount, reward_gold, reward_fame) VALUES
('Primeiro Sangue', 'Derrote seu primeiro inimigo', '⚔️', 'combat', 'kills', 1, 500, 10),
('Caçador Novato', 'Derrote 10 inimigos', '🗡️', 'combat', 'kills', 10, 2000, 25),
('Exterminador', 'Derrote 100 inimigos', '💀', 'combat', 'kills', 100, 10000, 100),
('Genocida', 'Derrote 1000 inimigos', '☠️', 'combat', 'kills', 1000, 100000, 500),
('Explorador', 'Visite 5 zonas diferentes', '🗺️', 'exploration', 'zones_explored', 5, 1000, 15),
('Viajante Mundial', 'Visite 20 zonas diferentes', '🌍', 'exploration', 'zones_explored', 20, 5000, 50),
('Artesão Iniciante', 'Crafte 5 itens', '🔨', 'crafting', 'items_crafted', 5, 1500, 20),
('Mestre Ferreiro', 'Crafte 50 itens', '⚒️', 'crafting', 'items_crafted', 50, 15000, 150),
('Rico', 'Acumule 10,000 gold', '💰', 'special', 'gold_earned', 10000, 5000, 30),
('Milionário', 'Acumule 1,000,000 gold', '💎', 'special', 'gold_earned', 1000000, 50000, 300),
('Colecionador', 'Colete 100 recursos', '📦', 'exploration', 'resources_collected', 100, 2000, 25),
('Comerciante', 'Complete 5 trades', '🤝', 'social', 'trades_completed', 5, 3000, 40)
ON CONFLICT (name) DO NOTHING;

-- Daily quests de exemplo
INSERT INTO daily_quests (quest_type, description, icon, requirement_amount, reward_gold, reward_exp, reward_fame, difficulty) VALUES
('explore', 'Explore 3 vezes', '🔍', 3, 1000, 50, 10, 'easy'),
('explore', 'Explore 5 vezes', '🔍', 5, 2500, 100, 20, 'medium'),
('explore', 'Explore 10 vezes', '🔍', 10, 5000, 200, 40, 'hard'),
('kill', 'Derrote 5 inimigos', '⚔️', 5, 1500, 75, 15, 'easy'),
('kill', 'Derrote 10 inimigos', '⚔️', 10, 3000, 150, 30, 'medium'),
('kill', 'Derrote 20 inimigos', '⚔️', 20, 6000, 300, 60, 'hard'),
('craft', 'Crafte 2 itens', '🔨', 2, 1200, 60, 12, 'easy'),
('craft', 'Crafte 5 itens', '🔨', 5, 3500, 150, 35, 'medium'),
('collect', 'Colete 50 recursos', '📦', 50, 1000, 50, 10, 'easy'),
('collect', 'Colete 150 recursos', '📦', 150, 3000, 120, 25, 'medium'),
('trade', 'Complete 1 trade', '🤝', 1, 2000, 100, 20, 'medium'),
('travel', 'Visite 3 zonas diferentes', '🗺️', 3, 2000, 80, 18, 'medium')
ON CONFLICT DO NOTHING;

-- =========================
-- ITENS ESPECIAIS DO HIDEOUT
-- =========================
INSERT INTO items (id, name, basedamage, basedefense, tier, subtier, slot_id, is_collectible)
VALUES (2210, 'Kit de Construção de Esconderijo', NULL, NULL, 6, 0, 9, FALSE)
ON CONFLICT (id) DO UPDATE 
SET name = EXCLUDED.name,
    tier = EXCLUDED.tier,
    subtier = EXCLUDED.subtier,
    slot_id = EXCLUDED.slot_id;

INSERT INTO items (id, name, basedamage, basedefense, tier, subtier, slot_id, is_collectible)
VALUES (7812, 'Estrutura Básica de Hideout', NULL, NULL, 6, 0, 9, FALSE)
ON CONFLICT (id) DO UPDATE 
SET name = EXCLUDED.name,
    tier = EXCLUDED.tier,
    subtier = EXCLUDED.subtier,
    slot_id = EXCLUDED.slot_id;
