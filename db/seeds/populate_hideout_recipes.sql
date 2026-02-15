-- =========================
-- RECEITAS DE CRAFTING DO SANCTUARY
-- Populate script para exemplos iniciais
-- =========================

-- IMPORTANTE: Ajuste os item_ids de acordo com sua tabela de items

-- =========================
-- RECEITA 1: Espada do Abismo (Tier 8)
-- =========================
INSERT INTO sanctuary_recipes (name, description, result_item_id, result_quantity, min_hideout_level, craft_time_seconds)
VALUES (
    'Espada do Abismo',
    'Uma lâmina forjada nas profundezas do abismo, pulsando com energia sombria.',
    NULL, -- Substitua com ID de item Tier 8
    1,
    3,
    600 -- 10 minutos
) ON CONFLICT DO NOTHING;

-- Materiais (ajuste os IDs)
-- INSERT INTO sanctuary_recipe_materials (recipe_id, item_id, quantity)
-- VALUES 
--   (1, 100, 50),  -- 50x Fragmento Sombrio
--   (1, 101, 20),  -- 20x Minério Negro
--   (1, 102, 5);   -- 5x Essência Abissal

-- =========================
-- RECEITA 2: Armadura de Placas Reforçada (Tier 7)
-- =========================
INSERT INTO sanctuary_recipes (name, description, result_item_id, result_quantity, min_hideout_level, craft_time_seconds)
VALUES (
    'Armadura de Placas Místicas',
    'Placas de metal infundidas com magia protetora.',
    NULL, -- Substitua com ID de armadura Tier 7
    1,
    2,
    480 -- 8 minutos
) ON CONFLICT DO NOTHING;

-- =========================
-- RECEITA 3: Poção de Poder Supremo
-- =========================
INSERT INTO sanctuary_recipes (name, description, result_item_id, result_quantity, min_hideout_level, craft_time_seconds)
VALUES (
    'Poção de Poder Supremo',
    'Aumenta temporariamente seu poder de combate.',
    NULL, -- Substitua com ID de poção
    3,
    1,
    180 -- 3 minutos
) ON CONFLICT DO NOTHING;

-- =========================
-- RECEITA 4: Elixir de Regeneração Maior
-- =========================
INSERT INTO sanctuary_recipes (name, description, result_item_id, result_quantity, min_hideout_level, craft_time_seconds)
VALUES (
    'Elixir de Regeneração Maior',
    'Restaura uma quantidade massiva de HP ao longo do tempo.',
    NULL, -- Substitua com ID de elixir
    2,
    2,
    300 -- 5 minutos
) ON CONFLICT DO NOTHING;

-- =========================
-- RECEITA 5: Gema do Abismo
-- =========================
INSERT INTO sanctuary_recipes (name, description, result_item_id, result_quantity, min_hideout_level, craft_time_seconds)
VALUES (
    'Gema do Abismo',
    'Uma gema rara usada para aprimorar equipamentos lendários.',
    NULL, -- Substitua com ID de gema
    1,
    4,
    900 -- 15 minutos
) ON CONFLICT DO NOTHING;

-- =========================
-- RECEITA 6: Escudo Cristalino
-- =========================
INSERT INTO sanctuary_recipes (name, description, result_item_id, result_quantity, min_hideout_level, craft_time_seconds)
VALUES (
    'Escudo Cristalino',
    'Escudo feito de cristais mágicos que refletem ataques.',
    NULL, -- Substitua com ID de escudo
    1,
    3,
    540 -- 9 minutos
) ON CONFLICT DO NOTHING;

-- =========================
-- RECEITA 7: Botas do Vento
-- =========================
INSERT INTO sanctuary_recipes (name, description, result_item_id, result_quantity, min_hideout_level, craft_time_seconds)
VALUES (
    'Botas do Vento',
    'Botas leves que aumentam sua velocidade de movimento.',
    NULL, -- Substitua com ID de botas
    1,
    2,
    360 -- 6 minutos
) ON CONFLICT DO NOTHING;

