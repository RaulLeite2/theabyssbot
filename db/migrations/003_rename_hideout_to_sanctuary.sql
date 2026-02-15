-- Migration: Renomeia todas as referências de Hideout para Sanctuary
-- Data: 2026-02-14
-- Descrição: Refatoração legal - renomear sistema de Hideout para Sanctuary (originalidade)
-- Fase 2 do Plano de Refatoração

-- =========================
-- PARTE 1: RENOMEAR TABELAS
-- =========================

-- 1. Tabela principal: hideouts → sanctuaries
ALTER TABLE IF EXISTS hideouts RENAME TO sanctuaries;

-- 2. Tabelas relacionadas
ALTER TABLE IF EXISTS hideout_recipes RENAME TO sanctuary_recipes;
ALTER TABLE IF EXISTS hideout_recipe_materials RENAME TO sanctuary_recipe_materials;
ALTER TABLE IF EXISTS hideout_crafting_queue RENAME TO sanctuary_crafting_queue;
ALTER TABLE IF EXISTS hideout_dungeon_runs RENAME TO sanctuary_dungeon_runs;
ALTER TABLE IF EXISTS hideout_dungeon_party RENAME TO sanctuary_dungeon_party;
ALTER TABLE IF EXISTS hideout_dungeon_rewards RENAME TO sanctuary_dungeon_rewards;

-- =========================
-- PARTE 2: RENOMEAR COLUNAS (Foreign Keys e Referencias)
-- =========================

-- 2.1 Coluna in_hideout_id na tabela users
ALTER TABLE users RENAME COLUMN IF EXISTS in_hideout_id TO in_sanctuary_id;

-- 2.2 Coluna is_hideout na tabela zone
ALTER TABLE zone RENAME COLUMN IF EXISTS is_hideout TO is_sanctuary;

-- 2.3 Atualizar colunas hideout_id para sanctuary_id em tabelas relacionadas
ALTER TABLE sanctuary_crafting_queue RENAME COLUMN IF EXISTS hideout_id TO sanctuary_id;
ALTER TABLE sanctuary_dungeon_runs RENAME COLUMN IF EXISTS hideout_id TO sanctuary_id;

-- =========================
-- PARTE 3: RENOMEAR CONSTRAINTS (Foreign Keys)
-- =========================

-- Remover constraints antigas e recriar com novos nomes
-- 3.1 sanctuaries (antiga hideouts)
DO $$
BEGIN
    -- FK guild_id
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hideouts_guild_id_fkey') THEN
        ALTER TABLE sanctuaries DROP CONSTRAINT hideouts_guild_id_fkey;
        ALTER TABLE sanctuaries ADD CONSTRAINT sanctuaries_guild_id_fkey 
            FOREIGN KEY (guild_id) REFERENCES guilds(id) ON DELETE CASCADE;
    END IF;

    -- FK alliance_id
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hideouts_alliance_id_fkey') THEN
        ALTER TABLE sanctuaries DROP CONSTRAINT hideouts_alliance_id_fkey;
        ALTER TABLE sanctuaries ADD CONSTRAINT sanctuaries_alliance_id_fkey 
            FOREIGN KEY (alliance_id) REFERENCES alliances(id) ON DELETE SET NULL;
    END IF;

    -- FK zone_id
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hideouts_zone_id_fkey') THEN
        ALTER TABLE sanctuaries DROP CONSTRAINT hideouts_zone_id_fkey;
        ALTER TABLE sanctuaries ADD CONSTRAINT sanctuaries_zone_id_fkey 
            FOREIGN KEY (zone_id) REFERENCES zone(zone_id) ON DELETE CASCADE;
    END IF;
END $$;

