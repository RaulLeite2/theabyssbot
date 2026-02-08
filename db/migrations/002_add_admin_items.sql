-- ================================================
-- MIGRATION: Add Admin Items
-- ================================================
-- Este arquivo adiciona itens de admin ao banco
-- Executado automaticamente pelo migration_runner.py

-- Verificar se já existem itens de admin
DO $$
DECLARE
    admin_count INT;
BEGIN
    SELECT COUNT(*) INTO admin_count FROM items WHERE quality_new = 'ADMIN' AND depth_new = 99;
    
    IF admin_count > 0 THEN
        RAISE NOTICE 'Admin items já existem (% itens). Pulando migration.', admin_count;
    ELSE
        RAISE NOTICE 'Inserindo itens de admin...';
        
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
            'ADMIN'
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
            99,
            0,
            99,
            'ADMIN'
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
            99,
            0,
            99,
            'ADMIN'
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
            99,
            0,
            99,
            'ADMIN'
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
            99,
            0,
            99,
            'ADMIN'
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
            99,
            0,
            99,
            'ADMIN'
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
            99,
            0,
            99,
            'ADMIN'
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
            99,
            0,
            99,
            'ADMIN'
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
            99,
            0,
            99,
            'ADMIN'
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
            99,
            0,
            99,
            'ADMIN'
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
            99,
            0,
            99,
            'ADMIN'
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
            99,
            0,
            99,
            'ADMIN'
        );

        -- Contar itens inseridos
        SELECT COUNT(*) INTO admin_count FROM items WHERE quality_new = 'ADMIN' AND depth_new = 99;
        RAISE NOTICE '✓ % itens de admin inseridos com sucesso!', admin_count;
    END IF;
END $$;

-- Verificação final
SELECT 
    COUNT(*) as total_admin_items,
    MAX(basedamage) as max_damage,
    MAX(basedefense) as max_defense
FROM items
WHERE depth_new = 99 AND quality_new = 'ADMIN';
