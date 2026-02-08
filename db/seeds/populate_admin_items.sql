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
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'espada_do_desenvolvedor',
    6,  -- weapon
    100000,
    50000,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- Armadura Do Admin
INSERT INTO items (
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'armadura_do_admin',
    4,  -- chest
    5000,
    200000,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- Elmo Omnisciente
INSERT INTO items (
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'elmo_omnisciente',
    2,  -- head
    10000,
    150000,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- Calcas Do Debugger
INSERT INTO items (
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'calcas_do_debugger',
    3,  -- legs
    8000,
    120000,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- Botas Do Hotfix
INSERT INTO items (
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'botas_do_hotfix',
    5,  -- feet
    15000,
    80000,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- Amuleto Do Sysadmin
INSERT INTO items (
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'amuleto_do_sysadmin',
    1,  -- amulet
    50000,
    50000,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- Anel Do Commit
INSERT INTO items (
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'anel_do_commit',
    7,  -- ring
    25000,
    25000,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- Escudo Do Rollback
INSERT INTO items (
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'escudo_do_rollback',
    8,  -- shield
    0,
    500000,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- Cajado Do Refactor
INSERT INTO items (
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'cajado_do_refactor',
    6,  -- weapon
    250000,
    10000,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- Pocao De Godmode
INSERT INTO items (
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'pocao_de_godmode',
    0,  -- consumable
    0,
    0,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- Kit De Emergencia
INSERT INTO items (
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'kit_de_emergencia',
    0,  -- consumable
    0,
    0,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- Pergaminho Do Fix
INSERT INTO items (
    name, slot_id, basedamage, basedefense, tier, subtier,
    depth_new, quality_new
) VALUES (
    'pergaminho_do_fix',
    0,  -- consumable
    0,
    0,
    99,  -- tier: Admin Tier
    0,  -- subtier: Admin
    99,  -- depth_new: Admin Tier
    'ADMIN'  -- quality_new: Qualidade especial de admin
);

-- ================================================
-- TOTAL: 12 itens de admin criados
-- ================================================

-- Verificar inserções
SELECT 
    COUNT(*) as total_admin_items,
    AVG(basedamage) as avg_damage,
    AVG(basedefense) as avg_defense,
    MAX(basedamage) as max_damage,
    MAX(basedefense) as max_defense
FROM items
WHERE depth_new = 99 AND quality_new = 'ADMIN';

-- Listar todos os itens de admin
SELECT id, name, slot_id, basedamage, basedefense, quality_new
FROM items
WHERE depth_new = 99 AND quality_new = 'ADMIN'
ORDER BY slot_id, name;