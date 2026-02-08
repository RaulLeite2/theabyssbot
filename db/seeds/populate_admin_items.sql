-- ================================================
-- ITENS DE ADMIN - APENAS PARA TESTES/DEBUG
-- ⚠️  NÃO DISTRIBUIR PARA JOGADORES NORMAIS
-- ================================================

-- Inserir itens de admin na tabela items
-- Todos com depth_new = 99 (tier especial de admin)
-- Todos com quality_new = 'ADMIN' (qualidade especial)

-- ADMIN_TIER

-- Espada Do Desenvolvedor
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'espada_do_desenvolvedor',
    6,  -- weapon
    100000,
    50000,
    '{"str": 1000.0, "dex": 1000.0, "int": 1000.0}',
    '[{"type": "crit_chance", "value": 100}, {"type": "crit_damage", "value": 500}, {"type": "lifesteal", "value": 50}, {"type": "exp_boost", "value": 1000}, {"type": "gold_boost", "value": 1000}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'A lendária espada dos criadores. Poder absoluto concentrado em uma lâmina.'
);

-- Armadura Do Admin
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'armadura_do_admin',
    4,  -- chest
    5000,
    200000,
    '{"str": 500.0, "dex": 500.0, "int": 500.0}',
    '[{"type": "damage_reduction", "value": 90}, {"type": "hp_regen", "value": 5000}, {"type": "mana_regen", "value": 5000}, {"type": "hp_boost", "value": 100000}, {"type": "reflect_damage", "value": 50}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'Armadura forjada nas chamas do código. Invulnerabilidade em forma tangível.'
);

-- Elmo Omnisciente
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'elmo_omnisciente',
    2,  -- head
    10000,
    150000,
    '{"str": 300.0, "dex": 300.0, "int": 1500.0}',
    '[{"type": "int_boost", "value": 5000}, {"type": "mana_boost", "value": 50000}, {"type": "mana_regen", "value": 2000}, {"type": "spell_power", "value": 500}, {"type": "cooldown_reduction", "value": 50}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'Elmo que concede conhecimento de todos os bugs e features do sistema.'
);

-- Calcas Do Debugger
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'calcas_do_debugger',
    3,  -- legs
    8000,
    120000,
    '{"str": 400.0, "dex": 1200.0, "int": 400.0}',
    '[{"type": "dex_boost", "value": 5000}, {"type": "dodge_chance", "value": 75}, {"type": "movement_speed", "value": 500}, {"type": "attack_speed", "value": 300}, {"type": "evasion", "value": 50}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'Calças que permitem esquivar de qualquer erro de runtime.'
);

-- Botas Do Hotfix
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'botas_do_hotfix',
    5,  -- feet
    15000,
    80000,
    '{"str": 600.0, "dex": 800.0, "int": 600.0}',
    '[{"type": "movement_speed", "value": 1000}, {"type": "str_boost", "value": 3000}, {"type": "dex_boost", "value": 3000}, {"type": "kick_damage", "value": 50000}, {"type": "stamina_boost", "value": 10000}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'Botas que aplicam correções instantâneas em qualquer situação crítica.'
);

-- Amuleto Do Sysadmin
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'amuleto_do_sysadmin',
    1,  -- amulet
    50000,
    50000,
    '{"str": 1000.0, "dex": 1000.0, "int": 1000.0}',
    '[{"type": "all_stats", "value": 10000}, {"type": "hp_boost", "value": 500000}, {"type": "mana_boost", "value": 500000}, {"type": "hp_regen", "value": 10000}, {"type": "mana_regen", "value": 10000}, {"type": "exp_boost", "value": 10000}, {"type": "gold_boost", "value": 10000}, {"type": "luck", "value": 1000}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'Amuleto que concede acesso root ao próprio universo do jogo.'
);

-- Anel Do Commit
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'anel_do_commit',
    7,  -- ring
    25000,
    25000,
    '{"str": 500.0, "dex": 500.0, "int": 500.0}',
    '[{"type": "crit_chance", "value": 100}, {"type": "crit_damage", "value": 1000}, {"type": "lifesteal", "value": 100}, {"type": "spell_vamp", "value": 100}, {"type": "penetration", "value": 100}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'Anel que faz commit direto na produção sem code review. Poder máximo, sem recuo.'
);

-- Escudo Do Rollback
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'escudo_do_rollback',
    8,  -- shield
    0,
    500000,
    '{"str": 1000.0, "dex": 200.0, "int": 200.0}',
    '[{"type": "damage_reduction", "value": 99}, {"type": "block_chance", "value": 90}, {"type": "reflect_damage", "value": 100}, {"type": "hp_regen", "value": 20000}, {"type": "revive_chance", "value": 100}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'Escudo capaz de desfazer qualquer ação hostil. Ctrl+Z físico perfeito.'
);

-- Cajado Do Refactor
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'cajado_do_refactor',
    6,  -- weapon
    250000,
    10000,
    '{"str": 100.0, "dex": 200.0, "int": 5000.0}',
    '[{"type": "spell_power", "value": 2000}, {"type": "int_boost", "value": 15000}, {"type": "mana_boost", "value": 1000000}, {"type": "mana_regen", "value": 50000}, {"type": "cooldown_reduction", "value": 90}, {"type": "aoe_radius", "value": 500}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'Cajado que refatora a realidade ao seu redor. Caos reorganizado em harmonia.'
);

-- Pocao De Godmode
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'pocao_de_godmode',
    0,  -- consumable
    0,
    0,
    '{}',
    '[{"type": "instant_heal", "value": 999999999}, {"type": "mana_restore", "value": 999999999}, {"type": "invulnerability", "value": 3600}, {"type": "all_stats_temp", "value": 100000, "duration": 3600}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'Poção que concede literalmente poder divino. Use com responsabilidade... ou não.'
);

-- Kit De Emergencia
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'kit_de_emergencia',
    0,  -- consumable
    0,
    0,
    '{}',
    '[{"type": "instant_heal", "value": 10000000}, {"type": "mana_restore", "value": 10000000}, {"type": "cleanse_debuffs", "value": 100}, {"type": "temp_shield", "value": 1000000}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'Kit de emergência para quando tudo está pegando fogo. Literalmente salva vidas.'
);

-- Pergaminho Do Fix
INSERT INTO items (
    name, slot_id, base_damage, base_defense,
    scaling, buffs, legendary, quest_item,
    depth_new, quality_new, description
) VALUES (
    'pergaminho_do_fix',
    0,  -- consumable
    0,
    0,
    '{}',
    '[{"type": "resurrect_self", "value": 100}, {"type": "full_restore", "value": 100}, {"type": "temp_god_mode", "value": 60}]',
    true,
    false,
    99,  -- depth_new: Admin Tier
    'ADMIN',  -- quality_new: Qualidade especial de admin
    'Pergaminho que conserta literalmente qualquer problema. Até morte.'
);

-- ================================================
-- TOTAL: 12 itens de admin criados
-- ================================================

-- Verificar inserções
SELECT 
    COUNT(*) as total_admin_items,
    AVG(base_damage) as avg_damage,
    AVG(base_defense) as avg_defense,
    MAX(base_damage) as max_damage,
    MAX(base_defense) as max_defense
FROM items
WHERE depth_new = 99 AND quality_new = 'ADMIN';

-- Listar todos os itens de admin
SELECT id, name, slot_id, base_damage, base_defense, quality_new
FROM items
WHERE depth_new = 99 AND quality_new = 'ADMIN'
ORDER BY slot_id, name;