-- 3.2 sanctuary_crafting_queue
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hideout_crafting_queue_hideout_id_fkey') THEN
        ALTER TABLE sanctuary_crafting_queue DROP CONSTRAINT hideout_crafting_queue_hideout_id_fkey;
        ALTER TABLE sanctuary_crafting_queue ADD CONSTRAINT sanctuary_crafting_queue_sanctuary_id_fkey 
            FOREIGN KEY (sanctuary_id) REFERENCES sanctuaries(id) ON DELETE CASCADE;
    END IF;

    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hideout_crafting_queue_recipe_id_fkey') THEN
        ALTER TABLE sanctuary_crafting_queue DROP CONSTRAINT hideout_crafting_queue_recipe_id_fkey;
        ALTER TABLE sanctuary_crafting_queue ADD CONSTRAINT sanctuary_crafting_queue_recipe_id_fkey 
            FOREIGN KEY (recipe_id) REFERENCES sanctuary_recipes(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 3.3 sanctuary_recipe_materials
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hideout_recipe_materials_recipe_id_fkey') THEN
        ALTER TABLE sanctuary_recipe_materials DROP CONSTRAINT hideout_recipe_materials_recipe_id_fkey;
        ALTER TABLE sanctuary_recipe_materials ADD CONSTRAINT sanctuary_recipe_materials_recipe_id_fkey 
            FOREIGN KEY (recipe_id) REFERENCES sanctuary_recipes(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 3.4 sanctuary_dungeon_runs
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hideout_dungeon_runs_hideout_id_fkey') THEN
        ALTER TABLE sanctuary_dungeon_runs DROP CONSTRAINT hideout_dungeon_runs_hideout_id_fkey;
        ALTER TABLE sanctuary_dungeon_runs ADD CONSTRAINT sanctuary_dungeon_runs_sanctuary_id_fkey 
            FOREIGN KEY (sanctuary_id) REFERENCES sanctuaries(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 3.5 sanctuary_dungeon_party
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hideout_dungeon_party_run_id_fkey') THEN
        ALTER TABLE sanctuary_dungeon_party DROP CONSTRAINT hideout_dungeon_party_run_id_fkey;
        ALTER TABLE sanctuary_dungeon_party ADD CONSTRAINT sanctuary_dungeon_party_run_id_fkey 
            FOREIGN KEY (run_id) REFERENCES sanctuary_dungeon_runs(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 3.6 users.in_sanctuary_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'users_in_hideout_id_fkey') THEN
        ALTER TABLE users DROP CONSTRAINT users_in_hideout_id_fkey;
        ALTER TABLE users ADD CONSTRAINT users_in_sanctuary_id_fkey 
            FOREIGN KEY (in_sanctuary_id) REFERENCES sanctuaries(id) ON DELETE SET NULL;
    END IF;
END $$;

-- =========================
-- PARTE 4: RENOMEAR ÍNDICES
-- =========================

-- Renomear índices se existirem
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_hideouts_guild_id') THEN
        ALTER INDEX idx_hideouts_guild_id RENAME TO idx_sanctuaries_guild_id;
    END IF;

    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_hideouts_zone_id') THEN
        ALTER INDEX idx_hideouts_zone_id RENAME TO idx_sanctuaries_zone_id;
    END IF;

    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_hideout_recipes_type') THEN
        ALTER INDEX idx_hideout_recipes_type RENAME TO idx_sanctuary_recipes_type;
    END IF;
END $$;

-- =========================
-- PARTE 5: VERIFICAÇÃO
-- =========================

DO $$
DECLARE
    sanctuaries_count INTEGER;
    sanctuary_recipes_count INTEGER;
    has_sanctuary_column BOOLEAN;
BEGIN
    -- Verifica se as tabelas foram renomeadas
    SELECT COUNT(*) INTO sanctuaries_count 
    FROM information_schema.tables 
    WHERE table_name = 'sanctuaries';
    
    SELECT COUNT(*) INTO sanctuary_recipes_count 
    FROM information_schema.tables 
    WHERE table_name = 'sanctuary_recipes';
    
    -- Verifica se a coluna foi renomeada
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'zone' AND column_name = 'is_sanctuary'
    ) INTO has_sanctuary_column;
    
    -- Log dos resultados
    RAISE NOTICE '================================================';
    RAISE NOTICE 'VERIFICAÇÃO DA MIGRATION - HIDEOUT → SANCTUARY';
    RAISE NOTICE '================================================';
    
    IF sanctuaries_count = 1 THEN
        RAISE NOTICE '✅ Tabela sanctuaries existe';
    ELSE
        RAISE WARNING '❌ Tabela sanctuaries NÃO encontrada';
    END IF;
    
    IF sanctuary_recipes_count = 1 THEN
        RAISE NOTICE '✅ Tabela sanctuary_recipes existe';
    ELSE
        RAISE WARNING '❌ Tabela sanctuary_recipes NÃO encontrada';
    END IF;
    
    IF has_sanctuary_column THEN
        RAISE NOTICE '✅ Coluna zone.is_sanctuary existe';
    ELSE
        RAISE WARNING '❌ Coluna zone.is_sanctuary NÃO encontrada';
    END IF;
    
    RAISE NOTICE '================================================';
    RAISE NOTICE 'Migration 003_rename_hideout_to_sanctuary CONCLUÍDA';
    RAISE NOTICE '================================================';
END $$;

-- =========================
-- ROLLBACK (Para reverter se necessário)
-- =========================
-- Para reverter esta migration, execute:
-- ALTER TABLE sanctuaries RENAME TO hideouts;
-- ALTER TABLE sanctuary_recipes RENAME TO hideout_recipes;
-- ... etc (inverter todas as operações)