-- =========================
-- RECEITA 8: Amuleto da Fortuna
-- =========================
INSERT INTO hideout_recipes (name, description, result_item_id, result_quantity, min_hideout_level, craft_time_seconds)
VALUES (
    'Amuleto da Fortuna',
    'Aumenta a chance de encontrar itens raros.',
    NULL, -- Substitua com ID de amuleto
    1,
    3,
    720 -- 12 minutos
) ON CONFLICT DO NOTHING;

-- =========================
-- RECEITA 9: Kit de Reparo Avançado
-- =========================
INSERT INTO hideout_recipes (name, description, result_item_id, result_quantity, min_hideout_level, craft_time_seconds)
VALUES (
    'Kit de Reparo Avançado',
    'Restaura completamente a durabilidade de equipamentos.',
    NULL, -- Substitua com ID de kit
    5,
    1,
    120 -- 2 minutos
) ON CONFLICT DO NOTHING;

-- =========================
-- RECEITA 10: Capa Sombria
-- =========================
INSERT INTO hideout_recipes (name, description, result_item_id, result_quantity, min_hideout_level, craft_time_seconds)
VALUES (
    'Capa Sombria',
    'Uma capa que concede furtividade aprimorada.',
    NULL, -- Substitua com ID de capa
    1,
    4,
    660 -- 11 minutos
) ON CONFLICT DO NOTHING;

-- =========================
-- INSTRUÇÕES PARA POPULAR MATERIAIS
-- =========================

/*
Para adicionar materiais a uma receita, use:

INSERT INTO hideout_recipe_materials (recipe_id, item_id, quantity)
VALUES 
  (1, <item_id_material_1>, <quantidade>),
  (1, <item_id_material_2>, <quantidade>),
  (1, <item_id_material_3>, <quantidade>);

Exemplo real:
INSERT INTO hideout_recipe_materials (recipe_id, item_id, quantity)
VALUES 
  (1, 50, 100),  -- 100x Minério de Ferro
  (1, 51, 50),   -- 50x Cristal Mágico
  (1, 52, 10);   -- 10x Essência Obscura

Para encontrar o recipe_id:
SELECT id, name FROM hideout_recipes WHERE name LIKE '%Espada%';

Para encontrar item_ids:
SELECT id, name, tier FROM items WHERE name LIKE '%Minério%';
*/

-- =========================
-- VERIFICAÇÃO
-- =========================

-- Ver todas as receitas criadas
SELECT id, name, min_hideout_level, craft_time_seconds 
FROM hideout_recipes 
ORDER BY min_hideout_level, id;

-- =========================
-- RECEITA LENDÁRIA: CRISTAL DE FUNDAÇÃO DO SANTUÁRIO
-- Receita extremamente complexa para criar Hideout/Sanctuary
-- =========================

-- AVISO: Esta receita assume que os materiais foram criados via populate_sanctuary_crystal.sql
-- Os IDs abaixo são EXEMPLOS e devem ser ajustados após inserir os items na tabela

INSERT INTO hideout_recipes (
    name, 
    description, 
    result_item_id, 
    result_quantity, 
    min_hideout_level, 
    craft_time_seconds
)
VALUES (
    'Cristal de Fundação do Santuário',
    'Um ritual ancestral que funde fragmentos elementais, essências místicas e núcleos de poder supremo. Apenas os mais dedicados conseguem reunir todos os materiais necessários.',
    NULL, -- ⚠️ SUBSTITUA com ID do 'Cristal de Fundação do Santuário' da tabela items
    1,
    5, -- Requer Hideout nível 5 (alto)
    7200 -- 2 HORAS de craft time
) ON CONFLICT DO NOTHING;

