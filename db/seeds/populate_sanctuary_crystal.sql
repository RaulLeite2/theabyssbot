-- =========================
-- CRISTAL DE FUNDAÇÃO DO SANTUÁRIO
-- Item especial para criar Hideout/Sanctuary
-- =========================

BEGIN TRANSACTION;

-- Item: Cristal de Fundação do Santuário
INSERT INTO items (
    name, 
    slot_id, 
    tier, 
    depth_new, 
    quality_new, 
    plus_level,
    base_damage, 
    base_defense, 
    scaling, 
    buffs, 
    flags
) VALUES (
    'Cristal de Fundação do Santuário',
    NULL,  -- Não é equipável
    'T8.0',
    8,
    'LEGENDARY',
    0,
    0,
    0,
    '{}',
    '[
        {
            "type": "sanctuary_creation",
            "value": 1,
            "description": "Permite criar um Santuário para sua guilda"
        }
    ]',
    '{
        "legendary": true,
        "tradeable": false,
        "quest_item": true,
        "consumable": true,
        "stackable": false,
        "sanctuary_crystal": true,
        "description": "Um cristal mágico pulsante com energia ancestral. Contém o poder necessário para estabelecer um Santuário - um refúgio seguro para sua guilda nas profundezas do Abismo."
    }'
);

-- Materiais de crafting necessários (exemplos - ajuste IDs conforme necessário)

-- Fragmentos elementais (precisam ser criados também)
INSERT INTO items (name, slot_id, tier, depth_new, quality_new, plus_level, base_damage, base_defense, scaling, buffs, flags)
VALUES 
    ('Fragmento de Fogo Primordial', NULL, 'T6.0', 6, 'RARE', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}'),
    ('Fragmento de Gelo Eterno', NULL, 'T6.0', 6, 'RARE', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}'),
    ('Fragmento de Trovão Arcano', NULL, 'T6.0', 6, 'RARE', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}'),
    ('Fragmento de Terra Antiga', NULL, 'T6.0', 6, 'RARE', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}');

-- Essências místicas de alto nível
INSERT INTO items (name, slot_id, tier, depth_new, quality_new, plus_level, base_damage, base_defense, scaling, buffs, flags)
VALUES 
    ('Essência do Abismo', NULL, 'T7.0', 7, 'EPIC', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}'),
    ('Essência Celestial', NULL, 'T7.0', 7, 'EPIC', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}'),
    ('Essência do Vazio', NULL, 'T8.0', 8, 'LEGENDARY', 0, 0, 0, '{}', '[]', '{"legendary": true, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 99}');

-- Núcleos de poder
INSERT INTO items (name, slot_id, tier, depth_new, quality_new, plus_level, base_damage, base_defense, scaling, buffs, flags)
VALUES 
    ('Núcleo de Mana Concentrado', NULL, 'T5.0', 5, 'UNCOMMON', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}'),
    ('Cristal de Energia Pura', NULL, 'T6.0', 6, 'RARE', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}'),
    ('Coração de Dragão Ancião', NULL, 'T8.0', 8, 'MYTHIC', 0, 0, 0, '{}', '[]', '{"legendary": true, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 10}');

-- Minérios místicos
INSERT INTO items (name, slot_id, tier, depth_new, quality_new, plus_level, base_damage, base_defense, scaling, buffs, flags)
VALUES 
    ('Minério de Mythril', NULL, 'T5.0', 5, 'RARE', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}'),
    ('Minério de Adamantium', NULL, 'T6.0', 6, 'EPIC', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}'),
    ('Minério de Orichalcum', NULL, 'T7.0', 7, 'EPIC', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}');

-- Runas e pergaminhos arcanos
INSERT INTO items (name, slot_id, tier, depth_new, quality_new, plus_level, base_damage, base_defense, scaling, buffs, flags)
VALUES 
    ('Runa de Proteção Lv5', NULL, 'T5.0', 5, 'RARE', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}'),
    ('Pergaminho de Selamento', NULL, 'T6.0', 6, 'EPIC', 0, 0, 0, '{}', '[]', '{"legendary": false, "tradeable": true, "quest_item": false, "stackable": true, "max_stack": 999}'),
    ('Grimório Ancestral', NULL, 'T8.0', 8, 'LEGENDARY', 0, 0, 0, '{}', '[]', '{"legendary": true, "tradeable": false, "quest_item": true, "stackable": true, "max_stack": 1}');

COMMIT;

-- Total de items criados: 1 Cristal + 15 materiais = 16 items