-- MATERIAIS NECESSÁRIOS (ajuste os IDs após popular items)
-- Use a query abaixo para encontrar os IDs corretos:
-- SELECT id, name FROM items WHERE name IN (
--     'Fragmento de Fogo Primordial', 'Fragmento de Gelo Eterno', 
--     'Fragmento de Trovão Arcano', 'Fragmento de Terra Antiga',
--     'Essência do Abismo', 'Essência Celestial', 'Essência do Vazio',
--     'Núcleo de Mana Concentrado', 'Cristal de Energia Pura', 'Coração de Dragão Ancião',
--     'Minério de Mythril', 'Minério de Adamantium', 'Minério de Orichalcum',
--     'Runa de Proteção Lv5', 'Pergaminho de Selamento', 'Grimório Ancestral'
-- );

-- EXEMPLO de inserção (DESCOMENTE e ajuste IDs após popular items):
/*
INSERT INTO hideout_recipe_materials (recipe_id, item_id, quantity)
VALUES 
    -- Fragmentos Elementais (4 tipos, 100 de cada)
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Fragmento de Fogo Primordial'), 100),
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Fragmento de Gelo Eterno'), 100),
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Fragmento de Trovão Arcano'), 100),
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Fragmento de Terra Antiga'), 100),
    
    -- Essências Místicas (3 tipos, quantidades variadas)
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Essência do Abismo'), 50),
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Essência Celestial'), 50),
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Essência do Vazio'), 10),
    
    -- Núcleos de Poder (3 tipos, sendo o último muito raro)
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Núcleo de Mana Concentrado'), 200),
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Cristal de Energia Pura'), 75),
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Coração de Dragão Ancião'), 1),
    
    -- Minérios Místicos (3 tipos, quantidades altas)
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Minério de Mythril'), 500),
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Minério de Adamantium'), 300),
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Minério de Orichalcum'), 150),
    
    -- Runas e Pergaminhos (3 tipos, incluindo item único)
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Runa de Proteção Lv5'), 50),
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Pergaminho de Selamento'), 25),
    ((SELECT id FROM hideout_recipes WHERE name = 'Cristal de Fundação do Santuário'), (SELECT id FROM items WHERE name = 'Grimório Ancestral'), 1)
ON CONFLICT DO NOTHING;
*/

-- ========================================
-- RESUMO DA RECEITA:
-- ========================================
-- Nome: Cristal de Fundação do Santuário
-- Tempo de Craft: 2 HORAS
-- Nível Mínimo de Hideout: 5
-- 
-- MATERIAIS (TOTAL: 15 tipos diferentes):
-- 
-- Fragmentos Elementais (400 total):
--   - 100x Fragmento de Fogo Primordial
--   - 100x Fragmento de Gelo Eterno
--   - 100x Fragmento de Trovão Arcano
--   - 100x Fragmento de Terra Antiga
-- 
-- Essências Místicas (110 total):
--   - 50x Essência do Abismo
--   - 50x Essência Celestial
--   - 10x Essência do Vazio
-- 
-- Núcleos de Poder (276 total):
--   - 200x Núcleo de Mana Concentrado
--   - 75x Cristal de Energia Pura
--   - 1x Coração de Dragão Ancião ⭐ RARO
-- 
-- Minérios Místicos (950 total):
--   - 500x Minério de Mythril
--   - 300x Minério de Adamantium
--   - 150x Minério de Orichalcum
-- 
-- Runas e Pergaminhos (76 total):
--   - 50x Runa de Proteção Lv5
--   - 25x Pergaminho de Selamento
--   - 1x Grimório Ancestral ⭐ ÚNICO
-- 
-- TOTAL DE MATERIAIS: 1,812 items de 15 tipos diferentes!
-- ========================================

-- Contar receitas
SELECT COUNT(*) as total_recipes FROM hideout_recipes;

-- Ver materiais de uma receita específica
-- SELECT 
--     r.name as recipe_name,
--     i.name as material_name,
--     rm.quantity
-- FROM hideout_recipes r
-- JOIN hideout_recipe_materials rm ON r.id = rm.recipe_id
-- JOIN items i ON rm.item_id = i.id
-- WHERE r.id = 1;
